import json
import os

import six
from django.conf import settings

from golive.models import PROCESS_CONTROL_TYPE, Service

_task_name_to_class_map = {}


class BaseTaskMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = type.__new__(mcs, name, bases, namespace)
        name = cls.NAME or cls.__name__

        _task_name_to_class_map[name] = cls
        return cls


class BaseTask(six.with_metaclass(BaseTaskMeta)):
    NAME = None
    description = None

    def __init__(self, **kwargs):
        for k, v in six.iteritems(kwargs):
            setattr(self, k, v)

    def to_task(self):
        raise NotImplementedError

    def get_desc(self):
        if self.description:
            return self.description
        else:
            return self.__name__.lower()


class BaseServiceTask(BaseTask):
    NAME = None
    description = None

    def __init__(self, service, *args, **kwargs):
        super(BaseServiceTask, self).__init__(service=service, **kwargs)
        if not isinstance(service, Service):
            service = Service.objects.get(id=service)
        self.service = service

    def to_task(self):
        raise NotImplementedError

    def get_desc(self):
        if self.description:
            return self.description
        else:
            return self.__name__.lower()


class TextTask(BaseServiceTask):
    def __init__(self, text, **kwargs):
        super(TextTask, self).__init__(text=text, **kwargs)
        self.text = text


class CopyFileTask(BaseTask):
    def get_desc(self):
        return '复制文件 {} -> {}'.format(self.src, self.dest)

    def to_task(self):
        return [
            {
                'name': '复制文件 {} -> {}'.format(self.src, self.dest),
                'copy': {
                    'src': self.src,
                    'dest': self.dest,
                },
            }
        ]


class PullConfigTask(BaseServiceTask):
    description = '拉配置'

    def to_task(self):
        return [
            {
                'name': "git pull ops/config",
                'local_action': 'git',
                'args': {
                    'dest': settings.GM_CONFIG_PATH,
                    'force': 'yes',
                    'repo': settings.GM_CONFIG_REPO,
                    'ssh_opts': '-o StrictHostKeyChecking=no',
                },
                'run_once': True,
                # 'become': True,
                # 'become_user': 'gmuser',
            },
        ]


class DeployConfigTask(BaseServiceTask):
    description = '更改配置'

    def to_task(self):
        return PullConfigTask(service=self.service).to_task() + [
            {
                'name': 'Deploy {} config'.format(self.service.name),
                'copy': {
                    'src': os.path.join(settings.GM_CONFIG_PATH, self.service.git_repo.name,
                                        '{}/'.format(settings.ENV)),
                    'dest': self.service.app_dir,
                },
                'become': True,
                'become_user': 'gmuser',
            }
        ]


class GitPullTask(BaseServiceTask):
    description = '拉代码'

    def to_task(self):
        task = {
            'name': 'Update {} Use Git'.format(self.service.name),
            'become': True,
            'become_user': 'gmuser',
            'git': {
                'dest': self.service.app_dir,
                'force': 'yes',
                'repo': self.service.git_repo.repo,
                'ssh_opts': '-o StrictHostKeyChecking=no',
            },
        }
        # if hasattr(self, 'version') and self.version:
        #     task['git']['version'] = self.version
        return [task]


class GitVersionTask(BaseServiceTask):
    description = ' 获取分支当前所处版本'

    def to_task(self):
        task = {
            'name': 'Get {} branch version By Git'.format(self.service.name),
            'become': True,
            'become_user': 'gmuser',
            'raw': 'cd {} && git rev-parse HEAD'.format(self.service.app_dir)
        }

        return [task]


class GitRollbackTask(BaseServiceTask):
    description = '代码回滚'

    def to_task(self):
        task2 = {
            'name': 'Rollback {} Use Git'.format(self.service.name),
            'become': True,
            'become_user': 'gmuser',
            'raw': 'cd {} && git reset --hard {}'.format(
                self.service.app_dir,
                self.commit_id
            )
        }

        task1 = GitVersionTask(service=self.service).to_task()
        task3 = RestartTask(service=self.service).to_task()

        return task1 + [task2] + task3


