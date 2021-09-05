from tortoise.models import (
    Model as OldModel, 
    MetaInfo as OldMetaInfo, 
    ModelMeta as OldModelMeta,
    _get_comments
    )
import typing as t
from typing import *
from tortoise.manager import Manager as OldManager
from tortoise.query_utils import Q
from tortoise.queryset import QuerySetSingle, QuerySet as OldQuerySet

from tortoise.filters import get_filters_for_field
from tortoise.manager import Manager
from tortoise.fields.base import Field
from tortoise.fields.data import IntField
from tortoise.fields.relational import (
    ForeignKeyFieldInstance,
    ManyToManyFieldInstance,
    OneToOneFieldInstance,
)
from tortoise.exceptions import (
    ConfigurationError,
)
import inspect
from copy import deepcopy

# from .queryset import QuerySet
MODEL = t.TypeVar("MODEL", bound="Model")


class QuerySet(OldQuerySet):
    def get_or_404(self, *args: Q, **kwargs: t.Any) -> QuerySetSingle[t.Optional[MODEL]]:
        """
        Fetch exactly one object matching the parameters.
        """
        queryset = self.filter(*args, **kwargs)
        queryset._limit = 2
        queryset._single = True
        return queryset
        

class Manager(OldManager):
    def get_queryset(self) -> QuerySet:
        return QuerySet(self._model)

    def __str__(self) -> str:
        return "flask-tortoise-manager"


class MetaInfo(OldMetaInfo):
    def __init__(self, meta:"Model.Meta"):
        super(MetaInfo, self).__init__(meta)
        self.manager = Manager()


