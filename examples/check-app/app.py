from flask import Flask, jsonify
from models import *
from random import choice


STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)
app.config['TORTOISE_DATABASE_URI'] = 'sqlite://db.sqlite3'
app.config['TORTOISE_DATABASE_MODELS'] = "models"

models.init_app(app)

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

@app.get("/aniket")
async def aniket():
    pk=17
    user =await Users.get_or_404(pk=pk, description=f"user object not found at ID: {pk}")
    return jsonify(name=str(user))

@app.get("/sarkar")
async def sarkar():
    user = await Users.filter(pk=1).first_or_404()
    return jsonify(name=str(user))

@app.get("/paginate")
async def paginator():
    user = await Users.paginate()
    print (user)
    return "none"


if __name__ == '__main__':
    app.run(debug=True, port=8080)