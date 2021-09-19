from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from tortoise.queryset import QuerySetSingle, QuerySet as OldQuerySet

from copy import copy
from math import ceil
from flask.globals import request
from werkzeug.exceptions import NotFound

import typing as t

if t.TYPE_CHECKING: # use this to omit the circular import issue.
    from .models import MODEL
    from tortoise.query_utils import Q

class Pagination:
    """Internal helper class returned by :meth:`QuerySet.paginate`.  You
    can also construct it from any other TortoiseORM query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(
        self, 
        queryset:"QuerySet", 
        page:int, 
        per_page:int, 
        total:int, 
        items:"QuerySet[MODEL]"):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.queryset = queryset
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    async def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert (
            self.queryset is not None
        ), "a query object is required for this method to work"
        return self.queryset.paginate(self.page - 1, self.per_page, error_out)

    @property
    async def prev_num(self):
        """Number of the previous page."""
        if not await self.has_prev:
            return None
        return self.page - 1

    @property
    async def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    async def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert (
            self.queryset is not None
        ), "a query object is required for this method to work"
        return self.queryset.paginate(self.page + 1, self.per_page, error_out)

    @property
    async def has_next(self):
        """True if a next page exists."""
        return self.page < await self.pages

    @property
    async def next_num(self):
        """Number of the next page"""
        if not await self.has_next:
            return None
        return self.page + 1

    async def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:
        .. sourcecode:: html+jinja
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > await self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def __await__(self: "Pagination") -> t.Generator[t.Any, None, "Pagination"]:
        async def _self() -> "Pagination":
            return self

        return _self().__await__()

class QuerySet(OldQuerySet):
    _raise_404_not_found:bool = False
    _not_found_err_description:t.Optional[str] = None
    
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
                    raise NotFound(description=self._not_found_err_description)
                return None

            else:
                raise MultipleObjectsReturned("Multiple objects returned, expected exactly one")
        return instance_list

    def get_or_404(
        self, 
        *args: "Q", 
        description:t.Optional[str]=None, 
        **kwargs: t.Any
        ) -> QuerySetSingle["MODEL"]:
        """
        Fetch exactly one object matching 
        the parameters or raise 404 not found.
        """
        err_description = description
        queryset:"QuerySet" = self.filter(*args, **kwargs)
        queryset._limit = 2
        queryset._single = True
        queryset._raise_404_not_found = True
        queryset._not_found_err_description = err_description
        return queryset

    def first_or_404(
        self, 
        *args: "Q", 
        description:t.Optional[str]=None, 
        **kwargs:t.Any
        ) -> QuerySetSingle["MODEL"]:
        """
        Like :meth:`first` but aborts with 404 if not found instead
        of returning ``None``.
        """
        return self.get_or_404(*args, description, **kwargs)

    def paginate(
        self, 
        page:t.Optional[int]=None, 
        per_page:t.Optional[int]=None, 
        error_out:bool=True, 
        max_per_page:t.Optional[int]=None, 
        count:bool=True
    ) -> t.Type["Pagination"]:
        """Returns ``per_page`` items from page ``page``.
        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively. If ``count`` is ``False``,
        no query to help determine total page count will be run.
        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:
        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.
        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.
        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    page = int(request.args.get("page", 1))
                except (TypeError, ValueError):
                    if error_out:
                        raise NotFound

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get("per_page", 20))
                except (TypeError, ValueError):
                    if error_out:
                        raise NotFound

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                raise NotFound
            else:
                page = 1

        if per_page < 0:
            if error_out:
                raise NotFound
            else:
                per_page = 20

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            raise NotFound

        if not count:
            total = None
        else:
            total = self.all().count()

        return Pagination(self, page, per_page, total, items)