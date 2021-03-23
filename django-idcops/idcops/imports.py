# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import csv
import copy
import xlrd
import operator
from functools import reduce

from django.db.models import Q
from django.utils.timezone import datetime

from idcops.lib.utils import shared_queryset
from idcops.lib.tasks import device_post_save
from idcops.models import (
    Option, Rack, Client, Unit, Pdu, User, Online, Device
)


CreatorId = 1


def import_online_for_csv(filename, onidc_id):
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        field_describe = [d for d in next(csvreader) if d]
        fieldnames = [f for f in next(csvreader) if f]
        rows = csv.DictReader(csvfile, fieldnames=fieldnames)
        handler_error = []
        handler_warning = []
        handler_success = []
        index = 0
        for index, row in enumerate(rows, 1):
            if index > 500:
                # 每次只处理500条数据
                msg = "一次最多导入500条数据"
                handler_error.append(msg)
                break
            raw = copy.copy(row)
            try:
                _created = '-'.join(re.split(r'-|/', row.get('created')))
                created = datetime.strptime(_created, '%Y-%m-%d')
            except:
                msg = "第{}行：日期格式不正确，跳过处理本行".format(index)
                handler_error.append(msg)
                continue
            raw.update(**dict(created=created))
            verify = Device.objects.filter(name=raw.get('name'))
            if verify.exists():
                msg = "第{}行：{}设备已存在".format(index, raw.get('name'))
                handler_error.append(msg)
                continue
            style = get_or_create_style(raw.get('style'), onidc_id)
            creator = get_creator(raw.get('creator'))
            # 获取机柜信息
            rack, err = get_rack(raw.get('rack'), onidc_id)
            if not rack:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                continue
            # 获取客户信息
            client, err = get_or_create_client(raw.get('client'), onidc_id)
            if not client:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                continue
            # 实例化在线设备
            instance = Online(
                created=created, style=style, creator=creator,
                rack=rack, client=client, name=raw.get('name'),
                sn=raw.get('sn'), ipaddr=raw.get('ipaddr'),
                model=raw.get('model'), onidc_id=onidc_id
            )
            instance.save()
            # 保存U位
            units, err = clean_units(raw.get('units'), rack.pk)
            if units:
                for u in units:
                    instance.units.add(u)
                units.update(actived=False)
                instance.save()
            else:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                # U位不对，删除本实例
                instance.delete()
                continue
            handler_success.append(instance.name)
            # 保存PDU
            pdus, err = clean_pdus(raw.get('pdus'), rack.pk)
            if pdus:
                for p in pdus:
                    instance.pdus.add(p)
                pdus.update(actived=False)
                instance.save()
            else:
                msg = "第{}行：{}".format(index, err)
                handler_warning.append(msg)
            # 保存TAGS
            tags = clean_tags(raw.get('tags'), onidc_id, creator.pk)
            if tags:
                for t in tags:
                    instance.tags.add(t)
                instance.save()
            device_post_save(instance.pk, True)
        return handler_error, handler_warning, handler_success, index


