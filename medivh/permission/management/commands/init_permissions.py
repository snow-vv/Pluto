# -*- coding: UTF-8 -*-
import json

from django.core.management import BaseCommand
from permission.models import Permission


class Command(BaseCommand):
    def handle(self, *args, **options):
        permissions = [
            {'code': 'audit.executions', 'description': '审计: 执行记录'},
            {'code': 'cmdb.ecs.list', 'description': 'CMDB：ECS列表'},
            {'code': 'cmdb.ecs.sync', 'description': 'CMDB: ECS同步'},
            {'code': 'cmdb.service.list', 'description': 'CMDB：服务列表'},
            {'code': 'cmdb.slb.change_weight', 'description': 'CMDB：修改负载均衡权重'},
            {'code': 'cmdb.slb.detail', 'description': 'CMDB：负载均衡页面'},
            {'code': 'grey.list', 'description': '灰度：计划列表'},
            {'code': 'grey.reset', 'description': '灰度：恢复计划'},
            {'code': 'grey.start', 'description': '灰度：执行计划'},
            {'code': 'permission.group.detail', 'description': '权限：权限组编辑'},
            {'code': 'permission.groups', 'description': '权限: 权限组列表'},
            {'code': 'permission.permissions', 'description': '权限: 权限列表'},
            {'code': 'plan.detail', 'description': '上线计划：创建和编辑'},
            {'code': 'plan.execution', 'description': '上线计划: 执行页面'},
            {'code': 'plan.execution.run', 'description': '上线计划: 执行'},
            {'code': 'plan.list', 'description': '上线计划：计划列表'},
            {'code': 'service.relation', 'description': '服务：关系图'},
            {'code': 'shield.add_black_ip', 'description': 'GM-Shield：黑名单添加IP'},
            {'code': 'shield.black_ips', 'description': 'GM-Shield：黑名单列表'},
            {'code': 'shield.rm_black_ip', 'description': 'GM－Shield：黑名单移除IP'}]
        for f in permissions:
            Permission.objects.get_or_create(**f)