class ModelMeta(OldModelMeta):
    __slots__ = ()

    def __new__(mcs, name: str, bases: t.Tuple[Type, ...], attrs: dict):
        fields_db_projection: Dict[str, str] = {}
        fields_map: Dict[str, Field] = {}
        filters: Dict[str, Dict[str, dict]] = {}
        fk_fields: Set[str] = set()
        m2m_fields: Set[str] = set()
        o2o_fields: Set[str] = set()
        meta_class: "Model.Meta" = attrs.get("Meta", type("Meta", (), {}))
        pk_attr: str = "id"

        # Searching for Field attributes in the class hierarchy
        def __search_for_field_attributes(base: Type, attrs: dict) -> None:
            """
            Searching for class attributes of type fields.Field
            in the given class.

            If an attribute of the class is an instance of fields.Field,
            then it will be added to the fields dict. But only, if the
            key is not already in the dict. So derived classes have a higher
            precedence. Multiple Inheritance is supported from left to right.

            After checking the given class, the function will look into
            the classes according to the MRO (method resolution order).

            The MRO is 'natural' order, in which python traverses methods and
            fields. For more information on the magic behind check out:
            `The Python 2.3 Method Resolution Order
            <https://www.python.org/download/releases/2.3/mro/>`_.
            """
            for parent in base.__mro__[1:]:
                __search_for_field_attributes(parent, attrs)
            meta = getattr(base, "_meta", None)
            if meta:
                # For abstract classes
                for key, value in meta.fields_map.items():
                    attrs[key] = value
                # For abstract classes manager
                for key, value in base.__dict__.items():
                    if isinstance(value, Manager) and key not in attrs:
                        attrs[key] = value.__class__()
            else:
                # For mixin classes
                for key, value in base.__dict__.items():
                    if isinstance(value, Field) and key not in attrs:
                        attrs[key] = value

        # Start searching for fields in the base classes.
        inherited_attrs: dict = {}
        for base in bases:
            __search_for_field_attributes(base, inherited_attrs)
        if inherited_attrs:
            # Ensure that the inherited fields are before the defined ones.
            attrs = {**inherited_attrs, **attrs}

        if name != "Model":
            custom_pk_present = False
            for key, value in attrs.items():
                if isinstance(value, Field):
                    if value.pk:
                        if custom_pk_present:
                            raise ConfigurationError(
                                f"Can't create model {name} with two primary keys,"
                                " only single primary key is supported"
                            )
                        if value.generated and not value.allows_generated:
                            raise ConfigurationError(
                                f"Field '{key}' ({value.__class__.__name__}) can't be DB-generated"
                            )
                        custom_pk_present = True
                        pk_attr = key

            if not custom_pk_present and not getattr(meta_class, "abstract", None):
                if "id" not in attrs:
                    attrs = {"id": IntField(pk=True), **attrs}

                if not isinstance(attrs["id"], Field) or not attrs["id"].pk:
                    raise ConfigurationError(
                        f"Can't create model {name} without explicit primary key if field 'id'"
                        " already present"
                    )

            for key, value in attrs.items():
                if isinstance(value, Field):
                    if getattr(meta_class, "abstract", None):
                        value = deepcopy(value)

                    fields_map[key] = value
                    value.model_field_name = key

                    if isinstance(value, OneToOneFieldInstance):
                        o2o_fields.add(key)
                    elif isinstance(value, ForeignKeyFieldInstance):
                        fk_fields.add(key)
                    elif isinstance(value, ManyToManyFieldInstance):
                        m2m_fields.add(key)
                    else:
                        fields_db_projection[key] = value.source_field or key
                        filters.update(
                            get_filters_for_field(
                                field_name=key,
                                field=fields_map[key],
                                source_field=fields_db_projection[key],
                            )
                        )
                        if value.pk:
                            filters.update(
                                get_filters_for_field(
                                    field_name="pk",
                                    field=fields_map[key],
                                    source_field=fields_db_projection[key],
                                )
                            )

        # Clean the class attributes
        for slot in fields_map:
            attrs.pop(slot, None)
        attrs["_meta"] = meta = MetaInfo(meta_class)

        meta.fields_map = fields_map
        meta.fields_db_projection = fields_db_projection
        meta._filters = filters
        meta.fk_fields = fk_fields
        meta.backward_fk_fields = set()
        meta.o2o_fields = o2o_fields
        meta.backward_o2o_fields = set()
        meta.m2m_fields = m2m_fields
        meta.default_connection = None
        meta.pk_attr = pk_attr
        meta.pk = fields_map.get(pk_attr) 
        if meta.pk:
            meta.db_pk_column = meta.pk.source_field or meta.pk_attr
        meta._inited = False
        if not fields_map:
            meta.abstract = True

        new_class = super().__new__(mcs, name, bases, attrs)
        for field in meta.fields_map.values():
            field.model = new_class  

        for fname, comment in _get_comments(new_class).items():  
            if fname in fields_map:
                fields_map[fname].docstring = comment
                if fields_map[fname].description is None:
                    fields_map[fname].description = comment.split("\n")[0]

        if new_class.__doc__ and not meta.table_description:
            meta.table_description = inspect.cleandoc(new_class.__doc__).split("\n")[0]
        for key, value in attrs.items():
            if isinstance(value, Manager):
                value._model = new_class
        meta._model = new_class  # type: ignore
        meta.manager._model = new_class
        meta.finalise_fields()
        return new_class

    def __getitem__(cls: Type[MODEL], key: Any) -> QuerySetSingle[MODEL]:  # type: ignore
        return cls._getbypk(key)  # type: ignore



class Model(OldModel, metaclass=ModelMeta):
    """
    the base Model class inherited from `tortoise.models.Model`
    """
    _meta = MetaInfo(None)

    @classmethod
    def get_or_404(cls: t.Type[MODEL], *args: Q, **kwargs: t.Any) -> QuerySetSingle[t.Optional[MODEL]]:
        """
        Fetches a single record for a Model type using the provided filter parameters or None.

        .. code-block:: python3

            user = await User.get_or_404(username="foo")

        :param args: Q functions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        self = cls.__new__(cls)
        # cls.attr
        # print (self.meta)
        # return " "
        return cls._meta.manager.get_queryset().get_or_404(*args, **kwargs)