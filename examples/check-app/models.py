from flask_tortoise import Tortoise, Model, fields
from flask_tortoise.models import Manager

db:"Tortoise" = Tortoise()


class Users(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)
    # name = fields.CharField(20, null=True)

    def __str__(self):
        return f"User {self.id}: {self.status}"
    class Meta:
        manager = Manager()


class Workers(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"