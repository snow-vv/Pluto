from django.contrib.auth.models import User
from django.db import models
from common.utils.enum import Enum


class CLOUD_TYPE(Enum):
    ALI = 1, '阿里云'


class ECS(models.Model):
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=100, unique=True)
    instance_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    cpu = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    description = models.CharField(max_length=200, default='', blank=True)
    public_ip = models.CharField(max_length=30, null=True, blank=True)
    created_time = models.DateTimeField(null=True, auto_now_add=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class InstanceType(models.Model):
    code = models.CharField(max_length=100)
    cpu_core_count = models.IntegerField()
    memory_size = models.IntegerField(help_text="单位GB")
    cloud_type = models.IntegerField(choices=CLOUD_TYPE, default=CLOUD_TYPE.ALI)


class SLB(models.Model):
    instance_id = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    ip = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, default='')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class UserExtra(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=13, null=True, blank=True)


class RDS(models.Model):
    instance_id = models.CharField(max_length=30)
    region_id = models.CharField(max_length=50)
    description = models.CharField(max_length=200, default='', blank=True)
    status = models.CharField(max_length=100, default='', blank=True)
    slow_log_dingding = models.CharField(max_length=200, default='', blank=True)

