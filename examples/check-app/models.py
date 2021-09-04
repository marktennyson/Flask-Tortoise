from tortoise import Model, fields
from flask_tortoise import FlaskTortoise

db:"FlaskTortoise" = FlaskTortoise()


class Users(db.Model):
    id = fields.IntField(pk=True)
    status = db.fields.CharField(20)

    def __str__(self):
        return f"User {self.id}: {self.status}"


class Workers(db.Model):
    id = db.fields.IntField(pk=True)
    status = db.fields.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"