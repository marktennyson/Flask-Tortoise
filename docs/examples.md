# Simple Examples

## Basic

```python
"""
This example demonstrates most basic operations with single model
"""
from flask import Flask
from flask_tortoise import Tortoise

app = Flask(__name__)
db = Tortoise(app)

class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    datetime = db.DatetimeField(null=True)

    class Meta:
        table = "event"

    def __str__(self):
        return self.name


@app.get("/event")
async def event():
    event = await Event.create(name="Test")
    await Event.filter(id=event.id).update(name="Updated name")

    print(await Event.filter(name="Updated name").first())
    # >>> Updated name

    await Event(name="Test 2").save()
    print(await Event.all().values_list("id", flat=True))
    # >>> [1, 2]
    print(await Event.all().values("id", "name"))
    # >>> [{'id': 1, 'name': 'Updated name'}, {'id': 2, 'name': 'Test 2'}]
    return "null"


if __name__ == "__main__":
    app.run()
```

## Comments

```python
"""
This example demonstrates most basic operations with single model
and a Table definition generation with comment support
"""

class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField(description="Name of the event that corresponds to an action")
    datetime = db.DatetimeField(
        null=True, description="Datetime of when the event was generated"
    )

    class Meta:
        table = "event"
        table_description = "This table contains a list of all the example events"

    def __str__(self):
        return self.name


@app.route("/events")
async def events():
    event = await Event.create(name="Test")
    await Event.filter(id=event.id).update(name="Updated name")

    print(await Event.filter(name="Updated name").first())

    await Event(name="Test 2").save()
    print(await Event.all().values_list("id", flat=True))
    print(await Event.all().values("id", "name"))
    return 'null'


if __name__ == "__main__":
    app.run()
```

## Prefetching

```python
from tortoise.query_utils import Prefetch


class Tournament(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    tournament: db.ForeignKeyRelation[Tournament] = db.ForeignKeyField(
        "db.Tournament", related_name="events"
    )
    participants: db.ManyToManyRelation["Team"] = db.ManyToManyField(
        "db.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Team(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ManyToManyRelation[Event]

    def __str__(self):
        return self.name


@app.route("/events")
async def events():
    tournament = await Tournament.create(name="tournament")
    await Event.create(name="First", tournament=tournament)
    await Event.create(name="Second", tournament=tournament)
    tournament_with_filtered = (
        await Tournament.all()
        .prefetch_related(Prefetch("events", queryset=Event.filter(name="First")))
        .first()
    )
    print(tournament_with_filtered)
    print(await Tournament.first().prefetch_related("events"))

    tournament_with_filtered_to_attr = (
        await Tournament.all()
        .prefetch_related(
            Prefetch("events", queryset=Event.filter(name="First"), to_attr="to_attr_events_first"),
            Prefetch(
                "events", queryset=Event.filter(name="Second"), to_attr="to_attr_events_second"
            ),
        )
        .first()
    )
    print(tournament_with_filtered_to_attr.to_attr_events_first)
    print(tournament_with_filtered_to_attr.to_attr_events_second)
    return 'null'


if __name__ == "__main__":
    app.run()
```

## Transactions

```python
"""
This example demonstrates how you can use transactions with tortoise
"""
from tortoise.exceptions import OperationalError
from tortoise.transactions import atomic, in_transaction


class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    class Meta:
        table = "event"

    def __str__(self):
        return self.name


@app.route("/run")
async def run():
    try:
        async with in_transaction() as connection:
            event = Event(name="Test")
            await event.save(using_db=connection)
            await Event.filter(id=event.id).using_db(connection).update(name="Updated name")
            saved_event = await Event.filter(name="Updated name").using_db(connection).first()
            await connection.execute_query("SELECT * FROM non_existent_table")
    except OperationalError:
        pass
    saved_event = await Event.filter(name="Updated name").first()
    print(saved_event)

    @atomic()
    async def bound_to_fall():
        event = await Event.create(name="Test")
        await Event.filter(id=event.id).update(name="Updated name")
        saved_event = await Event.filter(name="Updated name").first()
        print(saved_event.name)
        raise OperationalError()

    try:
        await bound_to_fall()
    except OperationalError:
        pass
    saved_event = await Event.filter(name="Updated name").first()
    print(saved_event)
    return 'null'


if __name__ == "__main__":
    app.run()
```

