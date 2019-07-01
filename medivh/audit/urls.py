# -*- coding: UTF-8 -*-
from django.conf.urls import url

from audit.views import ExecutionView


audit_apis = [
    url(r'^executions$', ExecutionView.as_view()),
]
