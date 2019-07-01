from django.db import models

# Create your models here.

class InitRelation(models.Model):
    class Meta:
       db_table = 'InitRelation'

    src = models.CharField(max_length=32)
    target = models.CharField(max_length=32)
    weight = models.IntegerField(default=0)