def import_online(path, onidc_id):
    fileds = [
        'name', 'creator', 'rack', 'client', 'created', 'onidc',
        'sn', 'model', 'ipaddr', 'style', 'units', 'pdus', 'tags'
    ]
    workbook = xlrd.open_workbook(path)
    sheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(sheets[0])
    # 设置导入错误日志记录到一个字典中
    handler_error = []
    handler_warning = []
    handler_success = []
    index = 0
    headers = None
    for index, row in enumerate(worksheet.get_rows(), 1):
        # header = index
        if index == 1:
            # 跳过表头
            continue
        if index == 2:
            # 获取字段名称
            headers = [h.value for h in row]
            continue
        if index > 502:
            # 每次只处理500条数据
            msg = "一次最多导入500条数据"
            handler_error.append(msg)
            break
        data = dict(zip(headers, [k.value for k in row]))
        raw = {k: str(data.get(k)) for k in fileds}
        _created = '-'.join(re.split(r'-|/', raw.get('created')))
        created = datetime.strptime(_created, '%Y-%m-%d')
        raw.update(**dict(created=created))
        verify = Device.objects.filter(name=raw.get('name'))
        if verify.exists():
            msg = "第{}行：{}设备已存在".format(index, raw.get('name'))
            handler_error.append(msg)
            continue
        else:
            style = get_or_create_style(raw.get('style'), onidc_id)
            creator = get_creator(raw.get('creator'))
            # 获取机柜信息
            rack, err = get_rack(raw.get('rack'), onidc_id)
            if not rack:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                continue
            # 获取客户信息
            client, err = get_or_create_client(raw.get('client'), onidc_id)
            if not client:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                continue
            # 实例化在线设备
            instance = Online(
                created=created, style=style, creator=creator,
                rack=rack, client=client, name=raw.get('name'),
                sn=raw.get('sn'), ipaddr=raw.get('ipaddr'),
                model=raw.get('model'), onidc_id=onidc_id
            )
            instance.save()
            # 保存U位
            units, err = clean_units(raw.get('units'), rack.pk)
            if units:
                for u in units:
                    instance.units.add(u)
                units.update(actived=False)
                instance.save()
            else:
                msg = "第{}行：{}".format(index, err)
                handler_error.append(msg)
                # U位不对，删除本实例
                instance.delete()
                continue
            handler_success.append(instance.name)
            # 保存PDU
            pdus, err = clean_pdus(raw.get('pdus'), rack.pk)
            if pdus:
                for p in pdus:
                    instance.pdus.add(p)
                pdus.update(actived=False)
                instance.save()
            else:
                msg = "第{}行：{}".format(index, err)
                handler_warning.append(msg)
            # 保存TAGS
            tags = clean_tags(raw.get('tags'), onidc_id, creator.pk)
            if tags:
                for t in tags:
                    instance.tags.add(t)
                instance.save()
            device_post_save(instance.pk, True)
    total = (index-2)
    return handler_error, handler_warning, handler_success, total


def import_rack(path, onidc_id):
    fileds = [
        'name', 'cname', 'zone', 'client', 'style',
        'status', 'unitc', 'pduc', 'cpower', 'tags'
    ]
    workbook = xlrd.open_workbook(path)
    sheets = workbook.sheet_names()
    worksheet = workbook.sheet_by_name(sheets[0])
    # 设置导入错误日志记录到一个字典中
    handler_error = []
    handler_warning = []
    handler_success = []
    index = 0
    headers = None
    for index, row in enumerate(worksheet.get_rows(), 1):
        # header = index
        if index == 1:
            # 跳过表头
            continue
        if index == 2:
            # 获取字段名称
            headers = [h.value for h in row]
            continue
        if index > 1002:
            # 每次只处理500条数据
            msg = "一次最多导入1000条数据"
            handler_error.append(msg)
            break
        data = dict(zip(headers, [k.value for k in row]))
        raw = {k: data.get(k) for k in fileds}
        zone, err = get_rack_zone(raw.get('zone'), onidc_id)
        if not zone:
            msg = "第{}行：{}".format(index, err)
            handler_error.append(msg)
            continue
        name = raw.get('name')
        verify = Rack.objects.filter(name=name, zone=zone)
        if verify.exists():
            msg = "第{}行：{}机柜已存在".format(index, name)
            handler_error.append(msg)
            continue
        else:
            # 处理机柜别名
            cname = raw.get('cname') if raw.get('cname') else name
            # 获取机柜类型和机柜状态
            style = get_or_create_option(
                raw.get('style'), onidc_id, flag='Rack-Style'
            )
            status = get_or_create_option(
                raw.get('status'), onidc_id, flag='Rack-Status', create=True
            )
            # 获取客户信息
            if raw.get('client'):
                actived = True
                client, err = get_or_create_client(raw.get('client'), onidc_id)
                if not client:
                    msg = "第{}行：{}".format(index, err)
                    handler_error.append(msg)
                    continue
            else:
                actived = False
                client = None
            unitc = int(raw.get('unitc'))
            pduc = int(raw.get('pduc'))
            cpower = int(raw.get('cpower'))
            # 实例化机柜
            instance = Rack(
                name=name, cname=cname, zone=zone, client=client,
                style=style, status=status, actived=actived,
                creator_id=CreatorId, unitc=unitc, pduc=pduc,
                cpower=cpower, onidc_id=onidc_id
            )
            instance.save()
            handler_success.append(instance.name)
            # 保存标签
            tags = get_or_create_tags(
                raw.get('tags'), onidc_id, CreatorId, 'Rack-Tags'
            )
            if tags:
                for t in tags:
                    instance.tags.add(t)
                instance.save()
    total = (index-2)
    return handler_error, handler_warning, handler_success, total


