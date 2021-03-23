# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import json
import socket
import struct
import ipaddress

from django.db import models, transaction
from django.db.models.fields import BLANK_CHOICE_DASH
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
)

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import formats, timezone
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import logger
from django.urls import reverse_lazy

# Create your models here.

from idcops.lib.fields import NullableCharField, IPNetwork
from idcops.lib.models import NamedMixin


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    today = timezone.datetime.now().strftime(r'%Y/%m/%d')
    return os.path.join('uploads', today, filename)


EXT_NAMES = (
    'level', 'hidden', 'dashboard', 'metric', 'icon',
    'icon_color', 'default_filters', 'list_display', 'extra_fields'
)

models.options.DEFAULT_NAMES += EXT_NAMES

COLOR_MAPS = (
    ("red", "红色"),
    ("orange", "橙色"),
    ("yellow", "黄色"),
    ("green", "深绿色"),
    ("blue", "蓝色"),
    ("muted", "灰色"),
    ("black", "黑色"),
    ("aqua", "浅绿色"),
    ("gray", "浅灰色"),
    ("navy", "海军蓝"),
    ("teal", "水鸭色"),
    ("olive", "橄榄绿"),
    ("lime", "高亮绿"),
    ("fuchsia", "紫红色"),
    ("purple", "紫色"),
    ("maroon", "褐红色"),
    ("white", "白色"),
    ("light-blue", "暗蓝色"),
)


class Mark(models.Model):
    CHOICES = (
        ('shared', "已共享的"),
        ('pre_share', "预共享的"),
    )
    mark = models.CharField(
        max_length=64, choices=CHOICES,
        blank=True, null=True,
        verbose_name="系统标记", help_text="系统Slug内容标记")

    class Meta:
        level = 0
        hidden = False
        dashboard = False
        metric = ""
        icon = 'fa fa-circle-o'
        icon_color = ''
        default_filters = {'deleted': False}
        list_display = '__all__'
        extra_fields = []
        abstract = True

    @cached_property
    def get_absolute_url(self):
        opts = self._meta
        # if opts.proxy:
        #    opts = opts.concrete_model._meta
        url = reverse_lazy('idcops:detail', args=[opts.model_name, self.pk])
        return url

    @cached_property
    def get_edit_url(self):
        opts = self._meta
        url = reverse_lazy('idcops:update', args=[opts.model_name, self.pk])
        return url

    def title_description(self):
        return self.__str__()


class Creator(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_creator",
        verbose_name="创建人", help_text="该对象的创建人")

    class Meta:
        abstract = True


class Operator(models.Model):
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_operator",
        blank=True, null=True,
        verbose_name="修改人", help_text="该对象的修改人"
    )

    class Meta:
        abstract = True


class Created(models.Model):
    created = models.DateTimeField(
        default=timezone.datetime.now, editable=True,
        verbose_name="创建日期", help_text="该对象的创建日期"
    )

    class Meta:
        abstract = True


class Modified(models.Model):
    modified = models.DateTimeField(
        auto_now=True, verbose_name="修改日期",
        help_text="该对象的修改日期"
    )

    class Meta:
        abstract = True
        ordering = ['-modified']


class Actived(models.Model):
    actived = models.NullBooleanField(
        default=True, verbose_name="已启用",
        help_text="该对象是否为有效资源"
    )

    class Meta:
        abstract = True


class Deleted(models.Model):
    deleted = models.NullBooleanField(
        default=False,
        verbose_name="已删除", help_text="该对象是否已被删除"
    )

    class Meta:
        abstract = True


class Parent(models.Model):
    parent = models.ForeignKey(
        'self',
        blank=True, null=True, on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_parent",
        verbose_name="父级对象", help_text="该对象的上一级关联对象"
    )

    class Meta:
        abstract = True


class Onidc(models.Model):
    onidc = models.ForeignKey(
        'Idc',
        blank=True, null=True, on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_onidc",
        verbose_name="所属机房", help_text="该资源所属的机房"
    )

    class Meta:
        abstract = True


class Tag(models.Model):
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag__icontains': 'tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="通用标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    class Meta:
        abstract = True


class ClientAble(models.Model):
    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="%(app_label)s_%(class)s_client",
        verbose_name="所属客户",
        help_text="该资源所属的客户信息"
    )

    class Meta:
        abstract = True


class RackAble(models.Model):
    rack = models.ForeignKey(
        'Rack',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="%(app_label)s_%(class)s_rack",
        verbose_name="所属机柜",
        help_text="该资源所属的机柜信息"
    )

    class Meta:
        abstract = True


class Intervaltime(models.Model):
    start_time = models.DateTimeField(
        default=timezone.datetime.now, editable=True,
        verbose_name="开始时间", help_text="该对象限定的开始时间"
    )
    end_time = models.DateTimeField(
        default=timezone.datetime.now, editable=True,
        null=True, blank=True,
        verbose_name="结束时间", help_text="该对象限定的结束时间"
    )

    class Meta:
        abstract = True


class PersonTime(Creator, Created, Operator, Modified):
    class Meta:
        abstract = True


class ActiveDelete(Actived, Deleted):
    class Meta:
        abstract = True


class Contentable(Onidc, Mark, PersonTime, ActiveDelete):
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_('content type'),
        related_name="%(app_label)s_%(class)s_content_type",
        limit_choices_to={'app_label': 'idcops'}
    )
    object_id = models.PositiveIntegerField(
        _('object id'), blank=True, null=True)
    object_repr = GenericForeignKey('content_type', 'object_id')
    content = models.TextField(verbose_name="详细内容", blank=True)

    def __str__(self):
        return force_text(self.object_repr)

    class Meta:
        abstract = True


class Comment(Contentable):
    class Meta(Mark.Meta):
        level = 2
        hidden = getattr(settings, 'HIDDEN_COMMENT_NAVBAR', True)
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "备注信息"


class Configure(Contentable):
    class Meta(Mark.Meta):
        level = 2
        hidden = getattr(settings, 'HIDDEN_CONFIGURE_NAVBAR', True)
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "用户配置"

    def __str__(self):
        return "{}-{} : {}".format(self.creator, self.content_type, self.pk)


