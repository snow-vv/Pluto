# coding=utf-8
from django.conf.urls import url

from cmdb.views import ECSListApiView, ServiceListApiView, SLBDetailApiView, ECSSyncApiView, SLBChangeWeightApiView
from cmdb.views import UserListView, RDSSyncApiView

cmdb_apis = [
    url(r'^ecses$', ECSListApiView.as_view()),
    url(r'^ecses/sync$', ECSSyncApiView.as_view()),
    url(r'^rdses/sync$', RDSSyncApiView.as_view()),
    url(r'^services$', ServiceListApiView.as_view()),
    url(r'^slbs/(?P<slb_id>\d+)$', SLBDetailApiView.as_view()),
    url(r'^slbs/(?P<slb_id>\d+)/ecses/(?P<ecs_id>\d+)/change_weight$', SLBChangeWeightApiView.as_view()),

    url(r"^users$", UserListView.as_view()),
]