class GitPullAndPipInstallTask(BaseServiceTask):
    description = '拉代码&&安装依赖'

    def to_task(self):
        tasks = []
        tasks += GitPullTask(host_group=self.host_group, service=self.service).to_task()
        tasks += PipInstallTask(host_group=self.host_group, service=self.service).to_task()
        return tasks


class PipInstallTask(BaseServiceTask):
    description = '安装依赖'

    def to_task(self):
        return [{
            'pip': {
                'virtualenv': self.service.virtualenv_dir,
                'requirements': os.path.join(self.service.app_dir, self.service.git_repo.requirements_path),
                'extra_args': '-i https://mirrors.aliyun.com/pypi/simple/',
            },
            u'become': True,
            u'name': u'Pip Install Requirements',
            u'become_user': u'gmuser'
        }]


class PipUpdateTask(BaseServiceTask):
    description = '升级pip'

    def to_task(self):
        return [{
            'pip': {
                'virtualenv': self.service.virtualenv_dir,
                'name': 'pip',
                'extra_args': '-U -i https://mirrors.aliyun.com/pypi/simple/',
            },
            u'become': True,
            u'name': u'Pip Install Requirements',
            u'become_user': u'gmuser'
        }]


class UpStarRestartTask(BaseServiceTask):
    description = '重启upstart服务'

    def to_task(self):
        return [{
            'name': u'Restart Service',
            'service': {
                'name': self.service.process_control_name,
                'state': 'reloaded',
            }
        }]


class SupervisorRestartTask(BaseServiceTask):
    description = '重启supervisor服务'

    def to_task(self):
        return [{
            'name': u'Restart Service',
            'raw': 'supervisorctl restart {}'.format(self.service.process_control_name),
        }]


class RestartTask(BaseServiceTask):
    description = '重启服务'

    def to_task(self):
        tasks = []
        if self.service.git_repo.check_command:
            tasks.append(ShellCommandTask(self.service, raw=self.service.git_repo.check_command).to_task())
        if self.service.process_control == PROCESS_CONTROL_TYPE.SUPERVISOR:
            tasks += SupervisorRestartTask(service=self.service).to_task()
        elif self.service.process_control == PROCESS_CONTROL_TYPE.UPSTART:
            tasks += UpStarRestartTask(service=self.service).to_task()
        else:
            raise NotImplementedError
        return tasks


class ShellCommandTask(BaseServiceTask):
    # 切换到项目目录，激活虚拟环境，执行shell命令
    def to_task(self):
        return [{
            'name': 'run shell command',
            'raw': "cd {}&&. {}&&{}".format(
                self.service.app_dir,
                os.path.join(self.service.virtualenv_dir, "bin/activate"),
                self.raw
            ),
            u'become': True,
            u'become_user': u'gmuser'
        }]


class DeployStaticTask(BaseServiceTask):
    def to_task(self):
        return [{
            'name': "Copy static files",
            'copy': {
                'src': self.service.static_dir,
                'dest': self.service.static_dir,
            },
            # 'become': True,
            # 'become_user': 'gmuser',
        },
        ]


class LocalCommandTask(BaseServiceTask):
    def get_desc(self):
        return "编译及执行shell脚本 {}".format(self.raw)

    def to_task(self):
        return [{
            'name': "Local command {}".format(self.raw),
            'local_action': 'raw',
            'args': {
                '_raw_params': "cd {}&&. {}&&{}".format(
                    self.service.app_dir,
                    os.path.join(self.service.virtualenv_dir, "bin/activate"),
                    self.raw
                ),
            },
            'run_once': True,
            'become': True,
            'become_user': 'gmuser',
        }, ]


class LocalGitPullTask(BaseServiceTask):
    def to_task(self):
        return [{
            'name': "更新{}代码".format(self.service.name),
            'local_action': 'git',
            'args': {
                'dest': self.service.app_dir,
                'force': 'yes',
                'repo': self.service.git_repo.repo,
                'ssh_opts': '-o StrictHostKeyChecking=no',
            },
            'run_once': True,
            'become': True,
            'become_user': 'gmuser',
        }, ]