def get_creator(username):
    fields = ['first_name', 'username', 'mobile']
    query = [Q(**{k: username.strip()}) for k in fields]
    query_str = reduce(operator.or_, query)
    user = User.objects.filter(query_str)
    if user.exists():
        return user.first()
    else:
        return User.objects.filter().order_by('pk').first()


def get_or_create_style(name, onidc_id):
    f = dict(
        flag='Device-Style', text=name.strip()
    )
    qs = shared_queryset(Option.objects.filter(**f), onidc_id)
    if qs.exists():
        instance = qs.first()
    else:
        extra = dict(
            description=name.strip(),
            onidc_id=onidc_id,
            creator_id=CreatorId
        )
        f.update(**extra)
        instance = Option.objects.create(**f)
    return instance


def get_or_create_option(name, onidc_id, flag, create=False):
    if not name.strip():
        instance = None
    f = dict(
        flag=flag, text=name.strip()
    )
    qs = shared_queryset(Option.objects.filter(**f), onidc_id)
    if qs.exists():
        instance = qs.first()
    else:
        if create and name.strip():
            extra = dict(
                description=name.strip(),
                onidc_id=onidc_id,
                creator_id=CreatorId
            )
            f.update(**extra)
            instance = Option.objects.create(**f)
        else:
            instance = None
    return instance


def get_or_create_client(name, onidc_id):
    qs = Client.objects.filter(name=name.strip())
    if qs.exists():
        instance = qs.first()
    else:
        types = Option.objects.filter(
            onidc_id=onidc_id, flag='Client-Style'
        )
        if types.exists():
            default = types.filter(master=True)
            if default.exists():
                style = default.first()
            else:
                style = types.first()
        else:
            return None, "客户类型不能为空"
        instance = Client.objects.create(
            onidc_id=onidc_id, creator_id=CreatorId,
            name=name.strip(), style=style
        )
    return instance, None


def get_rack_zone(name, onidc_id):
    """
    Return: (instance, error)
    """
    qs = Option.objects.filter(text=name.strip(), onidc_id=onidc_id)
    if qs.exists():
        return qs.first(), None
    else:
        return None, "找不到指定机房区域，请新建"


def get_rack(name, onidc_id):
    """
    Return: (instance, error)
    """
    qs = Rack.objects.filter(name=name.strip(), onidc_id=onidc_id)
    if qs.filter(actived=True).exists():
        return qs.first(), None
    elif qs.filter(actived=False).exists():
        return None, "该机柜未分配使用"
    else:
        return None, "找不到该机柜"


def clean_units(data, rack_id):
    units = sorted([int(i) for i in data.split('|') if len(i) != 0])
    units_list = [
        str(x).zfill(2) for x in range(units[0], units[-1]+1)
    ]
    instances = Unit.objects.filter(rack_id=rack_id, name__in=units_list)
    if instances.exists():
        used = instances.filter(actived=False)
        if used.count() > 0:
            return None, "有U位被占用中"
        return instances, None
    else:
        return None, "找不到U位信息"


def clean_pdus(data, rack_id):
    pdus = re.split('[, |]', data)
    pdus_list = [x.strip() for x in pdus if x]
    instances = Pdu.objects.filter(rack_id=rack_id, name__in=pdus_list)
    if instances.exists():
        used = instances.filter(actived=False)
        if used.count() > 0:
            return instances.filter(actived=True), "部分PDU位被占用中"
        return instances, None
    else:
        return None, "找不到PDU位信息"


def clean_tags(tags, onidc_id, creator_id):
    tags = re.split('[, |]', tags)
    tags_list = [x.strip() for x in tags if x]
    default = dict(onidc_id=onidc_id, flag='Device-Tags')
    instances = []
    for tag in tags_list:
        default.update(**dict(text=tag))
        verify = Option.objects.filter(**default)
        if verify.exists():
            instance = verify.first()
        else:
            default.update(**dict(creator_id=creator_id))
            instance = Option.objects.create(**default)
        instances.append(instance)
    return instances


def get_or_create_tags(tags, onidc_id, creator_id, flag):
    tags = re.split('[, |]', tags)
    tags_list = [x.strip() for x in tags if x]
    default = dict(onidc_id=onidc_id, flag=flag)
    instances = []
    for tag in tags_list:
        default.update(**dict(text=tag))
        verify = Option.objects.filter(**default)
        if verify.exists():
            instance = verify.first()
        else:
            default.update(**dict(creator_id=creator_id))
            instance = Option.objects.create(**default)
        instances.append(instance)
    return instances
