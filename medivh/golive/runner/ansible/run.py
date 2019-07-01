# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import datetime
import json

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars import VariableManager
from django.conf import settings

from golive.models import PlanStageExecutionSubTask
from golive.utils.notify import action_notify
from golive.runner.resultcallback import RunResultCallBack


class AnsibleRunResultCallBack(RunResultCallBack):
    def __init__(self, plan_stage_execution):
        self.plan_stage_execution = plan_stage_execution

    def on_task_finish(self, result, **kwargs):
        if 'failed' in result._result or 'unreachable' in result._result:
            is_success = False
        else:
            is_success = True
        PlanStageExecutionSubTask.objects.create(
            run_time=datetime.datetime.now(),
            plan_stage_execution=self.plan_stage_execution,
            is_success=is_success,
            result_json=json.dumps(result._result),
            host=result._host,
            description=str(result._task),
        )
        host = result._host
        req = {host.name: result._result}
        action_notify(req, self.plan_stage_execution)


class ResultCallback(CallbackBase):
    def __init__(self, run_result, *args, **kwargs):
        self.__run_result = run_result
        super(ResultCallback, self).__init__(*args, **kwargs)

    def v2_runner_on_ok(self, result, **kwargs):
        self.__run_result.on_task_finish(result=result, **kwargs)

        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_unreachable = v2_runner_on_ok


class Options(object):
    ask_pass = False
    ask_su_pass = False
    ask_sudo_pass = False
    ask_vault_pass = False
    become = False
    become_ask_pass = False
    become_method = 'sudo'
    become_user = 'root'
    check = False
    connection = 'smart'
    diff = False
    extra_vars = []
    forks = 5
    inventory = '/Users/Zyy/gengmei/MalGanis/hosts'
    listhosts = None
    module_args = ''
    module_name = 'uping'
    module_path = None
    new_vault_password_file = None
    one_line = None
    output_file = None
    poll_interval = 15
    private_key_file = settings.PRIVATE_KEY_FILE
    remote_user = 'root'
    scp_extra_args = ''
    seconds = 0
    sftp_extra_args = ''
    ssh_common_args = ''
    ssh_extra_args = ''
    su = False
    su_user = None
    subset = None
    sudo = False
    sudo_user = None
    syntax = None
    timeout = 10
    tree = None
    vault_password_file = None
    verbosity = 0


def ansible_run(ips, tasks, run_result):
    ips = ips
    passwords = dict(vault_pass='secret')

    options = Options()
    variable_manager = VariableManager()
    loader = DataLoader()
    results_callback = ResultCallback(run_result=run_result)
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=ips)

    variable_manager.set_inventory(inventory)

    play_source = {
        'gather_facts': 'no',
        'tasks': tasks,
        'hosts': ips,
        'name': 'Ansible Ad-Hoc'
    }

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )
        tqm.run(play)
        if tqm._failed_hosts:
            raise Exception(tqm._failed_hosts)
        if tqm._unreachable_hosts:
            raise Exception(tqm._unreachable_hosts)
    finally:
        if tqm is not None:
            tqm.cleanup()
