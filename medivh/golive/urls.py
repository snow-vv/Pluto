# coding=utf-8
from django.conf.urls import url

from golive.views.plan import PlanListApiView, PlanDetailApiView, ServiceListApiView, RunPlanApiView, RunStageApiView, \
    GreyServiceListApiView
from golive.views.stage import StageHostExecutionsApiView
from golive.views.plan import PlanExecutionApiView, ExecutionsResultApiView, PlanStageHostApiView, ReleaseDoneApiView, \
    ServiceCommitView, RunStageRollbackView
from golive.views.grey import GreyListApiView, GreyStartApiView, GreyResetApiView, ConfirmGreyApiView, ConfirmResetApiView, \
    GreyRuleApiView, DtabRulesExamplesApiView

golive_urls = [
]

golive_apis = [
    url(r'^plans$', PlanListApiView.as_view()),
    url(r'^plans/(?P<plan_id>\d+)$', PlanDetailApiView.as_view()),
    url(r'^plans/(?P<plan_id>\d+)/done$', ReleaseDoneApiView.as_view()),
    url(r'^plans/(?P<plan_id>\d+)/executions$', PlanExecutionApiView.as_view()),
    url(r'^plans/create$', PlanDetailApiView.as_view()),

    url(r'^services$', ServiceListApiView.as_view()),
    url(r'^grey_services$', GreyServiceListApiView.as_view()),
    url(r'^stages/(?P<stage_id>\d+)/hosts/(?P<host_id>\w+)/executions$', StageHostExecutionsApiView.as_view()),
    url(r'^stages/(?P<stage_id>\d+)/hosts$', PlanStageHostApiView.as_view()),

    url(r'^stages/(?P<stage_id>\d+)/run/(?P<execution_info_id>\w+)$', RunStageApiView.as_view()),
    url(r'^stages/(?P<stage_id>\d+)/rollback', RunStageRollbackView.as_view()),
    url(r'^plans/(?P<plan_id>\d+)/run/(?P<run_type>\w+)$', RunPlanApiView.as_view()),

    url(r'^executions/(?P<execution_id>\d+)$', ExecutionsResultApiView.as_view()),

    url(r'^greys$', GreyListApiView.as_view()),
    url(r'^greys/(?P<grey_id>\d+)/confirm$', ConfirmGreyApiView.as_view()),
    url(r'^greys/(?P<grey_id>\d+)/confirm_reset', ConfirmResetApiView.as_view()),
    url(r'^greys/(?P<grey_id>\d+)/start$', GreyStartApiView.as_view()),
    url(r'^greys/(?P<grey_id>\d+)/reset$', GreyResetApiView.as_view()),
    url(r'^grey_rule$', GreyRuleApiView.as_view()),
    url(r'^dtabrules_example$', DtabRulesExamplesApiView.as_view()),

    url(r'^service/commits', ServiceCommitView.as_view())
]