class Remark(models.Model):
    comment = GenericRelation(
        'Comment',
        related_name="%(app_label)s_%(class)s_comment",
        verbose_name="备注信息")

    @property
    def remarks(self):
        return self.comment.filter(deleted=False, actived=True)

    class Meta:
        abstract = True


class Syslog(Contentable):
    action_flag = models.CharField(_('action flag'), max_length=32)
    message = models.TextField(_('change message'), blank=True)
    object_desc = models.CharField(
        max_length=128,
        verbose_name="对象描述"
    )
    related_client = models.CharField(
        max_length=128,
        blank=True, null=True,
        verbose_name="关系客户"
    )

    def title_description(self):
        time = formats.localize(timezone.template_localtime(self.created))
        text = '{} > {} > {}了 > {}'.format(
            time, self.creator, self.action_flag, self.content_type
        )
        return text

    class Meta(Mark.Meta):
        icon = 'fa fa-history'
        list_display = [
            'created', 'creator', 'action_flag', 'content_type',
            'object_desc', 'related_client', 'message', 'actived',
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-created', ]
        verbose_name = verbose_name_plural = _('log entries')


@python_2_unicode_compatible
class User(AbstractUser, Onidc, Mark, ActiveDelete, Remark):
    slaveidc = models.ManyToManyField(
        'Idc',
        blank=True,
        verbose_name="附属机房",
        related_name="%(app_label)s_%(class)s_slaveidc"
    )
    upper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name="直属上级",
        related_name="%(app_label)s_%(class)s_upper"
    )
    mobile = models.CharField(max_length=16, blank=True, verbose_name="手机号码")
    avatar = models.ImageField(
        upload_to='avatar/%Y/%m/%d',
        default="avatar/default.png",
        verbose_name="头像"
    )
    settings = models.TextField(
        blank=True,
        verbose_name=_("settings"),
        help_text=_("user settings use json format")
    )

    def __str__(self):
        return self.first_name or self.username

    def title_description(self):
        text = '{} > {} '.format(
            self.onidc, self.__str__()
        )
        return text

    class Meta(AbstractUser.Meta, Mark.Meta):
        level = 2
        icon = 'fa fa-user'
        list_display = [
            'username', 'first_name', 'email', 'onidc',
            'mobile', 'last_login', 'is_superuser',
            'is_staff', 'is_active'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "用户信息"


@python_2_unicode_compatible
class Idc(Mark, PersonTime, ActiveDelete, Remark):
    name = models.CharField(
        max_length=16,
        unique=True,
        verbose_name="数据中心简称",
        help_text="数据中心简称,尽量简洁。例如：酷特尔"
    )
    desc = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="数据中心全称",
        help_text="请填写公司定义的数据中心全称。例如：中国xx信xxx机房"
    )
    codename = models.SlugField(
        blank=True, null=True,
        verbose_name="数据中心代码",
        help_text=_("数据中心代码，用于编号前缀")
    )
    emailgroup = models.EmailField(
        max_length=32, blank=True, null=True,
        verbose_name="邮箱组",
        help_text="该数据中心的邮箱组"
    )
    address = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="数据中心地址",
        help_text="数据中心的具体地址"
    )
    duty = models.CharField(
        max_length=16,
        blank=True, null=True,
        default="7*24",
        verbose_name="值班类型",
        help_text="数据中心值班类型,例如:5*8"
    )
    tel = models.CharField(
        max_length=32,
        verbose_name="值班电话",
        help_text="联系方式，例如：13800138000"
    )
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="管理人员",
        help_text="权限将比普通用户多一些"
    )
    settings = models.TextField(
        blank=True,
        verbose_name=_("settings"),
        help_text=_("data center extended settings use json format")
    )

    def __str__(self):
        return self.name

    class Meta(Mark.Meta):
        level = 2
        list_display = [
            'name', 'desc', 'emailgroup', 'address',
            'duty', 'tel'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "数据中心"


@python_2_unicode_compatible
class Option(
    Onidc, Parent, Mark, PersonTime, ActiveDelete, Remark
):
    """ mark in "`shared`, `system`, `_tpl`" """
    flag = models.SlugField(
        max_length=64,
        choices=BLANK_CHOICE_DASH,
        verbose_name="标记类型",
        help_text="该对象的标记类型,比如：设备类型")
    text = models.CharField(
        max_length=64,
        verbose_name="显示内容",
        help_text="记录内容,模板中显示的内容")
    description = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="记录说明",
        help_text="记录内容的帮助信息/说明/注释")
    color = models.SlugField(
        max_length=12,
        choices=COLOR_MAPS,
        null=True, blank=True,
        verbose_name="颜色",
        help_text="该标签使用的颜色, 用于报表统计以及页面区分")
    master = models.NullBooleanField(
        default=False,
        verbose_name="默认使用",
        help_text="用于默认选中,比如:默认使用的设备类型是 服务器")

    def __init__(self, *args, **kwargs):
        super(Option, self).__init__(*args, **kwargs)
        flag = self._meta.get_field('flag')
        flag.choices = self.choices_to_field()

    @classmethod
    def choices_to_field(cls):
        _choices = [BLANK_CHOICE_DASH[0], ]
        for rel in cls._meta.related_objects:
            object_name = rel.related_model._meta.object_name.capitalize()
            field_name = rel.remote_field.name.capitalize()
            name = "{}-{}".format(object_name, field_name)
            remote_model_name = rel.related_model._meta.verbose_name
            verbose_name = "{}-{}".format(
                remote_model_name, rel.remote_field.verbose_name
            )
            _choices.append((name, verbose_name))
        return sorted(_choices)

    @property
    def flag_to_dict(self):
        maps = {}
        for item in self.choices_to_field():
            maps[item[0]] = item[1]
        return maps

    def clean_fields(self, exclude=None):
        super(Option, self).clean_fields(exclude=exclude)
        if not self.pk:
            verify = self._meta.model.objects.filter(
                onidc=self.onidc, master=self.master, flag=self.flag)
            if self.master and verify.exists():
                raise ValidationError({
                    'text': "标记类型: {} ,机房已经存在一个默认使用的标签: {}"
                            " ({}).".format(self.flag_to_dict.get(self.flag),
                                            self.text, self.description)})

    def __str__(self):
        return self.text

    def title_description(self):
        text = '{} > {}'.format(self.get_flag_display(), self.text)
        return text

    def save(self, *args, **kwargs):
        shared_flag = ['clientkf', 'clientsales', 'goodsbrand', 'goodsunit']
        if self.flag in shared_flag:
            self.mark = 'shared'
        return super(Option, self).save(*args, **kwargs)

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-cogs'
        metric = "项"
        list_display = [
            'text', 'flag', 'description', 'master',
            'color', 'parent', 'actived', 'onidc', 'mark'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-actived', '-modified']
        unique_together = (('flag', 'text'),)
        verbose_name = verbose_name_plural = "机房选项"


@python_2_unicode_compatible
class Client(Onidc, Mark, PersonTime, ActiveDelete, Remark):

    name = models.CharField(
        max_length=64,
        verbose_name="客户名称",
        help_text="请使用客户全称或跟其他系统保持一致")
    style = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Client-Style'},
        related_name="%(app_label)s_%(class)s_style",
        verbose_name="客户类型", help_text="从机房选项中选取")
    sales = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        blank=True, null=True,
        limit_choices_to={'flag': 'Client-Sales'},
        related_name="%(app_label)s_%(class)s_sales",
        verbose_name="客户销售", help_text="从机房选项中选取")
    kf = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        blank=True, null=True,
        limit_choices_to={'flag': 'Client-Kf'},
        related_name="%(app_label)s_%(class)s_kf",
        verbose_name="客户客服", help_text="从机房选项中选取")
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Client-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="通用标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    def __str__(self):
        return self.name

    def title_description(self):
        text = '{} > {}'.format(self.style, self.name)
        return text

    def onlinenum(self):
        return Online.objects.filter(client_id=self.pk).count()
    onlinenum.short_description = "设备数(台)"

    def nodenum(self):
        f = models.Q(sclient=self) | models.Q(dclient=self)
        return Jumpline.objects.filter(actived=True).filter(f).count()
    nodenum.short_description = "跳线数(条)"

    def offlinenum(self):
        return Offline.objects.filter(client_id=self.pk).count()
    offlinenum.short_description = "下线数(台)"

    def racknum(self):
        return Rack.objects.filter(client=self, actived=True).count()
    racknum.short_description = "机柜数(个)"

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-users'
        metric = "个"
        list_display = [
            'name', 'style', 'sales', 'kf', 'onlinenum',
            'nodenum', 'racknum', 'actived', 'tags'
        ]
        extra_fields = ['onlinenum', 'offlinenum', 'racknum']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        unique_together = (('onidc', 'name'),)
        ordering = ['-actived', '-modified']
        verbose_name = verbose_name_plural = "客户信息"


