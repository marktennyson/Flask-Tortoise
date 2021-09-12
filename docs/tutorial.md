# Tutorial

## Introduction

The basic introdunction provides you a basic understanding of the `Flask-Tortoise` module.
Primary entity of tortoise is flask_tortoise.models.Model. You can start writing models like this:
```python
from flask_tortoise.models import Tortoise, fields

db:"Tortoise" = Tortoise()

class Tournament(db.Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return self.name


class Event(db.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    # References to other models are defined in format
    # "{app_name}.{model_name}" - where {app_name} is defined in tortoise config
    tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
    participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')

    def __str__(self):
        return self.name


class Team(db.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    def __str__(self):
        return self.name
```
After you defined all your models, tortoise needs you to init them, in order to create backward relations between models and match your db client with appropriate models.

You can do it like this:
```python
from .models import *
from flask import Flask

app = Flask(__name__)

db.init_app(app)

if __name__ == '__main__':
    app.run()
```
Here **init_app** method will connect the `flask application` with the __Tortoise ORM__. Tortoise is the asynchronous based database. So the database connection must to close on every request end.
So this module will initialize the __Tortoise ORM__ before on every request and close it after the reqyest end.

After that you can start using your models:

```python
# Create instance by save
tournament = Tournament(name='New Tournament')
await tournament.save()

# Or by .create()
await Event.create(name='Without participants', tournament=tournament)
event = await Event.create(name='Test', tournament=tournament)
participants = []
for i in range(2):
    team = await Team.create(name='Team {}'.format(i + 1))
    participants.append(team)

# M2M Relationship management is quite straightforward
# (look for methods .remove(...) and .clear())
await event.participants.add(*participants)

# You can query related entity just with async for
async for team in event.participants:
    pass

# After making related query you can iterate with regular for,
# which can be extremely convenient for using with other packages,
# for example some kind of serializers with nested support
for team in event.participants:
    pass


# Or you can make preemptive call to fetch related objects,
# so you can work with related objects immediately
selected_events = await Event.filter(
    participants=participants[0].id
).prefetch_related('participants', 'tournament')
for event in selected_events:
    print(event.tournament.name)
    print([t.name for t in event.participants])

# Tortoise ORM supports variable depth of prefetching related entities
# This will fetch all events for team and in those team tournament will be prefetched
await Team.all().prefetch_related('events__tournament')

# You can filter and order by related models too
await Tournament.filter(
    events__name__in=['Test', 'Prod']
).order_by('-events__participants__name').distinct()
```

:bulb: **Note:** For more please visit the official documentation of __Tortoise ORM__ at: [https://tortoise-orm.readthedocs.io/en/latest/getting_started.html#tutorial](https://tortoise-orm.readthedocs.io/en/latest/getting_started.html#tutorial)