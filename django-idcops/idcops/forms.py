# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools

from django import forms
from django.db.models import Max
from django.utils.six import text_type
from django.utils.html import format_html
from django.utils.text import get_text_list
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from idcops.models import (
    Option, Rack, Comment, User, Client, Device,
    Idc, Testapply, Goods, Inventory, Jumpline,
    Document, Configure, Rextend, Unit, Pdu, Zonemap,
    Network, IPAddress
)
from idcops.lib.utils import can_create, shared_queryset


STATIC_PREFIX = getattr(settings, 'STATIC_URL', '/static/')

SITE_PREFIX = getattr(settings, 'SITE_PREFIX', '')

MIME_ACCEPT = '''
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,
application/vnd.ms-excel,
'''


class CalendarMedia(object):
    class Media:
        extend = True
        css = {
            'all': (
                '{}idcops/css/daterangepicker.min.css'.format(STATIC_PREFIX),
            )
        }

        js = (
            '{}idcops/js/moment.min.js'.format(STATIC_PREFIX),
            '{}idcops/js/daterangepicker.min.js'.format(STATIC_PREFIX),
        )


class Select2Media(object):
    class Media:
        css = {
            'all': (
                '{}idcops/css/select2.min.css'.format(STATIC_PREFIX),
            )
        }

        js = (
            '{}idcops/js/select2.min.js'.format(STATIC_PREFIX),
            '{}idcops/js/i18n/zh-CN.js'.format(STATIC_PREFIX),
        )


class CheckUniqueTogether(forms.ModelForm):

    def get_unique_together(self):
        unique_together = self.instance._meta.unique_together
        for field_set in unique_together:
            return field_set
        return None

    def clean(self):
        # self.validate_unique()
        cleaned_data = super(CheckUniqueTogether, self).clean()
        unique_fields = self.get_unique_together()
        if isinstance(unique_fields, (list, tuple)):
            unique_filter = {}
            instance = self.instance
            model_name = instance._meta.verbose_name
            for unique_field in unique_fields:
                field = instance._meta.get_field(unique_field)
                if field.editable and unique_field in self.fields:
                    unique_filter[unique_field] = cleaned_data.get(
                        unique_field)
                else:
                    unique_filter[unique_field] = getattr(
                        instance, unique_field)
            for k, v in unique_filter.items():
                if not v:
                    return
            existing_instances = type(instance).objects.filter(
                **unique_filter).exclude(pk=instance.pk)
            if existing_instances:
                field_labels = [
                    instance._meta.get_field(f).verbose_name
                    for f in unique_fields
                ]
                field_labels = text_type(get_text_list(field_labels, _('and')))
                msg = _("%(model_name)s with this %(field_labels)s already exists.") % {
                    'model_name': model_name, 'field_labels': field_labels, }
                for unique_field in unique_fields:
                    if unique_field in self.fields:
                        self.add_error(unique_field, msg)


