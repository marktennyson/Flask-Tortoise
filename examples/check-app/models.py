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