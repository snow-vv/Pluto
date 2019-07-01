# -*- coding: UTF-8 -*-
import datetime
import json
import os

from celery import shared_task
from django.conf import settings

from common.exception import SlbException
from common.logger import log_error
from common.utils.aliyun import aliyun_slb
from golive.models import Plan, PlanExecution, PLAN_STAGE_STATUS, SERVICE_RUNINFO_TYPE, Grey, GREY_STATUS, \
    PlanStageExecutionSubTask
from golive.models import PlanStageExecution, PlanStage, ServiceExecutionInfo
from golive.runner.ansible.run import ansible_run, AnsibleRunResultCallBack
from golive.runner.ansible.tasks import get_ansible_task_by_stage, CopyFileTask, RestartTask, DeployConfigTask, \
    PullConfigTask, GitRollbackTask
from golive.utils.grey import check_slb_num


def start_stage(stage_id, execution, service_execution_info_id, commit_id=None):
    if not isinstance(stage_id, PlanStage):
        stage = PlanStage.objects.get(id=stage_id)
    else:
        stage = stage_id
    service_execution_info = ServiceExecutionInfo.objects.get(id=service_execution_info_id)

    if commit_id is None:
        tasks = get_ansible_task_by_stage(stage)
    else:
        tasks = GitRollbackTask(service=stage.service, commit_id=commit_id).to_task()
    ips = list(service_execution_info.ecses.values_list('ip', flat=True))
    plan_stage_execution = PlanStageExecution.objects.create(
        execution=execution,
        plan_stage=stage,
        service_execution_info=service_execution_info,
        hosts=','.join(ips),
        status=1,
        tasks=json.dumps(tasks),
    )
    status = PLAN_STAGE_STATUS.SUCCESS
    try:
        ansible_run_result_callback = AnsibleRunResultCallBack(plan_stage_execution=plan_stage_execution)
        ansible_run(ips=ips, tasks=tasks, run_result=ansible_run_result_callback)
    except:
        status = PLAN_STAGE_STATUS.FAIL
        log_error()
    finally:
        plan_stage_execution.status = status
        plan_stage_execution.end_time = datetime.datetime.now()
        plan_stage_execution.save()


@shared_task
def run_stage(stage_id, execution_id, service_execution_info_id, commit_id=None):
    execution = PlanExecution.objects.get(id=execution_id)
    execution.start_time = datetime.datetime.now()
    try:
        start_stage(stage_id=stage_id, execution=execution,
                    service_execution_info_id=service_execution_info_id,
                    commit_id=commit_id)
    finally:
        execution.end_time = datetime.datetime.now()
        execution.save()


@shared_task
def run_plan(plan_id, execution_id, service_execution_info_type):
    plan = Plan.objects.get(id=plan_id)
    execution = PlanExecution.objects.get(id=execution_id)
    try:
        for stage in plan.planstage_set.order_by('order'):
            service_execution_info = ServiceExecutionInfo.objects.get(
                service=stage.service,
                type=service_execution_info_type
            )
            start_stage(stage.id, execution, service_execution_info.id)
    except:
        log_error()
    finally:
        execution.end_time = datetime.datetime.now()
        execution.save()