class Rack(Onidc, Mark, PersonTime, ActiveDelete, ClientAble, Remark):
    name = models.CharField(
        max_length=32,
        verbose_name="机柜名称",
        help_text="楼层区域-列+编号:3F1-A01"
    )
    cname = models.CharField(
        max_length=64,
        blank=True, null=True,
        verbose_name="机柜别名",
        help_text="仅用于区分多个机柜名称"
    )
    zone = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Rack-Zone'},
        related_name="%(app_label)s_%(class)s_zone",
        verbose_name="机房区域", help_text="从机房选项中选取 机房区域"
    )
    style = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        null=True, blank=True,
        limit_choices_to={'flag': 'Rack-Style'},
        related_name="%(app_label)s_%(class)s_style",
        verbose_name="机柜类型", help_text="从机房选项中选取 机柜类型"
    )
    status = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        null=True, blank=True,
        limit_choices_to={'flag': 'Rack-Status'},
        related_name="%(app_label)s_%(class)s_status",
        verbose_name="机柜状态", help_text="从机房选项中选取 机柜状态"
    )
    unitc = models.PositiveSmallIntegerField(
        default=45,
        validators=[MinValueValidator(0), MaxValueValidator(180)],
        verbose_name="U位数量",
        help_text="填写机柜实际U位数量,默认:45")
    pduc = models.PositiveSmallIntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        verbose_name="PDU数量",
        help_text="填写A、B两路PDU数总和,默认:30个"
    )
    cpower = models.PositiveIntegerField(
        default=10,
        verbose_name="合同电力 (A)",
        help_text="跟客户签署的合同电力,用于计算客户是否超电"
    )
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Rack-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="机柜标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    def __str__(self):
        return self.name

    def title_description(self):
        text = '{} > {}'.format(self.zone, self.name)
        return text

    def onum(self):
        return Online.objects.filter(rack_id=self.pk).count()
    onum.short_description = "设备数(台)"

    def jnum(self):
        f = models.Q(slocation=self) | models.Q(dlocation=self)
        return Jumpline.objects.filter(actived=True).filter(f).count()
    jnum.short_description = "跳线数(条)"

    @property
    def units(self):
        qset = self.idcops_unit_rack.all().order_by('-name')
        return qset

    @property
    def pdus(self):
        qset = self.idcops_pdu_rack.all()
        return qset

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-cube'
        icon_color = 'aqua'
        metric = "个"
        dashboard = True
        default_filters = {'deleted': False, 'actived': True}
        list_display = [
            'name', 'cname', 'zone', 'client', 'status', 'style',
            'unitc', 'pduc', 'cpower', 'onum', 'jnum', 'actived', 'tags'
        ]
        extra_fields = ['jnum', 'onum']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-actived', '-modified']
        unique_together = (('zone', 'name'), ('zone', 'cname'))
        verbose_name = verbose_name_plural = "机柜信息"


