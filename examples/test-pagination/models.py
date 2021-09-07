from flask_tortoise import Tortoise, fields
from flask_tortoise.models import Manager
# from datetime import datetime

db = Tortoise()

class Posts(db.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=True)
    body = fields.TextField()
    created_at = fields.DatetimeField(auto_now=True)

    class Meta:
        manager = Manager()