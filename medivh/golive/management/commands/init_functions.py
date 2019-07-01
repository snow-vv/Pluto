# -*- coding: UTF-8 -*-
import json

from django.core.management import BaseCommand
from golive.models import Function, Plan, Task, Service, PlanStage


class Command(BaseCommand):
    def handle(self, *args, **options):
        functions = [
            {'id': 1, 'name': 'GitPullTask'},
            {'id': 2, 'name': 'DeployConfigTask'},
            {'id': 3, 'name': 'PipInstallTask'},
            {'id': 4, 'name': 'RestartTask'},
            {'id': 5, 'name': 'DjangoCommandTask'},
            {'id': 6, 'name': 'ShellCommandTask'},
            {'id': 7, 'name': 'LocalVueBuildTask'},
            {'id': 8, 'name': 'SupervisorRestartTask'},
            {'id': 9, 'name': 'CopyFileTask'},
            {'id': 10, 'name': 'GitPullAndPipInstallTask'},
            {'id': 11, 'name': 'LocalGitPullTask'},
            {'id': 12, 'name': 'DeployLocalEnvTask'},
            {'id': 13, 'name': 'BaseTask'},
            {'id': 14, 'name': 'LocalCommandTask'},
            {'id': 15, 'name': 'LocalDeployConfig'},
            {'id': 16, 'name': 'TextTask'},
            {'id': 17, 'name': 'DeployStaticTask'},
            {'id': 18, 'name': 'LocalPipInstallTask'},
            {'id': 19, 'name': 'BaseServiceTask'},
            {'id': 20, 'name': 'UpStarRestartTask'},
            {'id': 21, 'name': 'PipUpdateTask'},
            {'id': 22, 'name': 'GitRollbackTask'}
        ]
        for f in functions:
            Function.objects.get_or_create(**f)