@python_2_unicode_compatible
class Rextend(Onidc, Mark, PersonTime, ActiveDelete, RackAble, ClientAble):

    ups1 = models.DecimalField(
        max_digits=3, decimal_places=1,
        blank=True, default="0.0",
        verbose_name="A路电量", help_text="填写数值"
    )
    ups2 = models.DecimalField(
        max_digits=3, decimal_places=1,
        blank=True, default="0.0",
        verbose_name="B路电量", help_text="填写数值"
    )
    temperature = models.DecimalField(
        max_digits=3, decimal_places=1,
        blank=True, default="22.0",
        verbose_name="机柜温度", help_text="机柜温度"
    )
    humidity = models.DecimalField(
        max_digits=3, decimal_places=1,
        blank=True, default="55.0",
        verbose_name="机柜湿度", help_text="机柜湿度"
    )

    def __str__(self):
        return self.rack.name

    class Meta(Mark.Meta):
        level = 2
        hidden = True
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "电量温湿度"


@python_2_unicode_compatible
class Unit(
    Onidc, Mark, PersonTime, ActiveDelete, RackAble, ClientAble
):
    name = models.SlugField(
        max_length=3, verbose_name="U位名称",
        help_text="必须是数字字符串,例如：01, 46, 47"
    )

    def __str__(self):
        return self.name

    @property
    def online(self):
        online = self.device_set.filter(actived=True, deleted=False)
        if online.exists():
            return online.first()
        else:
            return False

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                self.name = "%02d" % (int(self.name))
            except Exception:
                raise ValidationError("必须是数字字符串,例如：01, 46, 47")
        else:
            if not self.online and not self.actived:
                return
            if self.online and self.actived:
                return
        return super(Unit, self).save(*args, **kwargs)

    def clean(self):
        if not self.pk:
            try:
                int(self.name)
            except Exception:
                raise ValidationError("必须是数字字符串,例如：01, 46, 47")
        else:
            if not self.online and not self.actived:
                raise ValidationError('该U位没有在线设备, 状态不能为`True`')
            if self.online and self.actived:
                raise ValidationError('该U位已有在线设备，状态不能为`False`')

    @property
    def repeat(self):
        name = self.name
        last_name = "%02d" % (int(name) + 1)
        try:
            last = Unit.objects.get(rack=self.rack, name=last_name)
        except Exception:
            last = None
        if last:
            if (last.actived == self.actived) and (last.online == self.online):
                return True
        else:
            return False

    class Meta(Mark.Meta):
        level = 2
        icon = 'fa fa-magnet'
        metric = "个"
        list_display = [
            'name',
            'rack',
            'client',
            'actived',
            'modified',
            'operator']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        unique_together = (('rack', 'name'),)
        verbose_name = verbose_name_plural = "U位信息"


@python_2_unicode_compatible
class Pdu(
    Onidc, Mark, PersonTime, ActiveDelete, RackAble, ClientAble
):
    name = models.SlugField(max_length=12, verbose_name="PDU名称")

    def __str__(self):
        return self.name

    @property
    def online(self):
        online = self.device_set.filter(actived=True, deleted=False)
        if online.exists():
            return online.first()
        else:
            return False

    def save(self, *args, **kwargs):
        if self.pk:
            if not self.online and not self.actived:
                return
            if self.online and self.actived:
                return
        return super(Pdu, self).save(*args, **kwargs)

    class Meta(Mark.Meta):
        level = 2
        icon = 'fa fa-plug'
        metric = "个"
        list_display = [
            'name',
            'rack',
            'client',
            'actived',
            'modified',
            'operator']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        unique_together = (('rack', 'name'),)
        verbose_name = verbose_name_plural = "PDU信息"


