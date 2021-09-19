from tortoise.models import (
    Model as OldModel, 
    MetaInfo as OldMetaInfo, 
    )
from tortoise.manager import Manager as OldManager
from tortoise.query_utils import Q
from tortoise.manager import Manager

from .queryset import QuerySet

import typing as t

if t.TYPE_CHECKING:
    from tortoise.queryset import QuerySetSingle
    from .queryset import Pagination
    MODEL = t.TypeVar("MODEL", bound="Model")


class Manager(OldManager):
    def get_queryset(self) -> t.Type["QuerySet"]:
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
    def get_or_404(
        cls: t.Type["MODEL"], 
        *args: Q, 
        description: t.Optional[str]=None,
        **kwargs: t.Any
        ) -> "QuerySetSingle[MODEL]":
        """
        Fetches a single record for a Model type using the provided filter parameters or 404 error.

        for example::

            user:"User" = await User.get_or_404(username="foo", description="username not found.")

        :param args: Q functions containing constraints. Will be AND'ed.
        :param description: Error description for the `werkzeug's NotFound` error.
        :param kwargs: Simple filter constraints.
        """
        return cls._meta.manager.get_queryset().get_or_404(*args, description, **kwargs)

    @classmethod
    def first_or_404(
        cls: t.Type["MODEL"], 
        *args: Q, 
        description: t.Optional[str]=None,
        **kwargs: t.Any
        ) -> "QuerySetSingle[MODEL]":
        """
        Fetches the first record in the QuerySet or 404 error.

        for example::

            user:"User" = await User.first_or_404(username="foo", description="username not found.")

        :param args: Q functions containing constraints. Will be AND'ed.
        :param description: Error description for the `werkzeug's NotFound` error.
        :param kwargs: Simple filter constraints.
        """
        return cls._meta.manager.get_queryset().first_or_404(*args, description, **kwargs)

    @classmethod
    def paginate(
        cls: "MODEL", 
        page:t.Optional[int]=None, 
        per_page:t.Optional[int]=None, 
        error_out:bool=True, 
        max_per_page:t.Optional[int]=None, 
        count:bool=True
        ) -> "Pagination":

        return cls._meta.manager.get_queryset().paginate(
            page=page, 
            per_page=per_page, 
            error_out=error_out, 
            max_per_page=max_per_page, 
            count=count
            )