from flask_tortoise import Tortoise, Manager

models:"Tortoise" = Tortoise()


class Users(models.Model):
    id = models.IntField(pk=True)
    status = models.CharField(20)
    # name = fields.CharField(20, null=True)

    def __str__(self):
        return f"User {self.id}: {self.status}"
    class Meta:
        manager = Manager()


class Workers(models.Model):
    id = models.IntField(pk=True)
    status = models.CharField(20)

    def __str__(self):
        return f"Worker {self.id}: {self.status}"