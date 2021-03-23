# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import DetailView
from django.views.generic.edit import FormMixin
from django.utils.safestring import mark_safe
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.admin.utils import label_for_field, lookup_field

# Create your views here.

from idcops.lib.utils import (
    display_for_field, fields_for_model, can_change, get_actions
)
from idcops.forms import DetailNewCommentForm
from idcops.mixins import BaseRequiredMixin, PostRedirect


VISIBLE_XS_TR_FORMAT = '<tr class="visible-xs"><th>{th}</th><td>{td}</td></tr>'

HIDDEN_XS_TH_FORMAT = '''
<th class="hidden-xs">{th}</th>
<td class="hidden-xs">{td}</td></tr>
'''


class DetailModelView(
        BaseRequiredMixin,
        PostRedirect,
        SuccessMessageMixin,
        FormMixin,
        DetailView):

    form_class = DetailNewCommentForm

    def get_template_names(self):
        if self.request.is_ajax():
            return [
                "{0}/ajax_detail.html".format(self.model_name),
                "base/ajax_detail.html"
            ]
        else:
            return [
                "{0}/detail.html".format(self.model_name), "base/detail.html"]

    def get_success_message(self, cleaned_data):
        self.success_message = u'成功添加了{0} "{1}" 的备注信息'.format(
            self.opts.verbose_name, self.object)
        return self.success_message

    def get_object(self):
        return self.model.objects.get(pk=self.pk_url_kwarg)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    @property
    def make_info_panel(self):
        pin_fields = [
            'actived', 'deleted', 'created', 'creator',
            'modified', 'operator', 'onidc', 'mark'
        ]
        exclude = [
            'id', 'password', 'user_permissions',
            'onidc', 'actived', 'deleted', 'mark'
        ]
        base_fields = list(fields_for_model(self.model, exclude=exclude))
        new_pin_fields = [i for i in pin_fields if i in base_fields]
        fields = [
            f for f in base_fields if f not in new_pin_fields and f not in exclude
        ]
        fields.extend(new_pin_fields)
        default_fields = getattr(self.opts, 'list_display', None)
        if default_fields and isinstance(default_fields, list):
            o = [f for f in fields if f not in default_fields]
            default_fields.extend(o)
            fields = default_fields
        panel = ''
        for index, field_name in enumerate(fields, 1):
            tr_format = '<tr><th>{th}</th><td>{td}</td>'
            th = label_for_field(name=field_name, model=self.model)
            try:
                field = self.opts.get_field(field_name)
                value = field.value_from_object(self.object)
                td = display_for_field(value, field, only_date=False)
            except BaseException:
                try:
                    f, _, td = lookup_field(
                        field_name, self.object, self.model)
                except BaseException:
                    pass
            if (index % 2 == 0):
                append = VISIBLE_XS_TR_FORMAT
                _format = HIDDEN_XS_TH_FORMAT
                tr_format = _format + append
            tr_html = tr_format.format(th=th, td=td)
            panel += tr_html
        return mark_safe(panel)

    def get_context_data(self, **kwargs):
        context = super(DetailModelView, self).get_context_data(**kwargs)
        _extra = {
            'form': self.get_form(),
            'object_as_table': self.make_info_panel,
            'actions': get_actions(self.opts, self.request.user),
            'can_change': can_change(self.opts, self.request.user),
        }
        context.update(**_extra)
        return context

    def form_valid(self, form):
        form.instance.creator_id = self.request.user.pk
        form.instance.onidc_id = self.onidc_id
        form.instance.object_repr = self.object
        form.save()
        response = super(DetailModelView, self).form_valid(form)
        return response
