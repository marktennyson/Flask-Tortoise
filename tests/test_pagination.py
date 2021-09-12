import pytest
from werkzeug.exceptions import NotFound

from flask_tortoise import Pagination

# import typing as t

# if t.TYPE_CHECKING:
#     from 


@pytest.mark.asyncio
async def test_basic_pagination():
    p = await Pagination(None, 1, 20, 500, [])
    assert p.page == 1
    assert not await p.has_prev
    assert await p.has_next
    assert  p.total == 500
    assert await p.pages == 25
    assert await p.next_num == 2
    # assert list(await p.iter_pages()) == [1, 2, 3, 4, 5, None, 24, 25]
    p.page = 10
    # assert list(await p.iter_pages()) == [1, 2, None, 8, 9, 10, 11, 12, 13, 14, None, 24, 25]


@pytest.mark.asyncio
async def test_pagination_pages_when_0_items_per_page():
    p = await Pagination(None, 1, 0, 500, [])
    assert await p.pages == 0

@pytest.mark.asyncio
async def test_pagination_pages_when_total_is_none():
    p = await Pagination(None, 1, 100, None, [])
    assert await p.pages == 0

# @pytest.mark.asyncio
# async def test_query_paginate(app, db, Todo):
#     with app.app_context():
#         for _ in range(100):
#             await Todo(title="", text="")
        

#     @app.route("/")
#     async def index():
#         p = await Todo.paginate()
#         return f"{len(await p.items)} items retrieved"

#     c = app.test_client()
#     # request default
#     r = c.get("/")
#     assert r.status_code == 200
#     # request args
#     r = c.get("/?per_page=10")
#     assert r.data.decode("utf8") == "10 items retrieved"

#     with app.app_context():
#         # query default
#         p = await Todo.paginate()
#         assert p.total == 100


# @pytest.mark.asyncio
# def test_query_paginate_more_than_20(app, db, Todo):
#     with app.app_context():
#         db.session.add_all(Todo("", "") for _ in range(20))
#         db.session.commit()

#     assert len(Todo.query.paginate(max_per_page=10).items) == 10


# def test_paginate_min(app, db, Todo):
#     with app.app_context():
#         db.session.add_all(Todo(str(x), "") for x in range(20))
#         db.session.commit()

#     assert Todo.query.paginate(error_out=False, page=-1).items[0].title == "0"
#     assert len(Todo.query.paginate(error_out=False, per_page=0).items) == 0
#     assert len(Todo.query.paginate(error_out=False, per_page=-1).items) == 20

#     with pytest.raises(NotFound):
#         Todo.query.paginate(page=0)

#     with pytest.raises(NotFound):
#         Todo.query.paginate(per_page=-1)


# def test_paginate_without_count(app, db, Todo):
#     with app.app_context():
#         db.session.add_all(Todo("", "") for _ in range(20))
#         db.session.commit()

#     assert len(Todo.query.paginate(count=False, page=1, per_page=10).items) == 10