@python_2_unicode_compatible
class Device(Onidc, Mark, PersonTime, ActiveDelete, Remark):
    name = models.SlugField(
        max_length=32,
        unique=True,
        verbose_name="设备编号",
        help_text="默认最新一个可用编号")
    rack = models.ForeignKey(
        'Rack',
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_rack",
        verbose_name="所属机柜",
        help_text="该资源所属的机柜信息")
    units = models.ManyToManyField(
        'Unit',
        blank=True,
        verbose_name="设备U位",
        help_text="设备所在机柜中的U位信息")
    pdus = models.ManyToManyField(
        'Pdu',
        blank=True, verbose_name="PDU接口",
        help_text="设备所用机柜中的PDU接口信息")
    client = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_client",
        verbose_name="所属客户",
        help_text="该资源所属的客户信息")
    sn = models.SlugField(
        max_length=64,
        verbose_name="设备SN号", help_text="比如: FOC1447001")
    ipaddr = models.CharField(
        max_length=128,
        blank=True, default="0.0.0.0",
        verbose_name="IP地址",
        help_text="比如: 192.168.0.21/10.0.0.21")
    model = models.CharField(
        max_length=32,
        verbose_name="设备型号", help_text="比如: Dell R720xd")
    style = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Device-Style'},
        related_name="%(app_label)s_%(class)s_style",
        verbose_name="设备类型", help_text="设备类型默认为服务器")
    urange = models.CharField(
        max_length=12, blank=True, null=True,
        verbose_name="U位范围", help_text="U位起始到结束，比如：05-08"
    )
    _STATUS = (
        ('online', "在线"),
        ('offline', "已下线"),
        ('moved', "已迁移"),
    )
    status = models.SlugField(
        choices=_STATUS, default='online',
        verbose_name="状态", help_text="默认为在线")
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Device-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="设备标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    def __str__(self):
        return self.name

    def title_description(self):
        text = '{} > {} > {}'.format(
            self.client, self.get_status_display(), self.style
        )
        return text

    def list_units(self):
        value = [force_text(i) for i in self.units.all().order_by('name')]
        if len(value) > 1:
            value = [value[0], value[-1]]
        units = "-".join(value)
        return units

    @property
    def move_history(self):
        ct = ContentType.objects.get_for_model(self, for_concrete_model=True)
        logs = Syslog.objects.filter(
            content_type=ct, object_id=self.pk,
            actived=True, deleted=False, action_flag="修改",
        ).filter(content__contains='"units"')
        history = []
        for log in logs:
            data = json.loads(log.content)
            lus = data.get('units')[0]
            try:
                swap = {}
                swap['id'] = log.pk
                swap['created'] = log.created
                swap['creator'] = log.creator
                ous = Unit.objects.filter(pk__in=lus)
                value = [force_text(i) for i in ous]
                if len(value) > 1:
                    value = [value[0], value[-1]]
                swap['units'] = "-".join(value)
                swap['rack'] = ous.first().rack
                move_type = "跨机柜迁移" if 'rack' in data else "本机柜迁移"
                swap['type'] = move_type
                history.append(swap)
            except Exception as e:
                logger.warning(
                    'rebuliding device history warning: {}'.format(e))
        return history

    def last_rack(self):
        try:
            return self.move_history[0].get('rack')
        except Exception as e:
            logger.warning('Get device last rack warning: {}'.format(e))

    def save(self, *args, **kwargs):
        if not self.pk and not self.sn:
            cls = ContentType.objects.get_for_model(self)
            cls_id = "%02d" % (cls.id)
            try:
                object_id = \
                    cls.model_class().objects.order_by('pk').last().pk + 1
            except Exception:
                object_id = 1
            object_id = "%02d" % (object_id)
            self.sn = str(
                timezone.datetime.now().strftime('%Y%m%d') + cls_id + object_id
            )
        return super(Device, self).save(*args, **kwargs)

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-server'
        metric = "台"
        list_display = [
            'name', 'rack', 'urange', 'client', 'model', 'style',
            'sn', 'ipaddr', 'status', 'actived', 'modified'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-modified']
        unique_together = (('onidc', 'name',),)
        verbose_name = verbose_name_plural = "设备信息"


class OnlineManager(models.Manager):
    def get_queryset(self):
        return super(
            OnlineManager,
            self).get_queryset().filter(
            actived=True,
            deleted=False)


class OfflineManager(models.Manager):
    def get_queryset(self):
        return super(
            OfflineManager,
            self).get_queryset().filter(
            actived=False,
            deleted=False)


class Online(Device):

    objects = OnlineManager()

    class Meta(Mark.Meta):
        icon = 'fa fa-server'
        icon_color = 'green'
        metric = "台"
        dashboard = True
        list_display = [
            'name', 'rack', 'urange', 'client', 'model',
            'sn', 'ipaddr', 'style', 'status', 'created', 'creator'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        proxy = True
        verbose_name = verbose_name_plural = "在线设备"


class Offline(Device):

    objects = OfflineManager()

    class Meta(Mark.Meta):
        icon = 'fa fa-server'
        icon_color = 'red'
        metric = "台"
        list_display = [
            'name', 'rack', 'urange', 'client', 'model',
            'style', 'sn', 'ipaddr', 'modified', 'operator'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        proxy = True
        verbose_name = verbose_name_plural = "下线设备"


@python_2_unicode_compatible
class Jumpline(Onidc, Mark, PersonTime, ActiveDelete, Remark):

    linenum = models.SlugField(
        max_length=32,
        unique=True, editable=False,
        verbose_name="跳线编号",
        help_text="系统自动生成的slug, 整个系统唯一的编号"
    )
    linetype = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Jumpline-Linetype'},
        related_name="%(app_label)s_%(class)s_linetype",
        verbose_name="线缆类型",
        help_text="网线/光纤/其它, 字段数据来自机房选项"
    )
    netprod = models.ForeignKey(
        'Option',
        blank=True, null=True,
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Jumpline-Netprod'},
        related_name="%(app_label)s_%(class)s_netprod",
        verbose_name="网络产品",
        help_text="电信单线/动态BGP, 字段数据来自机房选项"
    )
    bandwidth = models.PositiveIntegerField(
        default=0,
        blank=True, null=True,
        verbose_name="带宽(MB)",
        help_text="仅填写上联带宽，客户内网不要填写"
    )
    sclient = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        verbose_name="本端客户", help_text="选择本端客户"
    )
    slocation = models.ForeignKey(
        'Rack',
        related_name="slocation",
        on_delete=models.PROTECT,
        verbose_name="本端机柜", help_text="选择本端机柜号"
    )
    sflag = models.CharField(
        max_length=64, verbose_name="本端标识",
        help_text="填写设备编号+(端口),如:1024-(g0/0/24)"
    )
    dclient = models.ForeignKey(
        'Client',
        on_delete=models.PROTECT,
        related_name="dclient",
        verbose_name="对端客户", help_text="选择对端客户"
    )
    dlocation = models.ForeignKey(
        'Rack',
        on_delete=models.PROTECT,
        related_name="dlocation",
        verbose_name="对端机柜", help_text="选择对端机柜号"
    )
    dflag = models.CharField(
        max_length=64, verbose_name="对端标识",
        help_text="填写设备编号+(端口),如:2048-(fa0/1/48)")
    route = models.TextField(
        null=True, blank=True,
        verbose_name="途径路由",
        help_text="按照上面格式填写中途路由节点信息"
    )
    tags = models.ManyToManyField(
        'Option',
        blank=True,
        limit_choices_to={'flag': 'Jumpline-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="跳线标签",
        help_text="可拥有多个标签,字段数据来自机房选项")

    def __str__(self):
        return self.linenum

    def title_description(self):
        state = "有效跳线" if self.actived else "已回收跳线"
        return '{} > {} > {}'.format(state, self.netprod, self.linenum)

    def save(self, *args, **kwargs):
        if not self.pk:
            cls = ContentType.objects.get_for_model(self)
            cls_id = "%02d" % cls.id
            try:
                object_id = \
                    cls.model_class().objects.order_by('pk').last().pk + 1
            except Exception:
                object_id = 1
            object_id = "%02d" % object_id
            self.linenum = str(
                timezone.datetime.now().strftime('%Y%m%d') + cls_id + object_id
            )
        return super(Jumpline, self).save(*args, **kwargs)

    class Meta(Mark.Meta):
        icon = 'fa fa-random'
        icon_color = 'yellow'
        metric = "条"
        default_filters = {'deleted': False, 'actived': True}
        dashboard = True
        list_display = [
            'linenum', 'linetype', 'netprod', 'bandwidth',
            'sclient', 'sflag', 'dclient', 'dflag', 'actived', 'tags'
        ]
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-actived', '-modified']
        verbose_name = verbose_name_plural = "跳线信息"


@python_2_unicode_compatible
class Testapply(Onidc, Mark, PersonTime, ActiveDelete, Intervaltime, Remark):

    name = models.CharField(
        max_length=32, unique=True, verbose_name="测试单号",
        help_text="请查看申请的测试单号")
    device = models.CharField(
        max_length=64, verbose_name="测试设备",
        # limit_choices_to={'tags__flag': 'Device-Tags', 'tags__text':'测试机'},
        help_text="测试设备调用在线设备中拥有'测试机'标签的设备")
    proposer = models.CharField(
        max_length=32,
        verbose_name="申请人", help_text="请填写真实申请人姓名")
    client = models.CharField(
        max_length=32,
        verbose_name="测试客户", help_text="填写申请客户信息")
    system = models.CharField(
        max_length=32, verbose_name="操作系统",
        help_text="填写测试机所使用的系统,比如：CentOS 6.5 x64")
    system_ip = models.CharField(
        max_length=128, verbose_name="测试IP地址",
        help_text="测试客户所测试的IP地址")
    system_user = models.SlugField(
        max_length=32, verbose_name="系统用户名",
        help_text="测试机系统的登录用户名")
    system_pass = models.CharField(
        max_length=32, verbose_name="系统密码",
        help_text="测试机系统的登录密码")
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Testapply-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="测试标签",
        help_text="可拥有多个标签,字段数据来自机房选项")

    def __str__(self):
        return self.name

    def title_description(self):
        state = "正在测试" if self.actived else "已结束的测试"
        text = '{} > {} '.format(state, self.name)
        return text

    def expired(self):
        expired = self.end_time < timezone.datetime.now()
        return "已过期" if expired else "正在测试"
    expired.short_description = "是否过期"

    class Meta(Mark.Meta):
        icon = 'fa fa-check-circle'
        icon_color = 'blue'
        metric = "个"
        default_filters = {'deleted': False, 'actived': True}
        dashboard = True
        list_display = [
            'name', 'device', 'client', 'system_ip', 'system_user',
            'start_time', 'end_time', 'expired', 'proposer', 'actived',
        ]
        extra_fields = ['expired']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        ordering = ['-actived', '-modified']
        verbose_name = verbose_name_plural = "测试信息"


@python_2_unicode_compatible
class Zonemap(Onidc, Mark, PersonTime, ActiveDelete, Remark):
    zone = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Rack-Zone'},
        related_name="%(app_label)s_%(class)s_zone",
        verbose_name="所在区域"
    )
    rack = models.ForeignKey(
        'Rack',
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_rack",
        null=True, blank=True, verbose_name="机柜号"
    )
    row = models.PositiveSmallIntegerField(verbose_name="行号")
    col = models.PositiveSmallIntegerField(verbose_name="列号")
    desc = models.CharField(
        max_length=128, blank=True,
        default="-", verbose_name="坐标描述"
    )

    def __str__(self):
        return "<{}, {}>".format(self.row, self.col)

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-binoculars'
        metric = "个"
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        unique_together = (('zone', 'row', 'col'),)
        verbose_name = verbose_name_plural = "区域视图"


