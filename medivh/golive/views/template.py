# -*- coding: UTF-8 -*-
import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from common.utils import to_dict
from golive.models import PlanTemplate, Plan


class TemplateListView(View):
    def get(self, request):
        data = {
            'plan_templates': PlanTemplate.objects.all(),
            'title': '上线申请模版',
        }
        return render(request, 'golive/template/list.html', data, )


class TemplateModifyView(View):
    def get(self, request, template_id=None):
        if template_id:
            template = PlanTemplate.objects.get(pk=template_id)
            data = {
                'template': template,
                'title': '编辑上线申请模版',
            }
        else:
            data = {
                'template': None,
                'title': '编辑上线申请模版',
            }
        return render(request, 'golive/template/modify.html', data)

    def post(self, request, template_id=None):
        data = json.loads(request.POST.get('data'))
        form_data = to_dict(data.get('form_data'))
        tasks = [to_dict(task) for task in data.get('tasks')]

        if template_id:
            template = PlanTemplate.objects.get(pk=template_id)
            template.name = form_data['name']

            template.tasks = json.dumps(tasks)
            template.save()
        else:
            template_data = dict(
                name=form_data['name'],
                creator=request.user,
                tasks=json.dumps(tasks),
            )

            template = PlanTemplate.objects.create(**template_data)

        if data['create']:
            plan_data = dict(
                name=template.name,
                creator=request.user,
                tasks=template.tasks,
            )
            plan = Plan.objects.create(**plan_data)
            return JsonResponse(data={
                'href': '/golive/plan/modify/{}/'.format(plan.id)
            })
        return JsonResponse(data={
            'href': '/golive/template/modify/{}/'.format(template.id)
        })