class FormBaseMixin(Select2Media, CheckUniqueTogether):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FormBaseMixin, self).__init__(*args, **kwargs)
        if 'mark' in self.fields:
            self.fields['mark'].widget = forms.HiddenInput()
        if self.user is not None:
            onidc_id = self.user.onidc_id
            effective = {
                'onidc_id': onidc_id,
                'deleted': False,
                'actived': True}
            for field_name in self.fields:
                field = self.fields.get(field_name)
                if isinstance(
                        field,
                        (forms.fields.SlugField,
                         forms.fields.CharField)):
                    self.fields[field_name].widget.attrs.update(
                        {'autocomplete': "off"})
                if isinstance(field, forms.fields.DateTimeField):
                    self.fields[field_name].widget.attrs.update(
                        {'data-datetime': "true"})
                if isinstance(field.widget, forms.widgets.Textarea):
                    self.fields[field_name].widget.attrs.update({'rows': "3"})
                if isinstance(field, (
                        forms.models.ModelChoiceField,
                        forms.models.ModelMultipleChoiceField)):
                    fl = ''
                    if getattr(field.queryset.model, 'mark', False):
                        field.queryset = shared_queryset(
                            field.queryset, onidc_id)
                        if field.queryset.model is Option:
                            _prefix = self._meta.model._meta.model_name
                            _postfix = field_name.capitalize()
                            flag = _prefix.capitalize() + '-' + _postfix
                            fl = flag
                            field_initial = field.queryset.filter(
                                master=True, flag=flag)
                            if field_initial.exists():
                                field.initial = field_initial.first()
                    else:
                        field.queryset = field.queryset.filter(**effective)
                    mn = field.queryset.model._meta
                    if can_create(mn, self.user) and fl:
                        fk_url = format_html(
                            ''' <a title="点击添加一个 {}"'''
                            ''' href="{}new/{}/?flag={}">'''
                            '''<i class="fa fa-plus"></i></a>'''.format(
                                field.label, SITE_PREFIX, mn.model_name, fl))
                    elif can_create(mn, self.user) and not fl:
                        fk_url = format_html(
                            ''' <a title="点击添加一个 {}"'''
                            ''' href="{}new/{}">'''
                            '''<i class="fa fa-plus"></i></a>'''.format(
                                field.label, SITE_PREFIX, mn.model_name))
                    else:
                        fk_url = ''
                    field.help_text = field.help_text + fk_url
                self.fields[field_name].widget.attrs.update(
                    {'class': "form-control"})


class UserNewForm(Select2Media, UserCreationForm):
    class Meta(FormBaseMixin, UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "email",
            "mobile",
            "groups",
            "slaveidc")

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super(UserNewForm, self).__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
                {'autofocus': True})
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'autocomplete': "off", 'class': "form-control"})
        if not self.user.is_superuser:
            self.fields['slaveidc'].queryset = self.user.slaveidc.all()
            self.fields['groups'].queryset = self.user.groups.all()


class UserEditForm(Select2Media, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "email",
            "mobile",
            "upper",
            "onidc",
            "groups",
            "slaveidc",
            'user_permissions'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserEditForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'autocomplete': "off", 'class': "form-control"
            })
        if self.user and not self.user.is_superuser:
            self.fields['onidc'].queryset = self.user.slaveidc.all()
            self.fields['slaveidc'].queryset = self.user.slaveidc.all()
            self.fields['groups'].queryset = self.user.groups.all()
            self.fields['upper'].queryset = self._meta.model.objects.filter(
                upper=self.user)
            self.fields['user_permissions'].queryset = \
                self.user.user_permissions.all()


class OptionForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Option
        fields = [
            'flag',
            'text',
            'description',
            'master',
            'color',
            'parent',
            'mark']

    def __init__(self, *args, **kwargs):
        self.flag = kwargs.pop('flag', None)
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields['flag'].choices = self._meta.model().choices_to_field
        if self.flag:
            self.fields['flag'].initial = self.flag


class IdcForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Idc
        fields = [
            'name', 'desc', 'codename', 'emailgroup',
            'managers', 'address', 'duty', 'tel'
        ]

    def __init__(self, *args, **kwargs):
        super(IdcForm, self).__init__(*args, **kwargs)
        if self.user and self.user.is_superuser:
            self.fields['managers'].queryset = User.objects.filter(
                actived=True, is_active=True
            )


class ClientForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'style', 'sales', 'kf', 'tags']


class RackNewForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Rack
        fields = [
            'name', 'cname', 'zone', 'unitc', 'pduc',
            'status', 'style', 'tags', 'actived'
        ]

    def __init__(self, *args, **kwargs):
        super(RackNewForm, self).__init__(*args, **kwargs)
        self.fields['actived'].initial = False
        self.fields['actived'].widget = forms.HiddenInput()


class RextendNewForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Rextend
        fields = ['rack', 'client', 'ups1', 'ups2', 'temperature', 'humidity']

    def __init__(self, rack_id=None, *args, **kwargs):
        super(RextendNewForm, self).__init__(*args, **kwargs)
        self.fields['rack'].widget = forms.HiddenInput()
        self.fields['client'].widget = forms.HiddenInput()
        if rack_id is not None:
            self.fields['rack'].initial = self.fields['rack'].queryset.get(
                pk=rack_id)
            self.fields['client'].initial = self.fields['rack'].queryset.get(
                pk=rack_id).client


class UnitForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['rack', 'name']


class PduForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Pdu
        fields = ['rack', 'name']


class RackEditForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Rack
        fields = ['name', 'cname', 'zone', 'status', 'tags']


class CheckUnitsAddOne(forms.ModelForm):

    @staticmethod
    def check_add_one(arr):
        check = functools.reduce(
            lambda x, y: (
                x+1 == y if isinstance(x, int) else x[0] and x[1]+1 == y, y
            ), arr
        )[0]
        return check

    def clean(self):
        super(CheckUnitsAddOne, self).clean()
        units = self.cleaned_data['units']
        unit_names = [int(u.name) for u in units]
        if not unit_names:
            msg = _("设备U位不能为空")
            self.add_error('units', msg)
        if len(units) > 1:
            verify = self.check_add_one(unit_names)
            if not verify:
                msg = _("设备U位必须是连续的")
                self.add_error('units', msg)


class OnlineNewForm(
    CalendarMedia, CheckUnitsAddOne,
    FormBaseMixin, forms.ModelForm
):
    class Meta:
        model = Device
        fields = [
            'rack', 'client', 'created', 'style', 'name',
            'ipaddr', 'model', 'sn', 'units', 'pdus', 'tags'
        ]

    def __init__(self, *args, **kwargs):
        rack_id = kwargs.pop("rack_id", None)
        super(OnlineNewForm, self).__init__(*args, **kwargs)
        self.fields['rack'].empty_label = u'请选择一个机柜'
        self.fields['rack'].queryset = self.fields['rack'].queryset.order_by(
            'name')
        if rack_id is None:
            queryset_none = self.fields['client'].queryset.none()
            self.fields['client'].queryset = queryset_none
            self.fields['style'].queryset = queryset_none
            self.fields['units'].queryset = queryset_none
            self.fields['pdus'].queryset = queryset_none
            self.fields['tags'].queryset = queryset_none
        else:
            self.fields['style'].empty_label = None
            rack = self.fields['rack'].queryset.get(pk=rack_id)
            self.fields['rack'].initial = rack_id
            try:
                onidc_id = self.user.onidc_id
                name = Device.objects.filter(
                    onidc_id=onidc_id).order_by('-pk').first().name
            except BaseException:
                name = 'IS020123456-0000'
            try:
                pre, lnk, ext = name.rpartition('-')
                ext = "%05d" % (int(ext) + 1)
                self.fields['name'].initial = pre + lnk + ext
            except BaseException:
                self.fields['name'].initial = name
            try:
                self.fields['client'].initial = rack.client_id
            except BaseException:
                pass
            self.fields['units'].required = True
            self.fields['units'].queryset = self.fields['units'].queryset.filter(
                rack_id=rack_id).order_by('name')
            self.fields['pdus'].queryset = self.fields['pdus'].queryset.filter(
                rack_id=rack_id).order_by('pk')


class OnlineEditForm(
    CalendarMedia, CheckUnitsAddOne,
    FormBaseMixin, forms.ModelForm
):
    class Meta:
        model = Device
        fields = [
            'rack', 'client', 'style', 'ipaddr',
            'name', 'sn', 'model',
            'units', 'pdus', 'tags'
        ]

    def __init__(self, *args, **kwargs):
        rack_id = kwargs.pop("rack_id", None)
        super(OnlineEditForm, self).__init__(*args, **kwargs)
        self.fields['units'].required = True
        if not rack_id:
            rack_id = self.instance.rack_id
        if int(rack_id) == self.instance.rack_id:
            extra_units = self.instance.units.filter(rack_id=rack_id)
            extra_pdus = self.instance.pdus.filter(rack_id=rack_id)
        else:
            extra_units = self.instance.units.none()
            extra_pdus = self.instance.units.none()
        self.fields['rack'].queryset = self.fields['rack'].queryset.order_by(
            'name')
        self.fields['units'].queryset = self.fields['units'].queryset.filter(
            rack_id=rack_id) | extra_units
        self.fields['pdus'].queryset = self.fields['pdus'].queryset.filter(
            rack_id=rack_id).order_by("pk") | extra_pdus


