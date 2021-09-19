# Flask-Tortoise

<img src="https://tortoise-orm.readthedocs.io/en/latest/_static/tortoise.png" height="218px" width="388px"></img>
 
 Flask-Tortoise is an extension for Flask that adds support for asynchronous Tortoise-ORM to your application with in-built __migration__ system. It aims to simplify using Tortoise-ORM with Flask by providing useful defaults and extra helpers that make it easier to accomplish common tasks.

Tortoise-ORM is one of the best tool to interact with the database asynchronously. It's clean and Django type implementation provides you a better view and understanding of the database ORM system. Also you can use the Pydantic data module to write the error-less code.

The main aim of __Tortoise-ORM__ is to provide the same service and api like the __Django-ORM__.

### Installing
Install and update from PYPI:
```bash
pip install -U Flask-Tortoise
```
Install from source code:
```bash
git clone https://github.com/marktennyson/Flask-Tortoise
cd Flask-Tortoise && pip install .
```

### Important links
__Github Link:__ [https://github.com/marktennyson/Flask-Tortoise](https://github.com/marktennyson/Flask-Tortoise)    
__Official Documentation:__ [https://marktennyson.github.io/Flask-Tortoise](https://marktennyson.github.io/Flask-Tortoise/)

### Simple Examples for better understanding:
```python
from flask import Flask, jsonify
from flask_tortoise import Tortoise
from random import choice


STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)
app.config['TORTOISE_ORM_DATABASE_URI'] = 'sqlite://db.sqlite3'

db:"Tortoise" = Tortoise(app)


class Users(db.Model):
    id = db.IntField(pk=True)
    status = db.CharField(20)

    def __str__(self):
        return f"User {self.id}: {self.status}"


class Workers(db.Model):
    id = db.IntField(pk=True)
    status = db.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"

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
    app.run(debug=True, port=8080)
```

#### If you save your models into a separate file than you have mention the file name on app config:

let's assume you have stores all of your models at `models.py` file.
##### models.py file
```python
from flask_tortoise import Tortoise, Model, fields

db:"Tortoise" = Tortoise()


class Users(db.Model):
    id = db.IntField(pk=True)
    status = db.CharField(20)

    def __str__(self):
        return f"User {self.id}: {self.status}"


class Workers(db.Model):
    id = db.IntField(pk=True)
    status = db.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"
```

##### app.py file:
```python
from flask import Flask, jsonify
from models import *
from random import choice


STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)
app.config['TORTOISE_ORM_DATABASE_URI'] = 'sqlite://db.sqlite3'
app.config['TORTOISE_ORM_MODELS'] = "models" # if you have more than one models file then : ["models_1", "models_2", "models_3"]

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
    app.run(debug=True, port=8080)
```
### Contributing:
We welcome all types of contributions. If you face any issue while using this module then please let us know by creating a github issue on the official github repo. If you have the solution for the issue raised by you or somebody else then please fork this repo and create a pull request with the main branch.

##### How to run this project on local machine:
1. Fork this repo.
2. Clone this repo on your local machine.
3. create a virtual environment using python `virtualenv` module and activate it.
4. now run `python setup.py install`.
5. the above command will install the latest dev version of `Flask-Tortoise` on the virtual environment.

### Contributor List:
<a href="https://github.com/marktennyson/Flask-Tortoise/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=marktennyson/Flask-Tortoise" />
</a>

### License

GNU General Public License v3 or later (GPLv3+)

Copyright (c) 2021 Aniket Sarkar(aniketsarkar@yahoo.com)