from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from golive.models import Service


class Permission(models.Model):
    code = models.CharField(max_length=30)
    description = models.CharField(max_length=200)


class Group(models.Model):
    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User)
    permissions = models.ManyToManyField(Permission)
    services = models.ManyToManyField(Service)

    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "users": [
                {"id": user.id, "name": user.last_name or user.username}
                for user in self.users.all()
                ],
            "permissions": [
                {
                    'id': permission.id,
                    'code': permission.code,
                    'description': permission.description,
                } for permission in self.permissions.all()],
            "services": [
                {
                    'id': service.id,
                    'name': service.name,
                } for service in self.services.all()],
        }
