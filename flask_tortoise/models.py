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
        Fetch exactly one object matching 
        the parameters or raise 404 not found.
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


class Model(OldModel):
    """
    the base Model class inherited from `tortoise.models.Model`
    """
    _meta = MetaInfo(None)

    @classmethod
    def _init_from_db(cls: Type[MODEL], **kwargs: Any) -> MODEL:
        self = cls.__new__(cls)
        self._partial = False
        self._saved_in_db = True

        meta = self._meta

        try:
            # This is like so for performance reasons.
            #  We want to avoid conditionals and calling .to_python_value()
            # Native fields are fields that are already converted to/from python to DB type
            #  by the DB driver
            for key, model_field, field in meta.db_native_fields:
                setattr(self, model_field, kwargs[key])
            # Fields that don't override .to_python_value() are converted without a call
            #  as we already know what we will be doing.
            for key, model_field, field in meta.db_default_fields:
                value = kwargs[key]
                setattr(
                    self,
                    model_field,
                    None if value is None else field.field_type(value),
                )
            # These fields need manual .to_python_value()
            for key, model_field, field in meta.db_complex_fields:
                setattr(self, model_field, field.to_python_value(kwargs[key]))
        except KeyError:
            self._partial = True
            # TODO: Apply similar perf optimisation as above for partial
            for key, value in kwargs.items():
                setattr(self, key, meta.fields_map[key].to_python_value(value))

        return self

    @classmethod
    def get_or_404(cls: t.Type[MODEL], *args: Q, **kwargs: t.Any) -> QuerySetSingle[t.Optional[MODEL]]:
        """
        Fetches a single record for a Model type using the provided filter parameters or None.

        .. code-block:: python3

            user = await User.get_or_404(username="foo")

        :param args: Q functions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls._meta.manager.get_queryset().get_or_404(*args, **kwargs)