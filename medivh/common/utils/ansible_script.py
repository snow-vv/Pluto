# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import json

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars import VariableManager
from django.conf import settings


class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def __init__(self, plan, *args, **kwargs):
        self.plan = plan
        super(ResultCallback, self).__init__(*args, **kwargs)

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


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


def run_tasks(ips, tasks):
    if not isinstance(ips, (list, tuple, set)):
        ips = [ips]
    options = Options()

    variable_manager = VariableManager()
    loader = DataLoader()
    passwords = dict(vault_pass='secret')

    # Instantiate our ResultCallback for handling results as they come in
    results_callback = ResultCallback()

    # create inventory and pass to var manager
    inventory = Inventory(loader=loader, variable_manager=variable_manager,
                          host_list=ips)
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
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()


def update(ips):
    tasks = [
        {
            u'become_user': u'gmuser',
            u'become': True,
            'git': {
                'dest': '/srv/apps/gaia',
                'force': 'yes',
                'repo': 'git@git.wanmeizhensuo.com:backend/gaia.git',
                'ssh_opts': '-o StrictHostKeyChecking=no'
            },
            u'name': u'Update Gaia Use Git'
        },
        {
            'pip': {
                'virtualenv': '/srv/envs/gaia',
                'requirements': '/srv/apps/gaia/requirements.txt',
                'extra_args': '-i http://mirrors.aliyun.com/pypi/simple/',
            },
            u'become': True,
            u'name': u'Pip Install Requirements',
            u'become_user': u'gmuser'
        },
        {
            u'name': u'Restart Gaia',
            'service': {
                'name': 'gaia',
                'state': 'restarted',
            }
        }
    ]
    run_tasks(ips, tasks)


def ufw_allow_from(server_ip, ip):
    tasks = [
        {
            u'raw': u'ufw allow from {}'.format(ip),
            u'name': u'Update Gaia Use Git'
        },
    ]
    run_tasks(server_ip, tasks)
