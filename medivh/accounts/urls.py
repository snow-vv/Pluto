# -*- coding: UTF-8 -*-
from django.conf.urls import url

from accounts.views import LoginView, LogoutView, LoginApiView, LogoutApiView, ChangePasswordApiView

accounts_urls = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout')
]

accounts_apis = [
    url(r'^login$', LoginApiView.as_view(), name='login'),
    url(r'^logout$', LogoutApiView.as_view(), name='logout'),
    url(r'^change_password', ChangePasswordApiView.as_view(), name='change_password'),
]