@python_2_unicode_compatible
class Goods(Onidc, Mark, PersonTime, ActiveDelete):

    name = models.CharField(
        max_length=100, verbose_name="物品名称",
        help_text="推荐命名规则 [物品型号/ 物品尺寸] 物品名: 2.5寸SAS 600GB 固态硬盘"
    )
    brand = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        blank=True, null=True,
        limit_choices_to={'flag': 'Goods-Brand'},
        related_name="%(app_label)s_%(class)s_brand",
        verbose_name="生产厂商",
        help_text="来自机房选项, 标记类型为: 物品分类-生产厂商"
    )
    unit = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Goods-Unit'},
        related_name="%(app_label)s_%(class)s_unit",
        verbose_name="物品单位",
        help_text="来自机房选项, 标记类型为: 物品分类-物品单位"
    )

    def __str__(self):
        return "{} {}".format(self.brand if self.brand else '', self.name)

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-folder-open-o'
        list_display = ['name', 'unit', 'brand', 'actived', 'mark']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        # ordering = ['-modified']
        unique_together = (('brand', 'name'),)
        verbose_name = verbose_name_plural = "物品分类"


@python_2_unicode_compatible
class Inventory(
    Onidc, Mark, PersonTime, Parent, ActiveDelete, ClientAble, Remark
):
    kcnum = models.SlugField(
        max_length=32,
        unique=True, editable=False,
        verbose_name="库存编号",
        help_text="系统自动生成的slug, 整个系统唯一的编号"
    )
    goods = models.ForeignKey(
        'Goods',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_goods",
        verbose_name="物品信息", help_text="从物品分类中选取")
    state = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Inventory-State'},
        related_name="%(app_label)s_%(class)s_state",
        verbose_name="物品状态",
        help_text="来自机房选项, 标记类型为: 库存物品-物品状态")
    location = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        limit_choices_to={'flag': 'Inventory-Location'},
        related_name="%(app_label)s_%(class)s_location",
        verbose_name="存放位置",
        help_text="存放位置, 从机房选项中选取")
    serials = models.TextField(
        blank=True, null=True,
        verbose_name="唯一标识",
        help_text="物品SN号，条形码等唯一标识, 多个请用英文逗号分隔"
    )
    expressnum = models.CharField(
        max_length=200,
        blank=True, null=True,
        verbose_name="快递单号",
        help_text="顺丰快递：287088422120"
    )
    amount = models.PositiveIntegerField(
        default=1, verbose_name="数量",
        help_text="同一客户，同一物品，同一状态，同一位置可以批量新建"
    )
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Inventory-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="通用标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    def __str__(self):
        return force_text(self.goods)

    def title_description(self):
        # state = "正在库存" if self.actived else "已出库"
        text = '{} > {} > {} > {}'.format(
            self.client, self.kcstate(), self.state, self.goods,
        )
        return text

    def get_serials_list(self):
        try:
            s = [i for i in self.serials.split(',') if i != '']
        except Exception:
            s = None
        return s

    def kcstate(self):
        state = "库存" if self.actived else "已出库"
        return state
    kcstate.short_description = "库存状态"

    def save(self, *args, **kwargs):
        if not self.pk:
            cls = ContentType.objects.get_for_model(self)
            cls_id = "%02d" % (cls.id)
            try:
                object_id = \
                    cls.model_class().objects.order_by('pk').last().pk + 1
            except Exception:
                object_id = 1
            object_id = "%02d" % (object_id)
            self.kcnum = str(
                timezone.datetime.now().strftime('%Y%m%d') + cls_id + object_id
            )
        return super(Inventory, self).save(*args, **kwargs)

    class Meta(Mark.Meta):
        icon = 'fa fa-cubes'
        metric = "件"
        list_display = [
            'kcnum', 'client', 'state',
            'goods', 'location',
            'amount', 'kcstate', 'tags']
        extra_fields = ['kcstate']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        # unique_together = (('state', 'actived', 'goods', 'client'),)
        ordering = ['-actived', '-modified']
        verbose_name = verbose_name_plural = "库存物品"


