from flask import Flask, jsonify
from register import register_tortoise
from models import *
import asyncio
from random import choice

STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)


# @app.get("/")
# def index():
#     return jsonify(message="index page")

@app.get("/")
async def list_all():
    users, workers = await asyncio.gather(Users.all(), Workers.all())
    return jsonify(
        {"users": [str(user) for user in users], "workers": [str(worker) for worker in workers]}
    )


@app.get("/user")
async def add_user():
    user = await Users.create(status=choice(STATUSES))  # nosec
    return str(user)


@app.get("/worker")
async def add_worker():
    worker = await Workers.create(status=choice(STATUSES))  # nosec
    return str(worker)


register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={"models": ["models"]},
    generate_schemas=False,
)



if __name__ == '__main__':
    app.run(debug=True, port=8000)