# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.http import urlencode
from idcops.models import Rack

register = template.Library()


@register.filter(name='addcss', is_safe=True)
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag(takes_context=True)
def get_query_string(context, **kwargs):
    params = context['request'].GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    if params:
        return '?%s' % urlencode(sorted(params.items()))
    else:
        return ''


@register.inclusion_tag('rack/overview.html')
def rack_overview(rack_id, obj_units):
    units = Rack.objects.get(pk=int(rack_id)).units.order_by('-name')
    return {'units': units, 'obj_units': obj_units}