@python_2_unicode_compatible
class Document(Onidc, Mark, PersonTime, ActiveDelete, Remark):
    title = models.CharField(max_length=128, verbose_name="文档标题")
    body = models.TextField(verbose_name="文档内容")
    category = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        blank=True, null=True,
        limit_choices_to={'flag': 'Document-Category'},
        related_name="%(app_label)s_%(class)s_category",
        verbose_name="文档分类",
        help_text="分类, 从机房选项中选取")
    status = models.ForeignKey(
        'Option',
        on_delete=models.PROTECT,
        blank=True, null=True,
        limit_choices_to={'flag': 'Document-Status'},
        related_name="%(app_label)s_%(class)s_status",
        verbose_name="文档状态",
        help_text="从机房选项中选取")
    tags = models.ManyToManyField(
        'Option',
        blank=True, limit_choices_to={'flag': 'Document-Tags'},
        related_name="%(app_label)s_%(class)s_tags",
        verbose_name="通用标签",
        help_text="可拥有多个标签,字段数据来自机房选项"
    )

    def __str__(self):
        return self.title

    class Meta(Mark.Meta):
        icon = 'fa fa-book'
        metric = "份"
        list_display = [
            'title',
            'category',
            'created',
            'creator',
            'status',
            'onidc',
            'tags']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "文档资料"


@python_2_unicode_compatible
class Attachment(Onidc, Mark, PersonTime, ActiveDelete, Tag, Remark):
    name = models.CharField(
        max_length=255,
        verbose_name=_("file name")
    )
    file = models.FileField(
        upload_to=upload_to,
        verbose_name=_("file")
    )

    def __str__(self):
        return self.name

    class Meta(Mark.Meta):
        level = 1
        icon = 'fa fa-file'
        metric = "份"
        hidden = True
        list_display = [
            'name',
            'file',
            'created',
            'creator',
            'onidc',
            'tags']
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = "媒体文件"


