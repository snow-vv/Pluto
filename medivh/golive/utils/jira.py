# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from django.conf import settings

from common.utils.jira_tool import get_jira
from common.logger import log_error
from golive.runner.ansible.tasks import get_task_by_stage


def create_or_update_issue_by_plan(plan):
    if not plan.jira_id:
        try:
            description = '申请人: {}\n'.format(plan.creator.username)
            description += '期望上线时间: {}\n'.format(plan.golive_expected_time)
            for stage in plan.planstage_set.order_by('order'):
                description += "h2.{}\n".format(stage.service.name)
                for task in get_task_by_stage(stage):
                    description += "* {}\n".format(task.get_desc())

            description += '\n备注: {}\n'.format(plan.notes)
            description += "url: http://{}/#/executions/{}".format(settings.HOST, plan.id)
            issue_dict = {
                'project': {'key': settings.JIRA_GOLIVE_PROJECT},
                'summary': plan.description,
                'description': description,
                'issuetype': {'name': 'Task'},
                'customfield_10304': {"id": "10100"},
                'customfield_10301': {'name': settings.JIRA_USR},
            }
            new_issue = get_jira().create_issue(fields=issue_dict)
            plan.jira_id = new_issue.id
        except:
            log_error()
