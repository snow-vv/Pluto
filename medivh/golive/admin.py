from django.contrib import admin

from golive.models import *
from golive.forms import ServiceForm, ServiceExecutionInfoForm
from cmdb.models import ECS

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceForm


class ServiceExecutionInfoAdmin(admin.ModelAdmin):
    form = ServiceExecutionInfoForm


admin.site.register(Plan)
admin.site.register(GitRepo)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceExecutionInfo, ServiceExecutionInfoAdmin)
admin.site.register(DtabRules)
admin.site.register(ECS)
