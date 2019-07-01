# coding=utf-8
from django.conf.urls import url

from permission.views import GroupDetailView, GroupListView, PermissionView

permission_apis = [
    url(r'^list$', PermissionView.as_view()),
    url(r'^groups$', GroupListView.as_view()),
    url(r'^groups/(?P<group_id>\d+)$', GroupDetailView.as_view()),
    url(r'^groups/create$', GroupDetailView.as_view()),
]