## Functions

```python
from tortoise.functions import Coalesce, Count, Length, Lower, Min, Sum, Trim, Upper
from tortoise.query_utils import Q


class Tournament(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    desc = db.TextField(null=True)

    events: db.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    tournament: db.ForeignKeyRelation[Tournament] = db.ForeignKeyField(
        "models.Tournament", related_name="events"
    )
    participants: db.ManyToManyRelation["Team"] = db.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Team(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ManyToManyRelation[Event]

    def __str__(self):
        return self.name


@app.route("/runs")
async def run():
    tournament = await Tournament.create(name="New Tournament", desc="great")
    await tournament.save()
    await Tournament.create(name="Second tournament")
    await Tournament.create(name=" final tournament ")
    await Event(name="Without participants", tournament_id=tournament.id).save()
    event = Event(name="Test", tournament_id=tournament.id)
    await event.save()
    participants = []
    for i in range(2):
        team = Team(name=f"Team {(i + 1)}")
        await team.save()
        participants.append(team)
    await event.participants.add(participants[0], participants[1])
    await event.participants.add(participants[0], participants[1])

    print(await Tournament.all().annotate(events_count=Count("events")).filter(events_count__gte=1))
    print(
        await Tournament.all()
        .annotate(events_count_with_filter=Count("events", _filter=Q(name="New Tournament")))
        .filter(events_count_with_filter__gte=1)
    )

    print(await Event.filter(id=event.id).first().annotate(lowest_team_id=Min("participants__id")))

    print(await Tournament.all().annotate(events_count=Count("events")).order_by("events_count"))

    print(await Event.all().annotate(tournament_test_id=Sum("tournament__id")).first())

    print(
        await Tournament.annotate(clean_desciption=Coalesce("desc", "")).filter(clean_desciption="")
    )

    print(
        await Tournament.annotate(trimmed_name=Trim("name")).filter(trimmed_name="final tournament")
    )

    print(
        await Tournament.annotate(name_len=Length("name")).filter(
            name_len__gt=len("New Tournament")
        )
    )

    print(await Tournament.annotate(name_lo=Lower("name")).filter(name_lo="new tournament"))
    print(await Tournament.annotate(name_lo=Upper("name")).filter(name_lo="NEW TOURNAMENT"))
    return 'null'

if __name__ == "__main__":
    app.run()
```

## Group By

