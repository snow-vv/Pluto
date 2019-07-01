# -*- coding: UTF-8 -*-
from cmdb.models import UserExtra


def get_user_extra_by_user(user):
    extra, _ = UserExtra.objects.get_or_create(user=user)
    return extra