@python_2_unicode_compatible
class IPAddress(
    Onidc, Mark, PersonTime, ActiveDelete, ClientAble, Tag
):
    address = models.GenericIPAddressField(
        verbose_name="IP 地址", help_text="例如：172.16.21.1",
        # unique=True,
    )
    hostname = NullableCharField(
        verbose_name="主机名", max_length=255,
        null=True, blank=True, default=None
    )
    is_management = models.BooleanField(
        verbose_name="管理地址", default=False,
    )
    is_public = models.BooleanField(
        verbose_name="公有地址", default=False, editable=False,
    )
    is_gateway = models.BooleanField(
        verbose_name="网关地址", default=False,
    )
    status = models.NullBooleanField(
        verbose_name="状态", default=None,
        help_text="如果IP地址已被使用，则值为True"
    )
    network = models.ForeignKey(
        'Network',
        null=True, default=None, editable=False,
        related_name="%(app_label)s_%(class)s_network",
        on_delete=models.SET_NULL, verbose_name="所属网域",
    )
    number = models.DecimalField(
        verbose_name="IP号",
        help_text="IP地址的整数形式",
        editable=False,
        # unique=True,
        max_digits=39, decimal_places=0,
        default=None,
    )

    class Meta(Mark.Meta):
        icon = 'fa fa-circle'
        metric = "个"
        level = 2
        hidden = True
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        verbose_name = verbose_name_plural = _('IP address')

    def __str__(self):
        return self.address

    @property
    def ip(self):
        return ipaddress.ip_address(self.address)

    def search_networks(self):
        int_value = int(self.ip)
        nets = Network.objects.filter(
            min_ip__lte=int_value,
            max_ip__gte=int_value
        ).order_by('-min_ip', 'max_ip')
        return nets

    def clean_fields(self, exclude=None):
        super(IPAddress, self).clean_fields(exclude=exclude)
        is_public = not self.ip.is_private
        if is_public:
            # 如果是公网地址，则验证唯一性
            number = int(ipaddress.ip_address(self.address or 0))
            verify = self._meta.model.objects.filter(
                onidc=self.onidc, number=number
            )
            if verify.exists():
                raise ValidationError({
                    'text': "机房已经存在 {} 这个公网地址".format(self.address)
                })

    def save(self, *args, **kwargs):
        if self.number and not self.address:
            self.address = ipaddress.ip_address(int(self.number))
        else:
            self.number = int(ipaddress.ip_address(self.address or 0))
        self.network = self.search_networks().first() \
            if self.search_networks().exists() else None
        self.is_public = not self.ip.is_private
        super(IPAddress, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Network(
    Onidc, Mark, PersonTime, Parent, ActiveDelete, ClientAble, Remark,
    NamedMixin, Tag, models.Model
):
    address = IPNetwork(
        verbose_name="网络地址",
        help_text="以字符串形式显示（例如172.16.21.0/24）",
    )
    gateway = models.ForeignKey(
        'IPAddress', verbose_name="网关地址",
        related_name="%(app_label)s_%(class)s_gateway",
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    vlan = models.PositiveIntegerField(
        verbose_name=_('VLAN ID'),
        null=True, blank=True, default=None,
    )
    vrf = models.CharField(
        max_length=32, null=True, blank=True,
        verbose_name=_("VRF"),
        help_text="虚拟路由转发 (Virtual Routing and Forwarding)"
    )
    discovery_hosts = models.BooleanField(
        verbose_name="自动发现", default=True,
        help_text="通过ICMP协议发现子网中新主机"
    )
    check_hosts = models.BooleanField(
        verbose_name="检查主机", default=False,
        help_text="ping 子网内的主机以检查可用性"
    )
    is_public = models.BooleanField(
        verbose_name="公有地址",
        editable=False, default=None
    )
    min_ip = models.DecimalField(
        verbose_name="最小IP号",
        editable=False,
        max_digits=39,
        decimal_places=0,
    )
    max_ip = models.DecimalField(
        verbose_name="最大IP号",
        editable=False,
        max_digits=39,
        decimal_places=0,
    )
    kind = models.ForeignKey(
        'Option',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="网络类型",
        limit_choices_to={'flag__icontains': 'Network-Kind'},
        related_name="%(app_label)s_%(class)s_kind",
        help_text="从机房选项中新建选择"
    )

    @property
    def network(self):
        return ipaddress.ip_network(self.address, strict=False)

    @property
    def network_address(self):
        return self.network.network_address

    @property
    def broadcast_address(self):
        return self.network.broadcast_address

    @property
    def netmask(self):
        return self.network.prefixlen

    @property
    def netmask_dot_decimal(self):
        return socket.inet_ntoa(
            struct.pack('>I', (0xffffffff << (32 - self.netmask)) & 0xffffffff)
        )

    @property
    def size(self):
        if not self.min_ip and not self.max_ip or self.netmask == 32:
            return 0
        if self.netmask == 31:
            return 2
        return self.max_ip - self.min_ip - 1

    @property
    def _has_address_changed(self):
        return self.address != self._old_address

    class Meta(Mark.Meta):
        icon = 'fa fa-sitemap'
        metric = "个"
        level = 0
        hidden = True
        default_permissions = ('view', 'add', 'change', 'delete', 'exports')
        unique_together = ('min_ip', 'max_ip')
        verbose_name = verbose_name_plural = "网络管理"

    def __init__(self, *args, **kwargs):
        super(Network, self).__init__(*args, **kwargs)
        self._old_address = self.address

    def __str__(self):
        return '{} ({} | VLAN: {})'.format(self.name, self.address, self.vlan)

    def save(self, *args, **kwargs):
        if self.gateway_id and not self.gateway.is_gateway:
            self.gateway.is_gateway = True
            self.gateway.save()

        update_subnetworks_parent = kwargs.pop(
            'update_subnetworks_parent', True
        )
        creating = not self.pk
        if (
            self._has_address_changed and
            update_subnetworks_parent and
            not creating
        ):
            prev_subnetworks = self.get_immediate_subnetworks()
        else:
            prev_subnetworks = []
        self.min_ip = int(self.network_address)
        self.max_ip = int(self.broadcast_address)
        self.is_public = self.network.is_global
        super(Network, self).save(*args, **kwargs)
        if self._has_address_changed or creating:
            self._assign_new_ips_to_network()
            self._unassign_ips_from_network()
            if update_subnetworks_parent:
                self._update_subnetworks_parent(prev_subnetworks)

    def delete(self):
        with transaction.atomic():
            self.address = '0.0.0.0/32'
            self.save()
            super().delete()

    def _update_subnetworks_parent(self, prev_subnetworks):
        for network in prev_subnetworks:
            network.save(update_subnetworks_parent=False)
        for network in self.get_immediate_subnetworks():
            network.save(update_subnetworks_parent=False)
        for network in self.__class__._default_manager.filter(
            parent=self.parent,
            min_ip__gte=self.min_ip, max_ip__lte=self.max_ip
        ):
            network.save(update_subnetworks_parent=False)

    def _assign_new_ips_to_network(self):
        for ip in IPAddress.objects.exclude(
            network=self,
        ).exclude(
            network__in=self.get_subnetworks()
        ).filter(
            number__gte=self.min_ip,
            number__lte=self.max_ip
        ):
            ip.save()

    def _unassign_ips_from_network(self):
        for ip in IPAddress.objects.filter(
            network=self, number__lt=self.min_ip, number__gt=self.max_ip
        ):
            ip.save()

    def get_subnetworks(self):
        return Network.objects.filter(parent=self).exclude(pk=self.pk)

    def get_immediate_subnetworks(self):
        return Network.objects.filter(parent=self)

    def get_first_free_ip(self):
        used_ips = set(IPAddress.objects.filter(
            number__range=(self.min_ip, self.max_ip)
        ).values_list(
            'number', flat=True
        ))
        min_ip = int(self.min_ip + 1)
        max_ip = int(self.max_ip - 1)
        free_ip_as_int = None
        for free_ip_as_int in range(min_ip, max_ip + 1):
            if free_ip_as_int not in used_ips:
                next_free_ip = ipaddress.ip_address(free_ip_as_int)
                return next_free_ip

    def issue_next_free_ip(self):
        ip_address = self.get_first_free_ip()
        return IPAddress.objects.create(address=str(ip_address))

    def search_networks(self):
        nets = Network.objects.filter(
            min_ip__lte=self.min_ip,
            max_ip__gte=self.max_ip
        ).exclude(pk=self.id).order_by('-min_ip', 'max_ip')
        return nets
