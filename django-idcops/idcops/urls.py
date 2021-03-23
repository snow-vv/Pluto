# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url, include, static
from idcops import views
from idcops.list import ListModelView, ConfigUserListView
from idcops.detail import DetailModelView
from idcops.edit import NewModelView, EditModelView

app_name = 'idcops'


accounts_urls = [
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^profile/', views.ProfileView.as_view(), name='profile'),
    url(r'^password_change/$', views.password_change, name='password_change'),
    url(r'^password_change/done/$', views.password_change_done,
        name='password_change_done'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done,
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.reset, name='password_reset_confirm'),
    url(r'^reset/done/$', views.reset_done, name='password_reset_complete'),
]


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^accounts/', include(accounts_urls)),
    url(r'^welcome/', views.welcome, name='welcome'),
    url(r'^switch_onidc/', views.switch_onidc, name='switch_onidc'),
    url(r'^list/zonemap/', views.ZonemapView.as_view(), name='zonemap'),
    url(r'^(?:new/(?P<model>\w+))/$', NewModelView.as_view(), name='new'),
    url(r'^(?:list/(?P<model>\w+))/$', ListModelView.as_view(), name='list'),
    url(r'^(?:config/(?P<model>\w+))/$',
        ConfigUserListView.as_view(), name='config'),
    url(r'^(?:config/list/(?P<model>\w+))/$',
        ConfigUserListView.as_view(), name='config_list'),
    url(r'^(?:detail/(?:(?P<model>\w+)-(?P<pk>\d+)))/$',
        DetailModelView.as_view(), name='detail'),
    url(r'^(?:update/(?:(?P<model>\w+)-(?P<pk>\d+)))/$',
        EditModelView.as_view(), name='update'),
    url(r'^upload/$',
        views.SummernoteUploadAttachment.as_view(), name='upload'),
    url(r'^import/(?P<model>\w+)/$',
        views.ImportExcelView.as_view(), name='import'),
]


if settings.DEBUG:
    urlpatterns += static.static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static.static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