```python
from tortoise.functions import Avg, Count, Sum


class Author(db.Model):
    name = db.CharField(max_length=255)


class Book(db.Model):
    name = db.CharField(max_length=255)
    author = db.ForeignKeyField("models.Author", related_name="books")
    rating = db.FloatField()


@app.route("/runs")
async def run():
    a1 = await Author.create(name="author1")
    a2 = await Author.create(name="author2")
    for i in range(10):
        await Book.create(name=f"book{i}", author=a1, rating=i)
    for i in range(5):
        await Book.create(name=f"book{i}", author=a2, rating=i)

    ret = await Book.annotate(count=Count("id")).group_by("author_id").values("author_id", "count")
    print(ret)
    # >>> [{'author_id': 1, 'count': 10}, {'author_id': 2, 'count': 5}]

    ret = (
        await Book.annotate(count=Count("id"))
        .filter(count__gt=6)
        .group_by("author_id")
        .values("author_id", "count")
    )
    print(ret)
    # >>> [{'author_id': 1, 'count': 10}]

    ret = await Book.annotate(sum=Sum("rating")).group_by("author_id").values("author_id", "sum")
    print(ret)
    # >>> [{'author_id': 1, 'sum': 45.0}, {'author_id': 2, 'sum': 10.0}]

    ret = (
        await Book.annotate(sum=Sum("rating"))
        .filter(sum__gt=11)
        .group_by("author_id")
        .values("author_id", "sum")
    )
    print(ret)
    # >>> [{'author_id': 1, 'sum': 45.0}]

    ret = await Book.annotate(avg=Avg("rating")).group_by("author_id").values("author_id", "avg")
    print(ret)
    # >>> [{'author_id': 1, 'avg': 4.5}, {'author_id': 2, 'avg': 2.0}]

    ret = (
        await Book.annotate(avg=Avg("rating"))
        .filter(avg__gt=3)
        .group_by("author_id")
        .values("author_id", "avg")
    )
    print(ret)
    # >>> [{'author_id': 1, 'avg': 4.5}]

    # and use .values_list()
    ret = (
        await Book.annotate(count=Count("id"))
        .group_by("author_id")
        .values_list("author_id", "count")
    )
    print(ret)
    # >>> [(1, 10), (2, 5)]

    # group by with join
    ret = (
        await Book.annotate(count=Count("id"))
        .group_by("author__name")
        .values("author__name", "count")
    )
    print(ret)
    # >>> [{"author__name": "author1", "count": 10}, {"author__name": "author2", "count": 5}]
    return 'null'

if __name__ == "__main__":
    app.run()
```

## Filtering

```python
"""
This example shows some more complex querying

Key points are filtering by related names and using Q objects
"""
from tortoise.query_utils import Q


class Tournament(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    tournament: db.ForeignKeyRelation[Tournament] = db.ForeignKeyField(
        "models.Tournament", related_name="events"
    )
    participants: db.ManyToManyRelation["Team"] = db.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Team(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ManyToManyRelation[Event]

    def __str__(self):
        return self.name


@app.route("/aniket")
async def run():
    tournament = Tournament(name="Tournament")
    await tournament.save()

    second_tournament = Tournament(name="Tournament 2")
    await second_tournament.save()

    event_first = Event(name="1", tournament=tournament)
    await event_first.save()
    event_second = await Event.create(name="2", tournament=second_tournament)
    await Event.create(name="3", tournament=tournament)
    await Event.create(name="4", tournament=second_tournament)

    await Event.filter(tournament=tournament)

    team_first = Team(name="First")
    await team_first.save()
    team_second = Team(name="Second")
    await team_second.save()

    await team_first.events.add(event_first)
    await event_second.participants.add(team_second)

    print(
        await Event.filter(Q(id__in=[event_first.id, event_second.id]) | Q(name="3"))
        .filter(participants__not=team_second.id)
        .order_by("tournament__id")
        .distinct()
    )

    print(await Team.filter(events__tournament_id=tournament.id).order_by("-events__name"))
    print(
        await Tournament.filter(events__name__in=["1", "3"])
        .order_by("-events__participants__name")
        .distinct()
    )

    print(await Team.filter(name__icontains="CON"))

    print(await Tournament.filter(events__participants__name__startswith="Fir"))
    print(await Tournament.filter(id__icontains=1).count())
    return 'null'

if __name__ == "__main__":
    app.run()
```

