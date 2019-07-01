# -*- coding: UTF-8 -*-
import json
import datetime

import requests
from django.conf import settings

from common.utils.aliyun import aliyun_slb
from common.views import JsonView
from common.exception import StatusMismactchException, SlbException, GreyEcsNotOneException
from golive.models import Grey, GREY_STATUS, PlanExecution, SERVICE_RUNINFO_TYPE, Service, DtabRules

from golive.tasks import run_grey_start, run_grey_reset
from golive.utils.grey import check_slb_num


class GreyListApiView(JsonView):
    permissions = ['grey.list']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        greys = Grey.objects.order_by('-id')
        total = greys.count()
        greys = greys[(page - 1) * num: page * num]

        def get_desc(grey):
            t = []
            for service in grey.services.all():
                info = service.serviceexecutioninfo_set.get(type=SERVICE_RUNINFO_TYPE.GRAY)
                ecs = info.ecses.first()
                if info.ecses.count() != 1:
                    raise GreyEcsNotOneException
                for slb in service.slbs.all():
                    t.append('[{}] 将 SLB({}) 中 ECS({}) 的权重改为0'.format(service.name, slb.name, ecs.name))
                t.append('[{}] 更改 ECS({}) 上的路由表'.format(service.name, ecs.name))
                t.append('[{}] 重启 ECS({}) 上的 {} 服务'.format(service.name, ecs.name, service.name))
            return '\n'.join(t)

        return {
            'total': total,
            'list': [
                {
                    "id": grey.id,
                    "description": get_desc(grey),
                    "name": grey.name,
                    "ecses": [
                        {
                            "id": ecs.id,
                            "name": ecs.name,
                        } for ecs in grey.ecses.all()
                        ],
                    "services": [
                        {
                            'id': service.id,
                            "name": service.name,
                        } for service in grey.services.all()
                        ],
                    "route_path": grey.route_path,
                    "status": {
                        "value": grey.status,
                        "desc": GREY_STATUS.getDesc(grey.status),
                    }
                }
                for grey in greys
                ]
        }


class ConfirmGreyApiView(JsonView):
    permissions = ['grey.start']

    def post(self, request, grey_id):
        request_body = json.loads(request.body.decode("utf-8"))
        service_ids = request_body.get("services")

        def get_desc(service_ids):
            t = []
            services = Service.objects.filter(id__in=service_ids).all()
            for service in services:
                info = service.serviceexecutioninfo_set.get(type=SERVICE_RUNINFO_TYPE.GRAY)
                ecs = info.ecses.first()
                if info.ecses.count() != 1:
                    raise GreyEcsNotOneException
                for slb in service.slbs.all():
                    check_slb_num(slb)
                    t.append('[{}] 将 SLB({}) 中 ECS({}) 的权重改为0'.format(service.name, slb.name, ecs.name))
                t.append('[{}] 更改 ECS({}) 上的路由表'.format(service.name, ecs.name))
                t.append('[{}] 重启 ECS({}) 上的 {} 服务'.format(service.name, ecs.name, service.name))
            return '\n'.join(t)

        return {
            'description': get_desc(service_ids)
        }


class GreyStartApiView(JsonView):
    permissions = ['grey.start']

    def post(self, request, grey_id):
        grey = Grey.objects.get(id=grey_id)
        grey.services.clear()
        request_body = json.loads(request.body.decode("utf-8"))
        service_ids = request_body.get("services")
        services = Service.objects.filter(id__in=service_ids)
        for service in services:
            grey.services.add(service)
        if grey.status not in [GREY_STATUS.NORMAL, GREY_STATUS.FAIL]:
            raise StatusMismactchException
        execution = PlanExecution.objects.create(
            user=request.user,
        )
        grey.executions.add(execution)
        grey.save()
        run_grey_start.delay(grey.id, execution.id)
        return {
            'execution_id': execution.id,
        }


class ConfirmResetApiView(JsonView):
    permissions = ['grey.reset']

    def post(self, request, grey_id):
        grey = Grey.objects.get(id=grey_id)

        def get_desc():
            t = []
            for service in grey.services.all():
                info = service.serviceexecutioninfo_set.get(type=SERVICE_RUNINFO_TYPE.GRAY)
                ecs = info.ecses.first()
                if info.ecses.count() != 1:
                    raise GreyEcsNotOneException
                t.append('[{}] 更改 ECS({}) 上的路由表'.format(service.name, ecs.name))
                t.append('[{}] 重启 ECS({}) 上的 {} 服务'.format(service.name, ecs.name, service.name))
                for slb in service.slbs.all():
                    t.append('[{}] 将 SLB({}) 中 ECS({}) 的权重改为0'.format(service.name, slb.name, ecs.name))
            return '\n'.join(t)

        return {
            'description': get_desc()
        }


class GreyResetApiView(JsonView):
    permissions = ['grey.reset']

    def post(self, request, grey_id):
        grey = Grey.objects.get(id=grey_id)
        if grey.status not in [GREY_STATUS.SUCCESS, GREY_STATUS.RESET_FAIL, GREY_STATUS.FAIL]:
            raise StatusMismactchException
        execution = PlanExecution.objects.create(
            user=request.user,
        )
        grey.executions.add(execution)
        grey.save()
        run_grey_reset.delay(grey.id, execution.id)
        return {
            'execution_id': execution.id,
        }



class GreyRuleApiView(JsonView):
    permissions = ['grey.start']

    def get(self, request):
        resp = requests.get(settings.NAMERD_DTAB_GM_URL)
        status_code = resp.status_code
        if status_code == 200:
            data_list = json.loads(resp.text)
        else:
            data_list = []
        print(status_code)
        return {
            'list': data_list,
            'message': 'namerd return status_code {} when fetch namerd data'.format(status_code),
            'success': 1 if status_code==200 else 0,
        }

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        dtabs_rule = data.get('dtabs_rule').encode("utf-8")
        execution = PlanExecution.objects.create(
            user=request.user,
        )
        execution.start_time = datetime.datetime.now()
        resp = requests.put(settings.NAMERD_DTAB_GM_URL, data=dtabs_rule, headers={'Content-Type':'application/dtab'})
        status_code = resp.status_code
        print(resp.text)
        code_result = {
            204: 'Success - Updated',
            400: 'Failed!!! - Dtab is malformed',
            404: 'Failed!!! - Dtab namespace does not exist',
            412: 'Failed!!! - If-Match header is provided and does not match the current dtab version'
        }
        status = code_result[status_code] if status_code in code_result else 'Failed!!! - status_code:{}'.format(status_code)
        description = '[{status}] {conf_text}'.format(
            status=status,
            conf_text=dtabs_rule,
        )[:497]
        if len(description) == 497:
            description += '...'
        execution.description = description
        execution.end_time = datetime.datetime.now()
        execution.save()
        return {
            'execution_id': execution.id,
            'message': status,
            'success': 1 if status_code==204 else 0,
        }


class DtabRulesExamplesApiView(JsonView):
    permissions = ['grey.start']

    def get(self, request):
        dtabrules = DtabRules.objects.all()
        return {
            'list': [
                {
                    'name': dtabrule.name,
                    'rule': dtabrule.rule,
                } for dtabrule in dtabrules
            ]
        }
        
