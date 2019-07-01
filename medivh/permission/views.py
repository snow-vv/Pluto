import json

from django.contrib.auth.models import User
from django.shortcuts import render
from common.views import JsonView
from golive.models import Service
from permission.models import Permission
from permission.models import Group, Permission


# Create your views here.
class PermissionView(JsonView):
    permissions = ['permission.permissions']

    def get(self, request):
        all = int(request.GET.get('all', 0))
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        counts = Permission.objects.count()
        permissions = Permission.objects.order_by('-id')
        if not all:
            permissions = permissions[(page - 1) * num:page * num]
        perms = [
            {
                'code': permission.code,
                'id': permission.id,
                'description': permission.description
            } for permission in permissions
            ]
        data = {
            'list': perms,
            'total': counts
        }

        return data


class GroupListView(JsonView):
    permissions = ['permission.groups']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        groups = Group.objects.order_by('-id')
        total = groups.count()
        groups = groups[(page - 1) * num: page * num]
        return {
            'total': total,
            'list': [
                group.data() for group in groups
                ]
        }


class GroupDetailView(JsonView):
    permissions = ['permission.group.detail']

    def get(self, request, group_id):
        group = Group.objects.get(id=group_id)
        return group.data()

    def post(self, request, group_id=None):
        data = json.loads(request.body.decode("utf-8"))['data']
        if group_id is not None:
            group = Group.objects.get(id=group_id)
            group.name = data['name']
            group.save()
        else:
            group = Group.objects.create(
                name=data['name'],
            )
        permission_ids = list(map(lambda x: x['id'], data['permissions']))
        group.permissions.remove(*group.permissions.exclude(id__in=permission_ids))
        group.permissions.add(*Permission.objects.filter(id__in=permission_ids))

        user_ids = list(map(lambda x: x['id'], data['users']))
        group.users.remove(*group.users.exclude(id__in=user_ids))
        group.users.add(*User.objects.filter(id__in=user_ids))

        service_ids = list(map(lambda x: x['id'], data['services']))
        group.services.remove(*group.services.exclude(id__in=service_ids))
        group.services.add(*Service.objects.filter(id__in=service_ids))
        group.save()