## Relations
```python
"""
This example shows how relations between models work.

Key points in this example are use of ForeignKeyField and ManyToManyField
to declare relations and use of .prefetch_related() and .fetch_related()
to get this related objects
"""
from tortoise.exceptions import NoValuesFetched


class Tournament(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ReverseRelation["Event"]

    def __str__(self):
        return self.name


class Event(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    tournament: db.ForeignKeyRelation[Tournament] = db.ForeignKeyField(
        "models.Tournament", related_name="events"
    )
    participants: db.ManyToManyRelation["Team"] = db.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Address(db.Model):
    city = db.CharField(max_length=64)
    street = db.CharField(max_length=128)

    event: db.OneToOneRelation[Event] = db.OneToOneField(
        "models.Event", on_delete=db.CASCADE, related_name="address", pk=True
    )

    def __str__(self):
        return f"Address({self.city}, {self.street})"


class Team(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()

    events: db.ManyToManyRelation[Event]

    def __str__(self):
        return self.name


@app.route("/verloop")
async def run():
    tournament = Tournament(name="New Tournament")
    await tournament.save()
    await Event(name="Without participants", tournament_id=tournament.id).save()
    event = Event(name="Test", tournament_id=tournament.id)
    await event.save()

    await Address.create(city="Santa Monica", street="Ocean", event=event)

    participants = []
    for i in range(2):
        team = Team(name=f"Team {(i + 1)}")
        await team.save()
        participants.append(team)
    await event.participants.add(participants[0], participants[1])
    await event.participants.add(participants[0], participants[1])

    try:
        for team in event.participants:
            print(team.id)
    except NoValuesFetched:
        pass

    async for team in event.participants:
        print(team.id)

    for team in event.participants:
        print(team.id)

    print(
        await Event.filter(participants=participants[0].id).prefetch_related(
            "participants", "tournament"
        )
    )
    print(await participants[0].fetch_related("events"))

    print(await Team.fetch_for_list(participants, "events"))

    print(await Team.filter(events__tournament__id=tournament.id))

    print(await Event.filter(tournament=tournament))

    print(
        await Tournament.filter(events__name__in=["Test", "Prod"])
        .order_by("-events__participants__name")
        .distinct()
    )

    print(await Event.filter(id=event.id).values("id", "name", tournament="tournament__name"))

    print(await Event.filter(id=event.id).values_list("id", "participants__name"))

    print(await Address.filter(event=event).first())

    event_reload1 = await Event.filter(id=event.id).first()
    print(await event_reload1.address)

    event_reload2 = await Event.filter(id=event.id).prefetch_related("address").first()
    print(event_reload2.address)
    return 'null'


if __name__ == "__main__":
    app.run()
```

## Relations with Unique field

```python
"""
This example shows how relations between models especially unique field work.

Key points in this example are use of ForeignKeyField and OneToOneField has to_field.
For other basic parts, it is the same as relation exmaple.
"""
from tortoise.query_utils import Prefetch


class School(db.Model):
    uuid = db.UUIDField(pk=True)
    name = db.TextField()
    id = db.IntField(unique=True)

    students: db.ReverseRelation["Student"]
    principal: db.ReverseRelation["Principal"]


class Student(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    school: db.ForeignKeyRelation[School] = db.ForeignKeyField(
        "models.School", related_name="students", to_field="id"
    )


class Principal(db.Model):
    id = db.IntField(pk=True)
    name = db.TextField()
    school: db.OneToOneRelation[School] = db.OneToOneField(
        "models.School", on_delete=db.CASCADE, related_name="principal", to_field="id"
    )


@app.route("/forloop")
async def run():
    school1 = await School.create(id=1024, name="School1")
    student1 = await Student.create(name="Sang-Heon Jeon1", school_id=school1.id)

    student_schools = await Student.filter(name="Sang-Heon Jeon1").values("name", "school__name")
    print(student_schools[0])

    await Student.create(name="Sang-Heon Jeon2", school=school1)
    school_with_filtered = (
        await School.all()
        .prefetch_related(Prefetch("students", queryset=Student.filter(name="Sang-Heon Jeon1")))
        .first()
    )
    school_without_filtered = await School.first().prefetch_related("students")
    print(len(school_with_filtered.students))
    print(len(school_without_filtered.students))

    school2 = await School.create(id=2048, name="School2")
    await Student.all().update(school=school2)
    student = await Student.first()
    print(student.school_id)

    await Student.filter(id=student1.id).update(school=school1)
    schools = await School.all().order_by("students__name")
    print([school.name for school in schools])

    fetched_principal = await Principal.create(name="Sang-Heon Jeon3", school=school1)
    print(fetched_principal.name)
    fetched_school = await School.filter(name="School1").prefetch_related("principal").first()
    print(fetched_school.name)
    return 'null'

if __name__ == "__main__":
    app.run()
```

