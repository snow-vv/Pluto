# coding=utf-8
from django.conf.urls import url

from shield.views import IpBlackListApiView, AddBlackIPApiView, DeleteBlackIPApiView

shield_apis = [
    url(r'^blackips$', IpBlackListApiView.as_view(), name='list'),
    url(r'^(?P<ip>(\d|\.)*)/del', DeleteBlackIPApiView.as_view(), name='delete_black_ip'),
    url(r'^(?P<ip>(\d|\.)*)/add', AddBlackIPApiView.as_view(), name='add_black_ip'),
]
