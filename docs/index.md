# Flask-Tortoise - Asynchronous database support for Flask

<p align="center">
  <a href="https://marktennyson.github.io/Flask-Tortoise"><img src="https://camo.githubusercontent.com/ac5549cf1ea281ad3422b09f0de31cffa09d95f817ff8f95d15865cf15ab8a48/68747470733a2f2f746f72746f6973652d6f726d2e72656164746865646f63732e696f2f656e2f6c61746573742f5f7374617469632f746f72746f6973652e706e67" alt="Flask-Tortoise"></a>
</p>
[![MIT licensed](https://img.shields.io/github/license/marktennyson/Flask-Tortoise)](https://raw.githubusercontent.com/marktennyson/Flask-Tortoise/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/marktennyson/Flask-Tortoise.svg)](https://github.com/marktennyson/Flask-Tortoise/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/marktennyson/Flask-Tortoise.svg)](https://github.com/marktennyson/Flask-Tortoise/network)
[![GitHub issues](https://img.shields.io/github/issues-raw/marktennyson/Flask-Tortoise)](https://github.com/marktennyson/Flask-Tortoise/issues)
[![Downloads](https://pepy.tech/badge/Flask-Tortoise)](https://pepy.tech/project/Flask-Tortoise)

_____________________________________________________________________

**Documentation:** <a href="https://navycut.github.io" target="_blank">https://navycut.github.io</a>  
**Github Repo:** <a href="https://github.com/navycut/navycut" target="_blank">https://github.com/navycut/navycut</a>

_______________________________________________________________________

## Introduction

Flask-Tortoise is an extension for Flask that adds support for asynchronous Tortoise-ORM to your application. It aims to simplify using Tortoise-ORM with Flask by providing useful defaults and extra helpers that make it easier to accomplish common tasks.

Tortoise-ORM is one of the best tool to interact with the database asynchronously. It's clean and Django type implementation provides you a better view and understanding of the database ORM system. Also you can use the Pydantic data module to write the error-less code.

The main aim of __Tortoise-ORM__ is to provide the same service and api like the __Django-ORM__.

<img src="https://tortoise-orm.readthedocs.io/en/latest/_images/ORM_Perf.png"></img>

## Installation

#### Install or update from `PYPI`
```bash
pip install -U Flask-Tortoise
```

#### Install from source code
```bash
$ git clone https://github.com/marktennyson/Flask-Tortoise
$ cd Flask-Tortoise && pip install .
```

## Features
- Fully asynchronous support.
- Clean, familiar python interface.
- Pluggable Database backends.
- Reach query system like Django.
- Composable, Django-inspired Models
- Proper implementation of different types of relation fields.
- Extra QuerySet added and pagination support.

`please check the official documentation of Tortoise-ORM for more details at: ` [https://tortoise-orm.readthedocs.io/en/latest/](https://tortoise-orm.readthedocs.io/en/latest/)


## Available configs

* __TORTOISE_ORM_DATABASE_URI:__           
ad the database url here.           
**Mandatory field**             
**Type:** `str`           

* __TORTOISE_ORM_MODELS:__            
add the name of the all model file.         
**Default value:** `app.import_name`        
**Type:** `str`        

* __TORTOISE_ORM_MODULES:__          
add the tortoise orm module dict here if you are about to initialize it by modules.        
**Default value:** `{}`           
**Type:** `dict`           

* __TORTOISE_ORM_CONFIG:__     
Initialize the tortoise Orm with the config dictionary.    
**Default value:** `{}`      
**Type:** `dict`      

* __TORTOISE_ORM_CONFIG_FILE:__
Initialize the tortoise orm from a config file.    
**Default value:** `None`   
**Type:** `optional-str`   

* __TORTOISE_ORM_GENERATE_SCHEMAS:__     
generate the schemas at the time of tortoise orm initialization.      
**Default value:** `False`         
**Type:** `bool` 

## A Basic demo for better understanding
```python
from flask import Flask, jsonify
from flask_tortoise import Tortoise, Model, fields
from random import choice


STATUSES = ["New", "Old", "Gone"]

app:"Flask" = Flask(__name__)
app.config['TORTOISE_ORM_DATABASE_URI'] = 'sqlite://db.sqlite3'

db:"Tortoise" = Tortoise(app)


class Users(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)

    def __str__(self):
        return f"User {self.id}: {self.status}"


class Workers(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)

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
__If you save your models into a separate file than you have mention the file name on app config:__

let's assume you have stores all of your models at `models.py` file.

**models.py file:**
```python
from flask_tortoise import Tortoise, Model, fields

db:"Tortoise" = Tortoise()


class Users(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)

    def __str__(self):
        return f"User {self.id}: {self.status}"


class Workers(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"
```

**app.py file:**
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