# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib
import re

from django.db import models
from django.utils.encoding import force_text
from django.contrib.contenttypes.models import ContentType
from idcops.models import Client, Syslog, User, Device
from idcops.lib.utils import display_for_field


def get_related_client_name(obj):
    related_clients = []
    for f in obj._meta.fields:
        if f.related_model is Client or (
                f.name == 'client' and isinstance(f, models.CharField)):
            value = display_for_field(f.value_from_object(obj), f, html=False)
            related_clients.append(value)
    return '{}'.format(", ".join(c for c in list(set(related_clients))))


def log_action(user_id, content_type_id, object_id,
               action_flag, message='', content='',
               actived=True, related_client=None, created=None
               ):
    model = ContentType.objects.get_for_id(content_type_id).model_class()
    object = model.objects.get(pk=object_id)
    if related_client is None:
        related_client = get_related_client_name(object) or '-'
    user = User.objects.get(pk=user_id)
    onidc_id = user.onidc_id
    data = dict(
        creator_id=user_id,
        onidc_id=onidc_id,
        object_repr=object,
        action_flag=action_flag,
        message=message,
        object_desc=force_text(object)[:128],
        related_client=related_client[:128],
        content=content, actived=actived
    )
    if created:
        data.update(**dict(created=created))
    log = Syslog.objects.create(**data)
    return force_text(log)


def get_dell_model(sn, model):
    """
    返回Dell设备SN号对应的设备型号
    """
    query_url = "http://www.dell.com/support/home/cn/zh/cnbsdt1/product-support/servicetag/"
    pattern = "deel|dell|PowerEdge|R7|R8|R6|R4|戴尔"
    if re.findall(pattern, model, re.M | re.I | re.U):
        try:
            url = "{0}{1}".format(query_url, sn)
            response = urllib.request(url, timeout=30)
            html = response.read()
            _model = ''.join(re.findall(r'productName:"(.*?)"', html))
            _code = ''.join(re.findall(
                r'<span class="beforeCaptcha">(.*?)</span>', html))
        except BaseException:
            _model = model
            _code = None
    else:
        _model = model
        _code = None
    return _model, _code


def device_post_save(pk, first=False):
    """
    设备信息保存后需要自动更新该设备的相关信息.
    """

    # 获取设备信息
    try:
        obj = Device.objects.get(pk=pk)
    except Exception as e:
        raise(e)

    # 更新设备状态
    if not obj.actived:
        status = 'offline'
    else:
        if obj.move_history and obj.actived:
            status = 'moved'
        else:
            status = 'online'
    Device.objects.filter(pk=obj.pk).update(status=status)
    Device.objects.filter(pk=obj.pk).update(urange=obj.list_units())
    '''
    if obj.sn and obj.mark != 'CheckSuccess':
        # Dell 设备
        if len(obj.sn.strip()) == 7:
            old_model = obj.model
            new_model, code = get_dell_model(obj.sn, obj.model)
            if code:
                mark = 'CheckSuccess'
            else:
                mark = 'CheckFailure'
    '''
    return obj.status
