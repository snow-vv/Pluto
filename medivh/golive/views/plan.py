import datetime
import json

from common.exception import RunInfoNotFountException, StatusMismactchException, NoCommitSHAException
from common.utils.time import from_timestamp, to_timestamp
from common.views import JsonView
from golive.models import Plan, PLAN_STATUS, PlanExecution, Service, PlanStage, Task, \
    PlanStageExecutionSubTask, PLAN_STAGE_STATUS, SERVICE_RUNINFO_TYPE, PlanStageExecution, \
    ServiceCommitRecords, ServiceExecutionInfo
from golive.tasks import run_plan, run_stage
from golive.utils.notify import plan_auditing_notify, plan_release_done_notify
from permission.utils import check_services


class PlanListApiView(JsonView):
    permissions = ['plan.list']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        plans = Plan.objects.order_by('-id')
        total = plans.count()
        plans = plans[(page - 1) * num: page * num]
        return {
            'total': total,
            'list': [
                {
                    "id": plan.id,
                    "description": plan.description,
                    "golive_expected_time": to_timestamp(plan.golive_expected_time),
                    "notes": plan.notes,
                    "creator": {
                        "id": plan.creator.id,
                        "name": plan.creator.username,
                    },
                    "services": [
                        {
                            'id': stage.service.id,
                            'name': stage.service.name
                        } for stage in plan.planstage_set.order_by('order')],
                    "status": {
                        "value": plan.status,
                        "desc": PLAN_STATUS.getDesc(plan.status),
                    }
                } for plan in plans
            ]
        }


class PlanDetailApiView(JsonView):
    permissions = ['plan.detail']

    def get(self, request, plan_id):
        plan = Plan.objects.get(id=plan_id)
        return {
            'name': plan.description,
            'golive_expected_time': to_timestamp(plan.golive_expected_time),
            'notes': plan.notes,
            'status': {
                'value': plan.status,
                'desc': PLAN_STATUS.getDesc(plan.status),
            },
            'stages': [
                {
                    'id': stage.id,
                    'service_id': stage.service_id,
                    'tasks': [
                        {
                            'id': task.id,
                            'function_id': task.function_id,
                            'params': json.loads(task.params_json),
                        } for task in stage.tasks.order_by('order')
                    ]
                } for stage in plan.planstage_set.order_by('order')
            ]
        }

    def post(self, request, plan_id=None):
        data = json.loads(json.loads(request.body.decode("utf-8"))['data'])
        # # must given commit SHA when add GitPullTask
        # for state in data.get('stages', []):
        #     for task in state.get('tasks', []):
        #         #NOTE: function_id为1为拉代码的task, 后期如有修改，应与golive.commands.init_functions以及前端定义相一致
        #         if task.get('function_id') == 1 and task.get('version') == "":
        #             raise NoCommitSHAException
        is_audit = int(json.loads(request.body.decode("utf-8"))['is_audit'])
        if is_audit:
            status = PLAN_STATUS.AUDIT_PASS
        else:
            status = PLAN_STATUS.EDITING
        if plan_id:
            plan = Plan.objects.get(id=plan_id)
            plan.description = data['name']
            plan.notes = data['notes']
            plan.golive_expected_time = from_timestamp(float(data['golive_expected_time']), )
            plan.status = status
            plan.save()
        else:
            plan = Plan.objects.create(
                description=data['name'],
                notes=data['notes'],
                golive_expected_time=from_timestamp(float(data['golive_expected_time'])),
                creator=request.user,
                status=status,
            )
        for index, stage_data in enumerate(data['stages']):
            stage_id = stage_data.get('id', None)
            service_id = stage_data.get('service_id', None)
            if stage_id:
                stage = PlanStage.objects.get(id=stage_id, plan=plan)
                stage.service_id = service_id
                stage.order = index
                stage.save()
            else:
                stage = PlanStage.objects.create(
                    plan=plan,
                    service_id=service_id,
                    order=index,
                )
            stage.tasks.remove(*stage.tasks.all())
            for index, task_data in enumerate(stage_data['tasks']):
                task_id = task_data.pop('id', None)
                function_id = task_data.pop('function_id', None)
                if task_id:
                    task = Task.objects.get(id=task_id)
                    task.function_id = function_id
                    task.params_json = json.dumps(task_data)
                    task.order = index
                    task.save()
                else:
                    task = Task.objects.create(
                        function_id=function_id,
                        params_json=json.dumps(task_data),
                        order=index,
                    )
                stage.tasks.add(task)

        if is_audit:
            plan_auditing_notify(plan)
            plan.save()


