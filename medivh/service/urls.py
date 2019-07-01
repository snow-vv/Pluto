# coding=utf-8
from django.conf.urls import url

from service.views import ServiceRelationApiView

service_apis = [
    url(r'^relation$', ServiceRelationApiView.as_view(), name='list'),
]
