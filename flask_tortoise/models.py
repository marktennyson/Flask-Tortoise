from tortoise.models import (
    Model as OldModel, 
    MetaInfo as OldMetaInfo, 
    )
from tortoise.manager import Manager as OldManager
from tortoise.query_utils import Q
from tortoise.queryset import QuerySetSingle, QuerySet as OldQuerySet
from tortoise.manager import Manager
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from copy import copy
from werkzeug.exceptions import NotFound

import typing as t

if t.TYPE_CHECKING:
    MODEL = t.TypeVar("MODEL", bound="Model")


class QuerySet(OldQuerySet):
    _raise_404_not_found:bool = False

    def _clone(self) -> "QuerySet[MODEL]":
        queryset = self.__class__.__new__(QuerySet)
        queryset.fields = self.fields
        queryset.model = self.model
        queryset.query = self.query
        queryset.capabilities = self.capabilities
        queryset._prefetch_map = copy(self._prefetch_map)
        queryset._prefetch_queries = copy(self._prefetch_queries)
        queryset._single = self._single
        queryset._raise_does_not_exist = self._raise_does_not_exist
        queryset._raise_404_not_found = self._raise_404_not_found
        queryset._db = self._db
        queryset._limit = self._limit
        queryset._offset = self._offset
        queryset._fields_for_select = self._fields_for_select
        queryset._filter_kwargs = copy(self._filter_kwargs)
        queryset._orderings = copy(self._orderings)
        queryset._joined_tables = copy(self._joined_tables)
        queryset._q_objects = copy(self._q_objects)
        queryset._distinct = self._distinct
        queryset._annotations = copy(self._annotations)
        queryset._having = copy(self._having)
        queryset._custom_filters = copy(self._custom_filters)
        queryset._group_bys = copy(self._group_bys)
        queryset._select_for_update = self._select_for_update
        queryset._select_for_update_nowait = self._select_for_update_nowait
        queryset._select_for_update_skip_locked = self._select_for_update_skip_locked
        queryset._select_for_update_of = self._select_for_update_of
        queryset._select_related = self._select_related
        queryset._select_related_idx = self._select_related_idx
        queryset._force_indexes = self._force_indexes
        queryset._use_indexes = self._use_indexes
        return queryset

    async def _execute(self) -> t.List["MODEL"]:
        instance_list = await self._db.executor_class(
            model=self.model,
            db=self._db,
            prefetch_map=self._prefetch_map,
            prefetch_queries=self._prefetch_queries,
            select_related_idx=self._select_related_idx,
        ).execute_select(self.query, custom_fields=list(self._annotations.keys()))
        if self._single:
            if len(instance_list) == 1:
                return instance_list[0]
            if not instance_list:
                if self._raise_does_not_exist:
                    raise DoesNotExist("Object does not exist")
                elif self._raise_404_not_found is True:
                    raise NotFound
                return None
            raise MultipleObjectsReturned("Multiple objects returned, expected exactly one")
        return instance_list

    def get_or_404(self, *args: Q, **kwargs: t.Any) -> QuerySetSingle[t.Optional["MODEL"]]:
        """
        Fetch exactly one object matching 
        the parameters or raise 404 not found.
        """
        queryset = self.filter(*args, **kwargs)
        queryset._limit = 2
        queryset._single = True
        queryset._raise_404_not_found = True
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
    _meta = MetaInfo(None)  # required for type checking      

    @classmethod
    def get_or_404(cls: t.Type["MODEL"], *args: Q, **kwargs: t.Any) -> QuerySetSingle[t.Optional["MODEL"]]:
        """
        Fetches a single record for a Model type using the provided filter parameters or 404 error.

        .. code-block:: python3

            user = await User.get_or_404(username="foo")

        :param args: Q functions containing constraints. Will be AND'ed.
        :param kwargs: Simple filter constraints.
        """
        return cls._meta.manager.get_queryset().get_or_404(*args, **kwargs)