def get_host_status_by_stage(stage):
    l = []
    for host in stage.service.ecses.all():
        pse = stage.planstageexecution_set.filter(service_execution_info__ecses=host).order_by('start_time').last()
        if pse:
            status = {'value': pse.status, 'desc': PLAN_STAGE_STATUS.getDesc(pse.status)}
        else:
            status = {'value': 0, 'desc': '未执行'}
        l.append({
            'host_id': host.id,
            'host_name': host.name,
            'status': status,
        })
    return l


class PlanExecutionApiView(JsonView):
    permissions = ['plan.execution']

    def get(self, request, plan_id):
        plan = Plan.objects.get(id=plan_id)
        return {
            'name': plan.description,
            'golive_expected_time': to_timestamp(plan.golive_expected_time),
            'notes': plan.notes,
            'status': {
                'value': plan.status,
                'desc': PLAN_STATUS.getDesc(plan.status),
            },
            'stages': [
                {
                    'id': stage.id,
                    'service': {
                        'id': stage.service_id,
                        'name': stage.service.name,
                    },
                    'tasks': [
                        {
                            'id': task.id,
                            'function_id': task.function_id,
                            'params': json.loads(task.params_json),
                        } for task in stage.tasks.order_by('order')
                    ],
                    'commit_ids': [
                        {
                            'commit_id': item.commit_id,
                            'ctime': item.ctime.strftime('%Y-%m-%d %H:%M:%S'),
                            'text': str(item.plan_id) + ' ' + item.plan.description + ' ' + item.ctime.strftime(
                                '%Y-%m-%d %H:%M:%S') + ' ' + item.commit_id[:10]
                        }
                        for item in ServiceCommitRecords.objects.filter(
                            service_id=stage.service_id
                        ).order_by('-id')[:10]
                    ],
                    'hosts': get_host_status_by_stage(stage),
                    'service_execution_info': [
                        {
                            'id': info.id,
                            'name': "{}:{}".format(stage.service.name, SERVICE_RUNINFO_TYPE.getDesc(info.type)),
                            'type': info.type
                        } for info in stage.service.serviceexecutioninfo_set.all()
                    ],
                } for stage in plan.planstage_set.order_by('order')
            ],
            'execution_info_types': [
                {'value': key, 'desc': value}
                for key, value in SERVICE_RUNINFO_TYPE
            ]
        }


class PlanStageHostApiView(JsonView):
    permissions = ['plan.execution']

    def get(self, request, stage_id):
        stage = PlanStage.objects.get(id=stage_id)
        return {
            'list': get_host_status_by_stage(stage),
        }


class ServiceListApiView(JsonView):
    def get(self, request):
        return {
            'list': [
                {'id': service.id, 'name': service.name}
                for service in Service.objects.all()
            ]
        }


class ServiceCommitView(JsonView):
    def get(self, request):
        size = 10
        service_id = int(request.GET.get('service_id'))
        return {
            'list': [
                {'commit_id': item.commit_id,
                 'ctime': item.ctime.strftime('%Y-%m-%d %H:%M:%S'),
                 'text': str(item.plan_id) + ' ' + item.plan.description + ' ' + item.ctime.strftime(
                     '%Y-%m-%d %H:%M:%S') + ' ' + item.commit_id[:10]}
                for item in ServiceCommitRecords.objects.filter(service_id=service_id).order_by('-id')[:size]
            ]
        }


class GreyServiceListApiView(JsonView):  # 获取能够进行灰度的服务
    def get(self, request):
        return {
            'list': [
                {'id': service.id, 'name': service.name} for service in
                Service.objects.filter(serviceexecutioninfo__type=SERVICE_RUNINFO_TYPE.GRAY)
            ]
        }


