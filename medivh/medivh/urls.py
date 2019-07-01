"""medivh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from accounts.urls import accounts_apis
from accounts.views import index
from audit.urls import audit_apis
from cmdb.urls import cmdb_apis
from golive.urls import golive_apis
from permission.urls import permission_apis
from service.urls import service_apis
from shield.urls import shield_apis

api_urls = [
    url(r'audit/', include(audit_apis)),
    url(r'accounts/', include(accounts_apis, namespace='accounts')),
    url(r'golive/', include(golive_apis, namespace='golive')),
    url(r'cmdb/', include(cmdb_apis)),
    url(r'shield/', include(shield_apis)),
    url(r'service/', include(service_apis)),
    url(r'permission/', include(permission_apis)),
]
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index),
    url(r'^api/', include(api_urls, namespace='api')),
]
