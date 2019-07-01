import json

from django.contrib.auth.models import User
from django.db import models

from cmdb.models import ECS, SLB
from common.utils.enum import Enum


class PLAN_STATUS(Enum):
    EDITING = 1, '正在编辑'
    AUDIT_PASS = 3, '待上线'
    GOLIVING = 4, '正在上线'
    GOLIVED = 5, '已上线'
    FAILED = 6, '上线失败'


class PROCESS_CONTROL_TYPE(Enum):
    UPSTART = 1, 'upstart'
    SUPERVISOR = 2, 'supervisor'


class EXECUTION_STAGE_RESULT(Enum):
    SUCCESS = 1, '成功'
    FAIL = 2, '失败'
    FINISH = 3, '整个Task执行完毕标识'


class SERVICE_RUNINFO_TYPE(Enum):
    GRAY = 1, '灰度模式'
    REST = 2, 'REST模式'
    ALL = 3, 'ALL模式'


class PLAN_STAGE_STATUS(Enum):
    PROCESSING = 1, '执行中'
    SUCCESS = 2, '成功'
    FAIL = 3, '失败'


class GREY_STATUS(Enum):
    NORMAL = 0, '正常'
    PROCESSING = 1, '正在执行'
    SUCCESS = 2, '执行成功'
    FAIL = 3, '执行失败'
    RESETTING = 4, '重置中'
    RESET_FAIL = 5, '重置失败'


class Function(models.Model):
    name = models.CharField(max_length=100)


class Task(models.Model):
    function = models.ForeignKey(Function)
    params_json = models.TextField(max_length=100)
    order = models.IntegerField()


class GitRepo(models.Model):
    name = models.CharField(max_length=100)
    repo = models.CharField(max_length=100)
    requirements_path = models.CharField('依赖文件在git repo下面的相对路径', max_length=100, default='requirements.txt')
    manage_path = models.CharField('依赖文件在git repo下面的相对路径', max_length=100, default='manage.py')
    check_command = models.CharField('checker脚本命令', max_length=300, default='')

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    app_dir = models.CharField(max_length=100)
    static_dir = models.CharField(max_length=100, null=True, blank=True)
    virtualenv_dir = models.CharField(max_length=100)
    process_control = models.IntegerField(choices=PROCESS_CONTROL_TYPE)
    process_control_name = models.CharField(max_length=100)
    git_repo = models.ForeignKey(GitRepo)
    ecses = models.ManyToManyField(ECS, related_name='services', blank=True)
    slbs = models.ManyToManyField(SLB, blank=True, null=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class ServiceExecutionInfo(models.Model):
    class Meta:
        unique_together = ('service', 'type')

    service = models.ForeignKey(Service)
    type = models.IntegerField(choices=SERVICE_RUNINFO_TYPE)
    ecses = models.ManyToManyField(ECS, related_name='service_execution_infos')

    def __repr__(self):
        return "{} {}".format(self.service.name, SERVICE_RUNINFO_TYPE.getDesc(self.type))

    def __str__(self):
        return "{} {}".format(self.service.name, SERVICE_RUNINFO_TYPE.getDesc(self.type))


class Plan(models.Model):
    description = models.CharField(max_length=100)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    golive_expected_time = models.DateTimeField('预计上线时间', null=True, auto_now_add=True)
    tasks = models.TextField('json序列化的task')
    creator = models.ForeignKey(User, verbose_name='创建者')
    assignee = models.ForeignKey(User, related_name='assigned_plans', null=True)
    status = models.IntegerField(choices=PLAN_STATUS, default=PLAN_STATUS.EDITING)
    jira_id = models.CharField(max_length=30, verbose_name="JIRA ISSUE ID", null=True)
    notes = models.TextField('备注')

    def __repr__(self):
        return self.description

    def __str__(self):
        return self.description


class PlanStage(models.Model):
    plan = models.ForeignKey(Plan)
    service = models.ForeignKey(Service)
    tasks = models.ManyToManyField(Task)
    order = models.IntegerField()


class PlanTemplate(models.Model):
    name = models.CharField(max_length=100)
    tasks = models.TextField('json序列化的task')
    creator = models.ForeignKey(User, verbose_name='创建者')
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('最后更改时间', auto_now=True)


class PlanStatusChangeLog(models.Model):
    plan = models.ForeignKey(Plan)
    user = models.ForeignKey(User, null=True)
    source_status = models.IntegerField(verbose_name='原状态', choices=PLAN_STATUS)
    target_status = models.IntegerField(verbose_name='目标状态', choices=PLAN_STATUS)
    action_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')


class PlanExecution(models.Model):
    plan = models.ForeignKey(Plan, null=True)
    user = models.ForeignKey(User, verbose_name='操作人')
    start_time = models.DateTimeField(null=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, verbose_name='结束时间')
    description = models.CharField(max_length=500, default='')

    @property
    def target_text(self):
        if self.plan:
            return "PLAN({}): {}".format(self.plan.id, self.plan.description)
        else:
            return self.description


class PlanStageExecution(models.Model):
    execution = models.ForeignKey(PlanExecution)
    plan_stage = models.ForeignKey(PlanStage, null=True)
    service_execution_info = models.ForeignKey(ServiceExecutionInfo)
    hosts = models.TextField()
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    status = models.IntegerField(choices=PLAN_STAGE_STATUS, default=PLAN_STAGE_STATUS.PROCESSING)
    tasks = models.TextField('JSON序列化的TASK')


class PlanStageExecutionSubTask(models.Model):
    run_time = models.DateTimeField(auto_now_add=True)
    plan_stage_execution = models.ForeignKey(PlanStageExecution, related_name='subtasks')
    is_success = models.BooleanField()
    result_json = models.TextField()
    description = models.CharField(max_length=500, default='')
    host = models.CharField(max_length=100)


class Grey(models.Model):
    name = models.CharField(max_length=30)
    route_path = models.CharField(verbose_name='路由表路径', max_length=300)
    ecses = models.ManyToManyField(ECS, blank=True)
    services = models.ManyToManyField(Service, blank=True)
    description = models.TextField()
    executions = models.ManyToManyField(PlanExecution, blank=True)
    status = models.IntegerField(choices=GREY_STATUS, default=GREY_STATUS.NORMAL)

    def __str__(self):
        return '{}: {}'.format(self.name, self.services.all())


class ServiceCommitRecords(models.Model):
    """记录服务对应上线成功的commit_id,便于回滚操作"""

    commit_id = models.CharField(verbose_name='记录对应服务上线成功的commit_id', max_length=64)
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    plan = models.ForeignKey(Plan)
    service = models.ForeignKey(Service)


class DtabRules(models.Model):
    """预设路由规则示例"""
    name = models.CharField(max_length=100)
    rule = models.TextField()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