class RunPlanApiView(JsonView):
    permissions = ['plan.execution.run']

    def post(self, request, plan_id, run_type):
        run_type = int(run_type)
        plan = Plan.objects.get(id=plan_id)
        if not request.user.is_superuser:
            check_services(
                user=request.user,
                services=[stage.service for stage in plan.planstage_set.all()]
            )
        execution = PlanExecution.objects.create(
            plan_id=plan_id,
            user=request.user,
        )
        if plan.status != PLAN_STATUS.AUDIT_PASS:
            raise StatusMismactchException
        for stage in plan.planstage_set.all():
            if not stage.service.serviceexecutioninfo_set.filter(type=run_type).exists():
                raise RunInfoNotFountException(
                    message="{}没有{}".format(stage.service.name, SERVICE_RUNINFO_TYPE.getDesc(run_type))
                )
        run_plan.delay(
            plan_id=plan_id,
            execution_id=execution.id,
            service_execution_info_type=run_type,
        )
        return {
            'execution_id': execution.id,
        }


class RunStageApiView(JsonView):
    permissions = ['plan.execution.run']

    def post(self, request, stage_id, execution_info_id):
        stage = PlanStage.objects.get(id=stage_id)
        if not request.user.is_superuser:
            check_services(
                user=request.user,
                services=[stage.service]
            )
        if stage.plan.status != PLAN_STATUS.AUDIT_PASS:
            raise StatusMismactchException
        execution = PlanExecution.objects.create(
            plan_id=stage.plan_id,
            user=request.user,
        )
        run_stage.delay(
            stage_id=stage_id,
            execution_id=execution.id,
            service_execution_info_id=execution_info_id,
        )
        return {
            'execution_id': execution.id,
        }


class RunStageRollbackView(JsonView):
    permissions = ['plan.execution.run']

    def post(self, request, stage_id):
        commit_id = json.loads(request.body.decode('utf-8'))['commit_id']
        stage = PlanStage.objects.get(id=stage_id)
        if not request.user.is_superuser:
            check_services(user=request.user, services=[stage.service])

        if stage.plan.status == PLAN_STATUS.GOLIVED:
            raise StatusMismactchException

        execution = PlanExecution.objects.create(
            plan_id=stage.plan_id,
            user=request.user
        )

        service_execution_info_id = ServiceExecutionInfo.objects.get(
            service=stage.service,
            type=SERVICE_RUNINFO_TYPE.ALL
        ).id

        run_stage.delay(
            stage_id=stage_id,
            execution_id=execution.id,
            service_execution_info_id=service_execution_info_id,
            commit_id=commit_id
        )

        return {
            'execution_id': execution.id
        }


class ExecutionsResultApiView(JsonView):
    def get(self, request, execution_id):
        execution = PlanExecution.objects.get(id=execution_id)
        return {
            'finish': True if execution.end_time else False,
            'list': [
                {
                    'message': task.description,
                    'stack': task.result_json,
                    'id': task.id,
                    'is_success': task.is_success,
                    'ip': task.host
                } for task in PlanStageExecutionSubTask.objects.filter(plan_stage_execution__execution=execution)
            ]
        }


class ReleaseDoneApiView(JsonView):
    permissions = ['plan.execution.run']

    def post(self, request, plan_id):
        plan = Plan.objects.get(id=plan_id)
        if plan.status != PLAN_STATUS.AUDIT_PASS:
            raise StatusMismactchException
        plan.status = PLAN_STATUS.GOLIVED
        plan.save()
        plan_release_done_notify(plan)

        stages = plan.planstage_set.all()
        for stage_obj in stages:
            # find latest commit_id.
            stage_exec_obj = PlanStageExecution.objects.filter(
                plan_stage=stage_obj,
                status=PLAN_STAGE_STATUS.SUCCESS).order_by('-id').first()

            task_obj = PlanStageExecutionSubTask.objects.filter(
                plan_stage_execution=stage_exec_obj
            ).first()
            rs = json.loads(task_obj.result_json)
            ServiceCommitRecords.objects.create(
                service=stage_obj.service,
                commit_id=rs['after'],
                plan=plan
            )
        return {}