@shared_task
def run_grey_start(grey_id, execution_id):
    grey = Grey.objects.get(id=grey_id)
    execution = PlanExecution.objects.get(id=execution_id)
    execution.start_time = datetime.datetime.now()
    grey.status = GREY_STATUS.PROCESSING
    grey.save()

    grey_status = GREY_STATUS.SUCCESS
    try:
        # 保证所有要灰度的服务线上weight>0的机器数都大于等于2
        for service in grey.services.all():
            for slb in service.slbs.all():
                check_slb_num(slb)

        for service in grey.services.all():
            print("对{}执行灰度".format(service))
            execution.description += "对{}执行灰度 | ".format(service.name)
            execution.save()
            info = service.serviceexecutioninfo_set.get(type=SERVICE_RUNINFO_TYPE.GRAY)
            assert info.ecses.count() == 1
            ecs = info.ecses.first()

            tasks = []
            tasks += PullConfigTask(
                service=service,
            ).to_task()
            tasks += CopyFileTask(
                src=os.path.join(
                    settings.GM_CONFIG_PATH,
                    'systems/prod/static.dir/helios.dir/stage_static_route_table.json'
                ),
                dest='/etc/gm-config/storage/static.dir/helios.dir/static_route_table.json'
            ).to_task()
            tasks += RestartTask(service=service).to_task()
            plan_stage_execution = PlanStageExecution.objects.create(
                execution=execution,
                service_execution_info=info,
                hosts=ecs.ip,
                status=1,
                tasks=json.dumps(tasks),
            )

            status = PLAN_STAGE_STATUS.SUCCESS
            try:
                for slb in service.slbs.all():
                    is_success = True
                    try:
                        res = aliyun_slb.set_weight('cn-qingdao', slb.instance_id, ecs.instance_id, 0)
                        result_json = json.dumps(res)
                    except Exception as e:
                        is_success = False
                        result_json = json.dumps(repr(e))
                        raise
                    finally:
                        PlanStageExecutionSubTask.objects.create(
                            run_time=datetime.datetime.now(),
                            plan_stage_execution=plan_stage_execution,
                            is_success=is_success,
                            result_json=result_json,
                            host='aliyun',
                            description='[{}] 将 SLB({}) 中 ECS({}) 的权重改为0'.format(service.name, slb.name, ecs.name),
                        )

                ansible_run_result_callback = AnsibleRunResultCallBack(plan_stage_execution=plan_stage_execution)
                ansible_run(ips=[ecs.ip], tasks=tasks, run_result=ansible_run_result_callback)
            except:
                status = PLAN_STAGE_STATUS.FAIL
                raise
            finally:
                plan_stage_execution.status = status
                plan_stage_execution.end_time = datetime.datetime.now()
                plan_stage_execution.save()
    except Exception as e:
        grey_status = GREY_STATUS.FAIL
        log_error()
    finally:
        grey.status = grey_status
        grey.save()
        execution.end_time = datetime.datetime.now()
        execution.save()


@shared_task
def run_grey_reset(grey_id, execution_id):
    grey = Grey.objects.get(id=grey_id)
    grey.status = GREY_STATUS.RESETTING
    grey.save()

    grey_status = GREY_STATUS.NORMAL
    execution = PlanExecution.objects.get(id=execution_id)
    execution.start_time = datetime.datetime.now()
    execution.save()
    try:
        for service in grey.services.all():
            execution.description += "对{}执行灰度后的重置 | ".format(service.name)
            execution.save()
            info = service.serviceexecutioninfo_set.get(type=SERVICE_RUNINFO_TYPE.GRAY)
            assert info.ecses.count() == 1
            ecs = info.ecses.first()

            tasks = []
            tasks += PullConfigTask(
                service=service,
            ).to_task()
            tasks += CopyFileTask(
                src=os.path.join(
                    settings.GM_CONFIG_PATH,
                    'systems/prod/static.dir/helios.dir/static_route_table.json'
                ),
                dest='/etc/gm-config/storage/static.dir/helios.dir/static_route_table.json'
            ).to_task()
            tasks += RestartTask(service=service).to_task()
            plan_stage_execution = PlanStageExecution.objects.create(
                execution=execution,
                service_execution_info=info,
                hosts=ecs.ip,
                status=1,
                tasks=json.dumps(tasks),
            )
            status = PLAN_STAGE_STATUS.SUCCESS
            try:
                ansible_run_result_callback = AnsibleRunResultCallBack(plan_stage_execution=plan_stage_execution)
                ansible_run(ips=[ecs.ip], tasks=tasks, run_result=ansible_run_result_callback)
                for slb in service.slbs.all():
                    is_success = True
                    try:
                        res = aliyun_slb.set_weight('cn-qingdao', slb.instance_id, ecs.instance_id, 100)
                        result_json = json.dumps(res)
                    except Exception as e:
                        is_success = False
                        result_json = json.dumps(repr(e))
                        raise
                    finally:
                        PlanStageExecutionSubTask.objects.create(
                            run_time=datetime.datetime.now(),
                            plan_stage_execution=plan_stage_execution,
                            is_success=is_success,
                            result_json=result_json,
                            host='aliyun',
                            description='将 SLB({}) 中 ECS({}) 的权重改为 100'.format(slb.name, ecs.name),
                        )
            except:
                status = PLAN_STAGE_STATUS.FAIL
                raise
            finally:
                plan_stage_execution.status = status
                plan_stage_execution.end_time = datetime.datetime.now()
                plan_stage_execution.save()
    except:
        grey_status = GREY_STATUS.RESET_FAIL
        log_error()
    finally:
        grey.status = grey_status
        grey.save()
        execution.end_time = datetime.datetime.now()
        execution.save()
