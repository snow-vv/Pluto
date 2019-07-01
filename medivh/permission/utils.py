# -*- coding: UTF-8 -*-
from permission.models import Permission, Group
from common.exception import PermissionDeniedException


def check_permission(user, permissions):
    user_permissions = set()
    for group in Group.objects.filter(users=user):
        for permission in group.permissions.all():
            user_permissions.add(permission.code)
    t = set(permissions) - user_permissions

    if t:
        require_permissions = Permission.objects.filter(code__in=t).values_list("description", flat=True)
        raise PermissionDeniedException(
            message="本页面需要{}权限。\n如需使用，请向管理申请权限。".format(",".join(map(lambda x: "【" + x + "】", require_permissions)))
        )


def check_services(user, services):
    user_services = set()
    for group in Group.objects.filter(users=user):
        for service in group.services.all():
            user_services.add(service)
    t = set(services) - user_services

    if t:
        raise PermissionDeniedException(
            message="您没有{}权限。\n如需使用，请向管理申请权限。".format(",".join(map(lambda x: "【" + x.name + "】", t)))
        )
