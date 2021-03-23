# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import operator
from functools import reduce

from django.core.cache import cache, utils
from django.contrib import messages
from django.contrib.admin.utils import label_for_field
from django.db import models
# from django.db.models import fields
from django.http import HttpResponseRedirect
from django.utils import six
from django.utils.http import urlencode
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.urls import reverse_lazy

# Create your views here.

from idcops.mixins import BaseRequiredMixin, get_user_config
from idcops.models import Configure
from idcops.lib.utils import (
    can_create, nature_field_name,
    fields_for_model, make_tbody_tr,
    get_content_type_for_model, get_actions
)
from idcops.lib.fields import IPNetwork


_QUERY = 'search'
# _RANGE = 'range'
_ORDER = 'order'
_PAGINATE = 'paginate_by'
# _ALL_VAL = 'all'


class ListModelView(BaseRequiredMixin, ListView):

    """
    default_filter = {}
    list_display = ['__str__']
    list_display_links = ['first_column_field.']
    list_filter = ().
    list_select_related = True
    list_per_page = 20, user can config this value in range(10-50)
    list_max_show_all = 500
    config is by user configured or default.
    """

    def get_template_names(self):
        return ["{0}/list.html".format(self.model_name), "base/list.html"]

    @cached_property
    def _config(self):
        key = utils.make_template_fragment_key(
            "{}.{}.{}".format(self.request.user.id, self.model_name, 'list')
        )
        data = cache.get_or_set(
            key, get_user_config(self.request.user, 'list', self.model), 180
        )
        return data

    @property
    def list_only_date(self):
        try:
            config = self._config.get('list_only_date', 1)
            only_date = bool(int(config))
        except Exception:
            only_date = True
        return only_date

    @property
    def user_list_display(self):
        if self._config:
            return self._config.get('list_display', None)
        return None

    @property
    def model_list_display(self):
        fields = getattr(self.opts, 'list_display', '__all__')
        if fields and fields != '__all__':
            return fields
        return None

    @property
    def default_list_fields(self):
        exclude = ['id', 'password', 'system_pass', 'user_permissions']
        base_fields = list(fields_for_model(self.model, exclude=exclude))
        extra_fields = getattr(self.opts, 'extra_fields', None)
        if extra_fields and isinstance(extra_fields, list):
            base_fields.extend(extra_fields)
        return base_fields

    @property
    def display_link_field(self):
        return nature_field_name(self.model)

    @property
    def is_config(self):
        return self.request.GET.get('config', None)

    @property
    def get_list_fields(self):
        if self.user_list_display:
            fields = self.user_list_display
        elif self.model_list_display:
            fields = self.model_list_display
        else:
            fields = self.default_list_fields
        if not self.is_config:
            prefix_fields = ['field-first', 'field-second']
            fields = prefix_fields + fields
            fields.insert(len(fields), 'field-last')
        else:
            if fields == self.model_list_display:
                fields0 = [
                    f for f in self.default_list_fields if f not in fields]
                fields = fields + fields0
            else:
                return self.default_list_fields
        return fields

    def get_paginate_by(self, queryset):
        self.paginate_by = self.request.GET.get(_PAGINATE, 20)
        if int(self.paginate_by) > 100:
            messages.warning(
                self.request,
                "仅允许每页最多显示100条数据, 已为您显示100条."
            )
            self.paginate_by = 100
        return self.paginate_by

    @cached_property
    def get_params(self):
        self.params = dict(self.request.GET.items())
        return self.params

    def get_query_string(self, new_params=None, remove=None):
        new_params = {} if not new_params else new_params
        remove = [] if not remove else remove
        p = self.get_params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        if p:
            return '?%s' % urlencode(sorted(p.items()))
        else:
            return ''

    def get_ordering(self):
        ordering = list(self.opts.ordering or [])
        orders = self.request.GET.get(_ORDER, None)
        if orders:
            ordering = []
            for p in orders.split('.'):
                _, pfx, fname = p.rpartition('-')
                if fname.startswith('-') and pfx == "-":
                    ordering.append(fname[1:])
                else:
                    ordering.append(pfx + fname)
        pk_name = self.opts.pk.name
        if not (set(ordering) & {'pk', '-pk', pk_name, '-' + pk_name}):
            ordering.append('-pk')
        return ordering

    def get_filter_by(self):
        effective = {'deleted': False}
        _fields = dict((f.name, f.attname) for f in self.model._meta.fields)
        for item in _fields:
            if item in self.request.GET:
                effective[_fields[item]] = self.request.GET[item]
                if effective[_fields[item]] == 'all':
                    del effective[_fields[item]]
        return effective

    def apply_optimize_queryset(self, queryset):
        list_fields = self.get_list_fields
        _select = [f.name for f in self.opts.fields if (
            isinstance(f, models.ForeignKey) and f.name in list_fields)]
        _prefetch = [f.name for f in self.opts.many_to_many
                     if f.name in list_fields]
        _all = queryset.select_related(*_select).prefetch_related(*_prefetch)
        return _all

    def get_search_by(self):
        search_by = self.request.GET.get(_QUERY, None)
        return search_by.split(',') if search_by else None

    @property
    def allow_search_fields(self, exclude=None, include=None):
        opts = self.opts

        def construct_search(model):
            exclude = [f.name for f in opts.fields if getattr(f, 'choices')]
            fields = model._meta.fields
            _fields = []
            for f in fields:
                if isinstance(f, models.CharField) and f.name not in exclude:
                    _fields.append(f.name + '__icontains')
                if isinstance(f, IPNetwork):
                    _fields.append(f.name + '__icontains')
            return _fields

        if not exclude:
            exclude = ['onidc', 'slug', 'created', 'modified']
        exclude.extend([f.name for f in opts.fields if getattr(f, 'choices')])

        fields = construct_search(self.model)
        for f in opts.fields:
            if exclude and f.name in exclude:
                continue
            if isinstance(f, models.ForeignKey):
                submodel = f.related_model
                for sub in submodel._meta.fields:
                    if exclude and sub.name in exclude:
                        continue
                    if isinstance(
                            sub, models.CharField) and not getattr(
                            sub, 'choices'):
                        fields.append(f.name + '__' + sub.name + '__icontains')
            if isinstance(f, (models.CharField, models.TextField)):
                fields.append(f.name + '__icontains')
        return fields

    def get_queryset(self):
        queryset = super(ListModelView, self).get_queryset()
        search = self.get_search_by()
        effective = self.get_filter_by()
        ordering = self.get_ordering()
        if search and 'actived' in effective.keys():
            del effective['actived']
        _all = self.apply_optimize_queryset(queryset).filter(**effective)
        if hasattr(
                self.model,
                'onidc_id') and not self.request.user.is_superuser:
            _shared = _all.filter(mark='shared')
            _private = _all.filter(onidc_id=self.onidc_id)
            queryset = (_shared | _private).order_by(*ordering)
        else:
            queryset = _all.order_by(*ordering)
        if search:
            lst = []
            for q in search:
                q = q.strip()
                str = [models.Q(**{k: q}) for k in self.allow_search_fields]
                lst.extend(str)
            query_str = reduce(operator.or_, lst)
            queryset = _all.filter(query_str).order_by(*ordering)
        return queryset

    def make_paginate(self, max_size):
        request_size = int(self.paginate_by)
        if max_size <= request_size:
            return False
        else:
            min_size = 10
            max_size = max_size if max_size <= 100 else 100
            burst = len(str(max_size)) + 2
            rate = round(max_size / burst)
            ranges = [i for i in range(min_size, max_size, int(rate))]
            ranges.append(max_size)
            html = ''
            for p in ranges:
                url = self.get_query_string({'paginate_by': p})
                li = '<li><a href="{}">显示{}项</a></li>'.format(url, p)
                html += li
            return mark_safe(html)

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        mode = request.POST.get('mode')
        index = request.POST.getlist('index')
        objects = self.get_queryset().filter(pk__in=index)
        if mode == 'all':
            objects = self.get_queryset()
        redirect_to = reverse_lazy('idcops:list', args=[self.model_name])
        if not objects.exists():
            messages.warning(request, "您必须选中一些条目")
        else:
            try:
                current_action = import_string(
                    'idcops.actions.{}'.format(action))
                description = current_action.description
                metric = getattr(self.opts, 'metric', "条")
                mesg = format_html(
                    '您一共 <b>{0}</b> 了 <b>{1}</b> {2} <b>{3}</b>'.format(
                        description, objects.count(), metric,
                        self.opts.verbose_name
                    )
                )
                result = current_action(request, objects)
                # error has message.
                if isinstance(result, six.string_types):
                    messages.warning(request, result)
                    redirect_to = redirect_to + self.get_query_string()
                    return HttpResponseRedirect(redirect_to)
                elif result:
                    return result
                else:
                    messages.success(request, mesg)
                return HttpResponseRedirect(redirect_to)
            except Exception as e:
                messages.warning(request, "未知动作: {}".format(e))
        return HttpResponseRedirect(redirect_to)

    def make_thead(self):
        fields = self.get_list_fields
        ordering = [o for o in self.get_ordering() if o.rpartition('-')
                    [2] in fields]
        switch = {'asc': '', 'desc': '-'}
        checked_fields = self.user_list_display or self.model_list_display
        if not checked_fields:
            checked_fields = fields
        can_sorted_fields = [f.name for f in self.opts.concrete_fields]
        for _, field_name in enumerate(fields):
            checked = field_name in checked_fields
            sortable = field_name in can_sorted_fields
            if field_name == 'field-first':
                yield {
                    "text": mark_safe(
                        '''<input id="action-toggle"'''
                        '''name="mode" value="page" type="checkbox">'''
                    ),
                    "field": field_name,
                    "class_attrib": mark_safe(' class="no-print field-first"'),
                    "sortable": sortable,
                }
                continue
            if field_name == 'field-second':
                yield {
                    "text": "#",
                    "field": field_name,
                    "class_attrib": mark_safe(' class="field-second"'),
                    "sortable": sortable,
                }
            if field_name == 'field-last':
                yield {
                    "text": "操作",
                    "field": field_name,
                    "class_attrib": mark_safe(' class="no-print field-last"'),
                    "sortable": sortable,
                }
                continue
            try:
                text = label_for_field(name=field_name, model=self.model)
            except Exception:
                continue
            if field_name not in can_sorted_fields:
                # Not sortable
                yield {
                    "text": text,
                    "checked": checked,
                    "field": field_name,
                    "class_attrib": format_html(' class="col-{}"', field_name),
                    "sortable": sortable,
                }
                continue
            # OK, it is sortable if we got this far
            is_sorted = field_name in ordering or '-' + field_name in ordering
            sorted_key = 'asc' if is_sorted and field_name in ordering else 'desc'
            sorted_value = switch.get(sorted_key)
            new_ordering = [
                o for o in ordering if o != str(
                    sorted_value + field_name)]
            remove_link = '.'.join(i for i in new_ordering)
            new_sorted_key = 'desc' if is_sorted and field_name in ordering else 'asc'
            new_sorted_value = switch.get(new_sorted_key)
            new_ordering.insert(0, str(new_sorted_value + field_name))
            toggle_link = '.'.join(i for i in new_ordering)
            toggle_url = self.get_query_string({'order': toggle_link})
            remove_url = self.get_query_string({'order': remove_link})
            th_classes = ['sortable', 'col-{}'.format(field_name)]
            yield {
                "text": text,
                "checked": checked,
                "field": field_name,
                "sortable": sortable,
                "is_sorted": is_sorted,
                "sorted_key": sorted_key,
                "remove_link": "{}".format(remove_url),
                "toggle_link": "{}".format(toggle_url),
                "class_attrib": format_html(
                    'style="{}" class="{}"',
                    'min-width: 64px;' if is_sorted else '',
                    ' '.join(th_classes)) if th_classes else '',

            }

    def make_tbody(self, objects):
        extra_fields = ['field-first', 'field-second', 'field-last']
        fields = self.get_list_fields
        _only_date = self.list_only_date
        _verbose_name = self.verbose_name
        _model_name = self.model_name
        to_field_name = self.display_link_field
        for index, obj in enumerate(objects, 1):
            yield make_tbody_tr(
                self, obj, index, fields, extra_fields, _only_date,
                _verbose_name, _model_name, to_field_name
            )

    def get_context_data(self, **kwargs):
        context = super(ListModelView, self).get_context_data(**kwargs)
        objects = context.get('object_list')
        _extra = {
            'can_create': can_create(self.opts, self.request.user),
            'actions': get_actions(self.opts, self.request.user),
            'thead': self.make_thead(),
            'tbody': self.make_tbody(objects),
            'paginate': self.make_paginate(self.object_list.count())
        }
        context.update(**_extra)
        return context