class TestapplyForm(CalendarMedia, FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Testapply
        fields = [
            'name', 'device', 'start_time', 'end_time', 'proposer', 'client',
            'system', 'system_ip', 'system_pass', 'system_user', 'tags'
        ]


class GoodsForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['name', 'unit', 'brand', 'mark']


class InventoryForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'goods', 'client', 'state', 'location',
            'expressnum', 'amount', 'serials'
        ]


class JumplineForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Jumpline
        fields = [
            'linetype', 'netprod', 'bandwidth',
            'sclient', 'slocation', 'sflag',
            'dclient', 'dlocation', 'dflag', 'tags', 'route'
        ]


class DetailNewCommentForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class DocumentForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'body', 'category', 'status', 'tags']

    class Media:
        extend = True
        css = {
            'all': (
                '{}idcops/dist/summernote.css'.format(STATIC_PREFIX),
            )
        }

        js = (
            '{}idcops/dist/summernote.js'.format(STATIC_PREFIX),
            '{}idcops/dist/lang/summernote-zh-CN.min.js'.format(STATIC_PREFIX),
        )


class ConfigureNewForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Configure
        fields = ['mark', 'content']


class ZonemapNewForm(Select2Media, forms.Form):
    zone_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    rows = forms.IntegerField(
        required=True, max_value=50, min_value=1, label="行数")
    cols = forms.IntegerField(
        required=True, max_value=50, min_value=1, label="列数")

    def __init__(self, *args, **kwargs):
        self.zone_id = kwargs.pop('zone_id', None)
        super(ZonemapNewForm, self).__init__(*args, **kwargs)
        if self.zone_id is not None:
            cells = Zonemap.objects.filter(zone_id=self.zone_id).order_by(
                "row", "col").values("row", "col")
            if cells.exists():
                LAST_ROWS = cells.aggregate(Max('row'))['row__max']
                LAST_COLS = cells.aggregate(Max('col'))['col__max']
            else:
                LAST_ROWS = LAST_COLS = 0
            self.fields['zone_id'].initial = self.zone_id
            self.fields['rows'].initial = LAST_ROWS + 1
            self.fields['cols'].initial = LAST_COLS + 1
            self.fields['rows'].help_text = "类似Excel表格,行列从0开始标记,当前已有 %s行" % (
                LAST_ROWS+1)
            self.fields['cols'].help_text = "类似Excel表格,行列从0开始标记,当前已有 %s列" % (
                LAST_COLS+1)


class InitIdcForm(forms.ModelForm):
    class Meta:
        model = Idc
        fields = ['name', 'desc', 'address', 'tel']

    def __init__(self, *args, **kwargs):
        super(InitIdcForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {'autocomplete': "off", 'class': "form-control"})


class ImportOnlineForm(forms.Form):
    excel = forms.FileField(
        label="excel文件",
        help_text="请上传xls或xlsx文件",
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': True,
                # 'class': "form-control",
                'accept': MIME_ACCEPT.strip()
            }
        )
    )


class ImportExcelForm(forms.Form):
    excel = forms.FileField(
        label="excel文件",
        help_text="请上传xls或xlsx文件",
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': True,
                # 'class': "form-control",
                'accept': MIME_ACCEPT.strip()
            }
        )
    )


class NetworkForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = Network
        fields = [
            'name', 'client', 'address', 'gateway', 'vlan', 'vrf', 'kind',
        ]


class IpaddressNewForm(FormBaseMixin, forms.ModelForm):
    class Meta:
        model = IPAddress
        fields = [
            'hostname', 'address'
        ]
