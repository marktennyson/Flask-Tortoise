from datetime import datetime

import flask
import pytest

from flask_tortoise import Tortoise, fields


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app.config["TORTOISE_DATABASE_URI"] = "sqlite://:memory:"
    app.config["TORTOISE_DATABASE_MODELS"] = "__main__"
    return app


@pytest.fixture
def db(app):
    return Tortoise(app)


@pytest.fixture
def Todo(db:"Tortoise"):
    class Todo(db.Model):
        
        id = fields.IntField(pk=True)
        title = fields.CharField(max_length=60)
        text = fields.CharField(max_length=60)
        done = fields.BooleanField(default=False)
        pub_date = fields.DatetimeField(null=True)

        class Meta:
            tablename = "todos"

    db.generate_schemas()
    yield Todo
    db.remove_schemas()