class ConfigUserListView(BaseRequiredMixin, TemplateView):

    def get_template_names(self):
        return [
            "{0}/config_list.html".format(self.model_name),
            "base/config_list.html"
        ]

    def get_user_list_config(self):
        """
        获取用户当前的配置，如果没有则返回：None
        """
        data = get_user_config(self.request.user, 'list', self.model)
        return data

    def get_default_list_fields(self):
        """
        获取模型当前配置，如果没有配置则返回带扩展字段的所有字段
        """
        fields = getattr(self.opts, 'list_display', '__all__')
        if fields == '__all__':
            return self.get_model_all_fields()
        else:
            return fields

    def get_model_all_fields(self, exclude=None):
        """
        返回模型包含扩展字段的所有字段
        """
        if not exclude:
            exclude = ['id', 'password', 'system_pass', 'user_permissions']
        base_fields = list(fields_for_model(self.model, exclude=exclude))
        extra_fields = getattr(self.opts, 'extra_fields', None)
        if extra_fields and isinstance(extra_fields, list):
            base_fields.extend(extra_fields)
        return base_fields

    def make_fields_for_dict(self, fields):
        """
        根据fileds列表参数，返回列表字段
        data = [{
            'sort': 1, 'field_name': 'created',
            'verbose_name': '创建时间', 'selected': True
        }]
        """
        fields_for_dict = list()
        for field in fields:
            fields_for_dict.append(dict(
                name=field,
                verbose_name=label_for_field(field, self.model),
                )
            )
        return fields_for_dict

    def make_fields_metadata(self):
        """
        制作表头，返回字典
        """
        user_config = self.get_user_list_config()
        if not user_config:
            fields = self.get_default_list_fields()
            only_date = "1"
        else:
            fields = user_config.get('list_display')
            only_date = user_config.get('list_only_date')
        current_list_display = self.make_fields_for_dict(fields)
        model_all_fields_list = self.make_fields_for_dict(
            self.get_model_all_fields()
        )
        unused_list_fields = [
            f for f in model_all_fields_list if f not in current_list_display
        ]
        data = dict(
            only_date=only_date,
            current_list_display=current_list_display,
            model_all_fields_list=model_all_fields_list,
            unused_list_fields=unused_list_fields
        )
        return data

    def post(self, request, *args, **kwargs):
        key = utils.make_template_fragment_key(
            "{}.{}.{}".format(self.request.user.id, self.model_name, 'list')
        )
        cache.delete(key)
        data = request.POST.copy()
        clean_data = dict(
            list_display=data.getlist('list_display'),
            list_only_date=data.get('list_only_date', 1)
        )
        content = json.dumps(clean_data)
        config = Configure.objects.filter(
            content_type=get_content_type_for_model(self.model),
            onidc_id=self.onidc_id, creator=self.request.user, mark='list'
        ).order_by('-pk')
        if config.exists():
            config = config.update(content=content)
        else:
            config = Configure.objects.create(
                content_type=get_content_type_for_model(self.model),
                onidc_id=self.onidc_id, creator=self.request.user,
                mark='list', content=content
            )
        redirect_to = reverse_lazy('idcops:list', args=[self.model_name])
        messages.success(request, "您的{}自定义列表配置完成".format(self.verbose_name))
        return HttpResponseRedirect(redirect_to)

    def get_context_data(self, **kwargs):
        context = super(ConfigUserListView, self).get_context_data(**kwargs)
        _extra = {
            'fields_metadata': self.make_fields_metadata()
        }
        context.update(**_extra)
        return context
