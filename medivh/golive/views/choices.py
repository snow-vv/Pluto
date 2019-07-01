# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from golive.models import Service


class ChoiceView(View):
    model = None
    text_field = 'name'

    def get(self, request):
        q = request.GET.get('q', '')
        page = int(request.GET.get('page', '1'))
        num = int(request.GET.get('num', 30))
        initial = request.GET.get('initial', None)

        if initial is not None:
            initial = initial.split(',')
            qry = Q(id__in=initial)

        else:
            qry = Q(id__contains=q) | Q(**{'{}__contains'.format(self.text_field): q})
        query = self.model.objects.filter(qry).order_by('id')
        total_count = query.count()
        start_pos = (page - 1) * num
        start_pos = start_pos if start_pos >= 0 else 0
        results = [
            {
                'id': obj.id,
                'text': getattr(obj, self.text_field),
            } for obj in query[start_pos: start_pos + num]
            ]
        return JsonResponse({'total_count': total_count, 'results': results, 'page': page, 'num': num})


class ServiceChoiceView(ChoiceView):
    model = Service


class UserChoiceView(ChoiceView):
    model = User
    text_field = 'username'