class LocalPipInstallTask(BaseServiceTask):
    description = '编译及安装依赖'

    def to_task(self):
        return [{
            "local_action": 'pip',
            'args': {
                'virtualenv': self.service.virtualenv_dir,
                'requirements': os.path.join(self.service.app_dir, self.service.git_repo.requirements_path),
                'extra_args': '-i https://mirrors.aliyun.com/pypi/simple/',
            },
            u'become': True,
            u'name': u'Pip Install Requirements',
            u'become_user': u'gmuser',
            'run_once': True,
        }]


class LocalDeployConfig(BaseServiceTask):
    description = '编译及同步配置文件'

    def to_task(self):
        return [
            {
                'name': "git pull ops/config",
                'local_action': 'git',
                'args': {
                    'dest': settings.GM_CONFIG_PATH,
                    'force': 'yes',
                    'repo': settings.GM_CONFIG_REPO,
                    'ssh_opts': '-o StrictHostKeyChecking=no',
                },
                'run_once': True,
                # 'become': True,
                # 'become_user': 'gmuser',
            },
            {
                'name': 'Local Deploy {} config'.format(self.service.name),
                'local_action': 'copy',
                'args': {
                    'src': os.path.join(settings.GM_CONFIG_PATH, self.service.git_repo.name,
                                        '{}/'.format(settings.ENV)),
                    'dest': self.service.app_dir,
                },
                'become': True,
                'become_user': 'gmuser',
            }
        ]


class LocalVueBuildTask(BaseServiceTask):
    description = "Vue 编译"

    def __init__(self, service, **kwargs):
        assert service.static_dir
        super(LocalVueBuildTask, self).__init__(service=service, **kwargs)

    def to_task(self):
        return [
            {
                'name': "Vue Build",
                'local_action': 'raw',
                'args': {
                    '_raw_params': ". {}&&cd {}&&{npm_path} install&&{npm_path} run build".format(
                        settings.NVM_SH,
                        os.path.join(self.service.app_dir, 'fe'),
                        npm_path=settings.NPM_PATH,
                    ),
                },
                'run_once': True,
                'become': True,
                'become_user': 'gmuser',
            },
            {
                'name': "Copy Index.html",
                'copy': {
                    'src': os.path.join(self.service.app_dir, 'fe', 'dist', 'index.html'),
                    'dest': os.path.join(self.service.app_dir, 'templates'),
                },
                'become': True,
                'become_user': 'gmuser',
            },
            {
                'name': "Copy Vue Static",
                'copy': {
                    'src': os.path.join(self.service.app_dir, 'fe', 'dist', 'static/'),
                    'dest': self.service.static_dir,
                },
                'become': True,
                'become_user': 'gmuser',
            },
        ]


class DjangoCommandTask(BaseServiceTask):
    def to_task(self):
        run_once = getattr(self, 'run_once', True)
        return [{
            'name': self.get_desc(),
            'raw': 'cd {app_dir}&&{python_path} {manager_path} {command}'.format(
                app_dir=self.service.app_dir,
                python_path=os.path.join(self.service.virtualenv_dir, 'bin/python'),
                manager_path=self.service.git_repo.manage_path,
                command=self.command,
            ),
            u'become': True,
            u'become_user': u'gmuser',
            'run_once': bool(run_once),
        }]

    def get_desc(self):
        return '跑Django脚本: {}'.format(self.command)


class DeployLocalEnvTask(BaseServiceTask):
    description = "编译及部署环境(拉代码, 装依赖, 更新配置)"

    def to_task(self):
        t = []
        t += LocalGitPullTask(service=self.service).to_task()
        t += LocalPipInstallTask(service=self.service).to_task()
        t += LocalDeployConfig(service=self.service).to_task()
        return t


def get_ansible_task(task, service):
    cls = _task_name_to_class_map.get(task.function.name)
    return cls(service=service, **json.loads(task.params_json)).to_task()


def get_task(task, service):
    cls = _task_name_to_class_map.get(task.function.name)
    return cls(service=service, **json.loads(task.params_json))


def get_task_by_stage(stage):
    tasks = []
    service = stage.service
    for task in stage.tasks.order_by('order'):
        tasks.append(get_task(task=task, service=service))
    return tasks


def get_ansible_task_by_stage(stage):
    tasks = []
    for task in get_task_by_stage(stage):
        tasks.extend(task.to_task())
    return tasks