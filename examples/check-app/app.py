from flask import Flask, jsonify
from models import *
from random import choice
from models import db
from inspect import getfile



STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)
app.config['TORTOISE_DATABASE_URI'] = 'sqlite://db.sqlite3'
app.config['TORTOISE_DATABASE_MODELS'] = {"models": [app.import_name]}
print (getfile(app.__class__))
print (__name__)


db.init_app(app)


@app.get("/")
async def list_all():
    users = await Users.all()
    workers = await Workers.all()
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

@app.get("/get-worker")
async def get_worker():
    worker:"Workers" = await Workers.get(id=1)
    return str(worker.status)

if __name__ == '__main__':
    app.run(debug=True, port=8000)