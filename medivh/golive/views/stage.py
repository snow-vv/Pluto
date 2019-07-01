# -*- coding: UTF-8 -*-

from cmdb.models import ECS
from common.utils.time import to_timestamp
from common.views import JsonView
from golive.models import PlanStageExecutionSubTask


class StageHostExecutionsApiView(JsonView):
    def get(self, request, stage_id, host_id):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        host = ECS.objects.get(id=host_id)
        return {
            'results': [
                {
                    'execution_id': result.plan_stage_execution.execution_id,
                    'description': result.description,
                    'host_ip': result.host,
                    'is_success': result.is_success,
                    'result': result.result_json,
                    'run_time': to_timestamp(result.run_time),
                    'id': result.id
                }
                for result in
                PlanStageExecutionSubTask.objects.filter(
                    plan_stage_execution__plan_stage_id=stage_id,
                    host=host.ip
                )[(page - 1) * num:page * num]
                ]
        }
