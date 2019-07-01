# Create your views here.
import json

from django.contrib.auth.models import User

from cmdb.models import ECS, SLB
from cmdb.tasks import sync_ecs, sync_rds
from common.utils.aliyun import aliyun_slb
from common.utils.time import to_timestamp
from common.views import JsonView
from common.exception import MedivhExceptionBase
from golive.models import Service


class ECSListApiView(JsonView):
    permissions = ['cmdb.ecs.list']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        ecses = ECS.objects.order_by('-id')
        total = ecses.count()
        plans = ecses[(page - 1) * num: page * num]
        return {
            'total': total,
            'list': [
                {
                    "name": ecs.name,
                    "ip": ecs.ip,
                    "instance_id": ecs.instance_id,
                    "cpu": ecs.cpu,
                    "memory": ecs.memory,
                    "description": ecs.description,
                    "public_ip": ecs.public_ip,
                    "created_time": to_timestamp(ecs.created_time) if ecs.created_time else None,
                    "id": ecs.id,
                } for ecs in plans
                ]
        }


class ECSSyncApiView(JsonView):
    permissions = ['cmdb.ecs.sync']

    def post(self, request):
        sync_ecs.delay()
        return {}


class RDSSyncApiView(JsonView):
    permissions = ['cmdb.ecs.sync']

    def get(self, request):
        sync_rds.delay()
        return {"message": "ok"}


class SLBDetailApiView(JsonView):
    permissions = ['cmdb.slb.detail']

    def get(self, request, slb_id):
        slb = SLB.objects.get(id=slb_id)
        res = aliyun_slb.info('cn-qingdao', slb.instance_id)
        servers = res['BackendServers']['BackendServer']
        l = []
        for server in servers:
            ecs = ECS.objects.get(instance_id=server['ServerId'])
            l.append({
                'id': ecs.id,
                'name': ecs.name,
                'weight': server['Weight'],
            })
        return {
            'name': slb.name,
            'description': slb.description,
            'list': l,
        }


class SLBChangeWeightApiView(JsonView):
    permissions = ['cmdb.slb.change_weight']

    def post(self, request, slb_id, ecs_id):
        data = json.loads(request.body.decode("utf-8"))
        weight = data.get('params').get('weight', None)
        if weight is None:
            raise MedivhExceptionBase(code=1, message='请填写权重')
        slb = SLB.objects.get(id=slb_id)
        ecs = ECS.objects.get(id=ecs_id)
        aliyun_slb.set_weight('cn-qingdao', slb.instance_id, ecs.instance_id, weight)
        return {}


class ServiceListApiView(JsonView):
    permissions = ['cmdb.service.list']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        services = Service.objects.order_by('-id')
        total = services.count()
        services = services[(page - 1) * num: page * num]
        return {
            'total': total,
            'list': [
                {
                    'id': service.id,
                    "name": service.name,
                    "git_repo": service.git_repo.repo,
                    "ecses": [
                        {'id': ecs.id, 'name': ecs.name}
                        for ecs in service.ecses.all()
                        ],
                    "slbs": [
                        {'id': slb.id, "name": slb.name}
                        for slb in service.slbs.all()
                        ],
                } for service in services
                ]
        }


class UserListView(JsonView):
    def get(self, request):
        users = User.objects.all()
        return {
            'total': users.count(),
            'list': [
                {
                    'id': user.id,
                    'name': user.username or user.last_name,
                } for user in users
                ]
        }
