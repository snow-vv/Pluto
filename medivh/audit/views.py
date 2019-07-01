from common.views import JsonView
from golive.models import PlanExecution
from common.utils.time import to_timestamp


# Create your views here.


class ExecutionView(JsonView):
    permissions = ['audit.executions']

    def get(self, request):
        page = int(request.GET.get('page', 1))
        num = int(request.GET.get('num', 20))
        executions = PlanExecution.objects.order_by('-id')
        total = executions.count()
        executions = executions[(page - 1) * num: page * num]
        return {
            'total': total,
            'list': [
                {
                    "id": execution.id,
                    "user": {
                        'id': execution.user.id,
                        "name": execution.user.last_name or execution.user.username,
                    },
                    "start_time": to_timestamp(execution.start_time),
                    "end_time": to_timestamp(execution.end_time),
                    "target": execution.target_text,
                } for execution in executions
                ]
        }