## Recursive relations

```python
"""
This example shows how self-referential (recursive) relations work.

Key points in this example are:
* Use of ForeignKeyField that refers to self
* To pass in the (optional) parent node at creation
* To use async iterator to fetch children
* To use .fetch_related(…) to emulate sync behaviour
* That insert-order gets preserved for ForeignFields, but not ManyToManyFields
"""

class Employee(db.Model):
    name = db.CharField(max_length=50)

    manager: db.ForeignKeyNullableRelation["Employee"] = db.ForeignKeyField(
        "models.Employee", related_name="team_members", null=True
    )
    team_members: db.ReverseRelation["Employee"]

    talks_to: db.ManyToManyRelation["Employee"] = db.ManyToManyField(
        "models.Employee", related_name="gets_talked_to"
    )
    gets_talked_to: db.ManyToManyRelation["Employee"]

    def __str__(self):
        return self.name

    async def full_hierarchy__async_for(self, level=0):
        """
        Demonstrates ``async for` to fetch relations

        An async iterator will fetch the relationship on-demand.
        """
        text = [
            "{}{} (to: {}) (from: {})".format(
                level * "  ",
                self,
                ", ".join([str(val) async for val in self.talks_to]),
                ", ".join([str(val) async for val in self.gets_talked_to]),
            )
        ]
        async for member in self.team_members:
            text.append(await member.full_hierarchy__async_for(level + 1))
        return "\n".join(text)

    async def full_hierarchy__fetch_related(self, level=0):
        """
        Demonstrates ``await .fetch_related`` to fetch relations

        On prefetching the data, the relationship files will contain a regular list.

        This is how one would get relations working on sync serialization/templating frameworks.
        """
        await self.fetch_related("team_members", "talks_to", "gets_talked_to")
        text = [
            "{}{} (to: {}) (from: {})".format(
                level * "  ",
                self,
                ", ".join([str(val) for val in self.talks_to]),
                ", ".join([str(val) for val in self.gets_talked_to]),
            )
        ]
        for member in self.team_members:
            text.append(await member.full_hierarchy__fetch_related(level + 1))
        return "\n".join(text)

@app.route("/relationer")
async def run():
    root = await Employee.create(name="Root")
    loose = await Employee.create(name="Loose")
    _1 = await Employee.create(name="1. First H1", manager=root)
    _2 = await Employee.create(name="2. Second H1", manager=root)
    _1_1 = await Employee.create(name="1.1. First H2", manager=_1)
    _1_1_1 = await Employee.create(name="1.1.1. First H3", manager=_1_1)
    _2_1 = await Employee.create(name="2.1. Second H2", manager=_2)
    _2_2 = await Employee.create(name="2.2. Third H2", manager=_2)

    await _1.talks_to.add(_2, _1_1_1, loose)
    await _2_1.gets_talked_to.add(_2_2, _1_1, loose)

    # Evaluated off creation objects
    print(await loose.full_hierarchy__fetch_related())
    print(await root.full_hierarchy__async_for())
    print(await root.full_hierarchy__fetch_related())

    # Evaluated off new objects → Result is identical
    root2 = await Employee.get(name="Root")
    loose2 = await Employee.get(name="Loose")
    print(await loose2.full_hierarchy__fetch_related())
    print(await root2.full_hierarchy__async_for())
    print(await root2.full_hierarchy__fetch_related())
    return 'null'

if __name__ == "__main__":
    app.run()
```