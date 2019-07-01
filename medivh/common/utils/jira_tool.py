# -*- coding: UTF-8 -*-


from django.conf import settings
from jira import JIRA

__gm_jira = None


def get_jira():
    global __gm_jira
    if __gm_jira is None:
        __gm_jira = JIRA('http://jira.gengmei.cc/', basic_auth=(settings.JIRA_USR, settings.JIRA_PWD))
    return __gm_jira
