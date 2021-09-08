# QuerySet

## Introduction
Tortoise-ORM provides a reach service of the query by using the class `tortoise.queryset.QuerySet`.
Here in this __Flask-Tortoise__ module I have inherited the default `tortoise.queryset.QuerySet` and added some extra query methods.

**To check all the inbuild available queries, please visit at:** [https://tortoise-orm.readthedocs.io/en/latest/query.html](https://tortoise-orm.readthedocs.io/en/latest/query.html)

## Custom Query

**To use the custom queries you have to change the `meta.manager` class for a `Model`.**

### How to add custom manager class with Model
```python
from flask_tortoise import Tortoise, fields
from flask_tortoise.models import Manager

db = Tortoise()

class Users(db.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(20, null=True)
    status = fields.CharField(20)

    class Meta:
        manager = Manager()
```
the above process will add a __custom manager__ with your model. And this **custom manager** will provide the extra query methods.


### Available custom methods

#### get_or_404
Fetch exactly one object matching the parameters or raise 404 not found error.     
###### Parameters  

__args:__ `Q functions containing constraints. Will be AND'ed.`   
__kwargs:__ `Simple filter constraints.`     
__description:__ `Error description.`    
 
###### Example:
```python
@app.get("/data")
async def get_data():
    pk=17
    user =await Users.get_or_404(pk=pk, description=f"user object not found at ID: {pk}")
    return jsonify(name=str(user))
```

#### first_or_404
Like **method** `first` but aborts with 404 if not found instead of returning ``None``.   
###### Parameters  
__args:__ `Q functions containing constraints. Will be AND'ed.`   
__kwargs:__ `Simple filter constraints.` 

##### Examples 
```python
@app.get("/data-1")
async def get_data_one():
    pk=17
    user =await Users.first_or_404(pk=pk, description=f"user object not found at ID: {pk}")
    return jsonify(name=str(user))
```