# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from threading import Thread

from django.db import models
from django.http import JsonResponse
from django.contrib import messages
from django.forms.models import model_to_dict, construct_instance
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.module_loading import import_string
from django.utils.encoding import force_text
from django.views.generic.edit import CreateView, UpdateView
# Create your views here.

from idcops.models import User
from idcops.mixins import BaseRequiredMixin, PostRedirect
from idcops.lib.utils import make_dict, diff_dict, get_content_type_for_model
from idcops.lib.tasks import log_action, device_post_save


class NewModelView(BaseRequiredMixin, PermissionRequiredMixin,
                   PostRedirect, SuccessMessageMixin, CreateView):

    def get_template_names(self):
        prefix = self.model_name
        if self.request.is_ajax():
            return ["{0}/ajax_new.html".format(prefix), "base/ajax_new.html"]
        else:
            return ["{0}/new.html".format(prefix), "base/new.html"]

    def get_permission_required(self):
        self.permission_required = 'idcops.add_%s' % (self.model_name)
        return super(NewModelView, self).get_permission_required()

    def handle_no_permission(self):
        messages.error(self.request, "您没有新建 {0} 的权限.".format(
            self.model._meta.verbose_name))
        return super(NewModelView, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        self.success_message = "成功创建了 {} {}".format(
            self.verbose_name, self.object
        )
        return self.success_message

    def get_form_class(self):
        name = self.model_name.capitalize()
        try:
            form_class_path = "idcops.forms.{}NewForm".format(name)
            self.form_class = import_string(form_class_path)
        except BaseException:
            form_class_path = "idcops.forms.{}Form".format(name)
            self.form_class = import_string(form_class_path)
        return self.form_class

    def get_form_kwargs(self):
        kwargs = super(NewModelView, self).get_form_kwargs()
        params = self.request.GET.dict()
        mfields = [f.attname for f in self.opts.fields]
        for k in params.keys():
            if k in mfields:
                kwargs.update({k: params[k]})
        related_models = []
        for f in self.opts.get_fields():
            if isinstance(f, (models.ForeignKey, models.ManyToManyField)):
                if f.related_model:
                    related_models.append(f.related_model)
        if User in related_models:
            kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.creator = self.request.user
        if 'onidc' not in form.cleaned_data:
            form.instance.onidc = self.request.user.onidc
        response = super(NewModelView, self).form_valid(form)
        log_action(
            user_id=self.request.user.pk,
            content_type_id=get_content_type_for_model(self.object, True).pk,
            object_id=self.object.pk,
            action_flag="新增"
        )
        if self.model_name == 'online':
            verify = Thread(target=device_post_save, args=(self.object.pk,))
            verify.start()
        if self.request.is_ajax():
            data = {
                'message': "Successfully submitted form data.",
                'data': form.cleaned_data
            }
            return JsonResponse(data)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super(NewModelView, self).get_context_data(**kwargs)
        return context


class EditModelView(BaseRequiredMixin, PermissionRequiredMixin,
                    PostRedirect, SuccessMessageMixin, UpdateView):

    def get_template_names(self):
        prefix = self.model_name
        if self.request.is_ajax():
            return ["{0}/ajax_edit.html".format(prefix), "base/ajax_edit.html"]
        else:
            return ["{0}/edit.html".format(prefix), "base/edit.html"]

    def get_permission_required(self):
        self.permission_required = 'idcops.change_%s' % (self.model_name)
        return super(EditModelView, self).get_permission_required()

    def handle_no_permission(self):
        messages.error(self.request, "您没有修改 {0} 的权限.".format(
            self.model._meta.verbose_name))
        return super(EditModelView, self).handle_no_permission()

    def get_success_message(self, cleaned_data):
        self.success_message = '成功修改了 {0} "{1}"'.format(
            self.model._meta.verbose_name, force_text(self.object)
        )
        return self.success_message

    def get_object(self):
        return self.model.objects.get(pk=self.pk_url_kwarg)

    def get_form_class(self):
        name = self.model_name.capitalize()
        try:
            form_class_path = "idcops.forms.{}EditForm".format(name)
            self.form_class = import_string(form_class_path)
        except BaseException:
            form_class_path = "idcops.forms.{}Form".format(name)
            self.form_class = import_string(form_class_path)
        return self.form_class

    def get_form_kwargs(self):
        kwargs = super(EditModelView, self).get_form_kwargs()
        params = self.request.GET.dict()
        mfields = [f.attname for f in self.opts.fields]
        for k in params.keys():
            if k in mfields:
                kwargs.update({k: params[k]})
        related_models = []
        for f in self.opts.get_fields():
            if isinstance(f, (models.ForeignKey, models.ManyToManyField)):
                if f.related_model:
                    related_models.append(f.related_model)
        if User in related_models:
            kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.operator = self.request.user
        if 'onidc' not in form.cleaned_data:
            form.instance.onidc = self.request.user.onidc
        d1 = form.initial
        message = json.dumps(form.changed_data)
        response = super(EditModelView, self).form_valid(form)
        d2 = model_to_dict(construct_instance(form, self.object))
        diffs = diff_dict(make_dict(d1), make_dict(d2))
        content = json.dumps(diffs)
        log_action(
            user_id=self.request.user.pk,
            content_type_id=get_content_type_for_model(self.object, True).pk,
            object_id=self.object.pk,
            action_flag="修改", message=message, content=content
        )
        if self.model_name == 'online':
            verify = Thread(target=device_post_save, args=(self.object.pk,))
            verify.start()
        if self.request.is_ajax():
            data = {
                'message': "Successfully submitted form data.",
                'data': form.cleaned_data
            }
            return JsonResponse(data)
        else:
            return response
