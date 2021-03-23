# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import copy
import time
import json

from functools import wraps

from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.encoding import force_text
from django.forms.models import model_to_dict

from notifications.signals import notify as notify_user

from idcops.lib.tasks import log_action
from idcops.lib.utils import (
    diff_dict, shared_queryset,
    get_content_type_for_model,
    get_deleted_objects
)
from idcops.mixins import construct_menus, system_menus_key
from idcops.exports import make_to_excel
from idcops.models import Comment, Online, Client, Option
from idcops.lib.tasks import get_related_client_name

SOFT_DELELE = getattr(settings, 'SOFT_DELELE', False)

general = ['download', 'actived', 'reactive']
unit = ['download']
pdu = ['download']
device = ['download', ]
online = ['download', 'movedown']
offline = ['download', 'removeup', 'delete']
syslog = ['download', 'actived']
comment = ['download', 'actived', 'delete']
rack = ['download', 'release', 'distribution', 'delete']
configure = ['delete',]

general_has_delete = ['download', 'actived', 'reactive', 'delete']

client = general_has_delete
jumpline = general_has_delete
option = general_has_delete
document = general_has_delete
goods = general_has_delete
testapply = general_has_delete
inventory = general_has_delete
user = general_has_delete
idc = general_has_delete


def check_multiple_clients(func):
    @wraps(func)
    def wrapper(request, queryset):
        model = queryset.model
        opts = model._meta
        if hasattr(model, 'client'):
            verify = queryset.values('client').order_by('client').distinct()
            if verify.count() > 1:
                mesg = "不允许操作多个不同客户的 {}".format(opts.verbose_name)
                return mesg
        return func(request, queryset)
    return wrapper


def construct_model_meta(request, model, title=None):
    opts = model._meta
    meta = {}
    if title is None:
        title = ''
    meta['logo'] = request.user.onidc
    meta['title'] = "{} {}".format(title, opts.verbose_name)
    meta['icon'] = opts.icon
    meta['model_name'] = opts.model_name
    meta['verbose_name'] = opts.verbose_name
    user_menus = cache.get_or_set(
        system_menus_key + str(request.user.id),
        construct_menus(request.user),
        180
    )
    return meta, user_menus


def construct_context(request, queryset, action, action_name):
    meta, menus = construct_model_meta(request, queryset.model, action_name)
    context = dict(
        meta=meta,
        menus=menus,
        action=action,
        action_name=action_name,
        queryset=queryset,
    )
    return context


def download(request, queryset):
    return make_to_excel(queryset)


download.description = "导出"
download.icon = 'fa fa-download'
download.required = 'exports'


@check_multiple_clients
def html_print(request, queryset):
    model = queryset.model
    opts = model._meta
    action = sys._getframe().f_code.co_name
    action_name = "打印"
    verify = queryset.values('status').order_by('status').distinct()
    if verify.count() > 1:
        mesg = "不允许打印多个不同状态的 {}".format(opts.verbose_name)
        return mesg
    extra_for = queryset.count() - 10 < 0
    if extra_for:
        extra_for = list(range(abs(queryset.count() - 10)))
    _extra = dict(
        extra_for=extra_for,
        ticket=int(time.time()),
    )
    context = construct_context(request, queryset, action, action_name)
    context.update(_extra)
    templates = ["%s/print.html" % (opts.model_name), "base/print.html"]
    return TemplateResponse(request, templates, context)


html_print.description = "打印"
html_print.icon = 'fa fa-print'
download.required = 'view'


@check_multiple_clients
def removeup(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "取消下架"
    exclude = queryset.filter(rack__actived=False)
    if exclude.exists():
        mesg = "有设备所在机柜未使用, 无法取消下架"
        return mesg

    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = True
            obj.status = 'online'
            obj.operator = request.user
            lastunits = copy.deepcopy(obj.units.all())
            lastpdus = copy.deepcopy(obj.pdus.all())
            ucan_recovery = False not in [u.actived for u in lastunits]
            pcan_recovery = False not in [p.actived for p in lastpdus]
            if ucan_recovery:
                obj.units.all().update(actived=False, operator=obj.operator)
            else:
                verb = "无法恢复 {} 的U位".format(force_text(obj))
                notify_user.send(
                    request.user,
                    recipient=request.user,
                    target=obj,
                    verb=verb,
                )
                obj.units.clear()
            if pcan_recovery:
                obj.pdus.all().update(actived=False, operator=obj.operator)
            else:
                obj.pdus.clear()
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            message = json.dumps(list(diffs.keys()))
            old_units = [force_text(u) for u in lastunits]
            old_pdus = [force_text(p) for p in lastpdus]
            diffs.update({'last_units': old_units, 'last_pdus': old_pdus})
            content = json.dumps(diffs)
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk, action_flag=action_name,
                message=message, content=content
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


removeup.description = "取消下架"
removeup.icon = 'fa fa-level-up'


@check_multiple_clients
def movedown(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "下架"
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = False
            obj.status = 'offline'
            obj.operator = request.user
            obj.units.all().update(actived=True, operator=obj.operator)
            obj.pdus.all().update(actived=True, operator=obj.operator)
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk, action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


movedown.description = "下架"
movedown.icon = 'fa fa-level-down'


@check_multiple_clients
def actived(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "停用"
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = False
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag="停用",
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


actived.description = "停用"
actived.icon = 'fa fa-ban'


@check_multiple_clients
def reclaim(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "回收"
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = False
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


reclaim.description = "回收"
reclaim.icon = 'fa fa-ban'


@check_multiple_clients
def cancel_reclaim(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "取消回收"
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = True
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


cancel_reclaim.description = "取消回收"
cancel_reclaim.icon = 'fa fa-check-circle-o'


@check_multiple_clients
def reactive(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "启用"
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = True
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


reactive.description = "启用"
reactive.icon = 'fa fa-check-circle-o'


@check_multiple_clients
def outbound(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "出库"
    queryset = queryset.filter(actived=True)
    if not queryset.exists():
        return "选择无结果"

    total = queryset.aggregate(Sum('amount'))
    if request.POST.get('post') and request.POST.getlist('items'):
        def construct_item(index):
            obj = queryset.get(pk=int(index))
            out_amount = int(request.POST.get('count-' + str(index)))
            out_serials = request.POST.getlist('sn-' + str(index))
            copy_needed = True
            if int(out_amount) == obj.amount:
                copy_needed = False
            comment = request.POST.get(('comment-' + index), None)
            return obj, copy_needed, out_serials, out_amount, comment

        for item in request.POST.getlist('items'):
            obj, _copy, out_serials, out_amount, comment = construct_item(item)
            o = copy.deepcopy(obj)
            if _copy:
                hold = [s for s in obj.serials.split(
                    ',') if s not in out_serials]
                obj.amount -= out_amount
                obj.serials = ','.join(hold)
                new_obj = copy.deepcopy(obj)
                new_obj.pk = None
                new_obj.amount = out_amount
                new_obj.serials = ','.join(out_serials)
                new_obj.actived = False
                new_obj.creator = request.user
                new_obj.created = timezone.datetime.now()
                new_obj.operator = None
                new_obj.parent = obj
                new_obj.save()
                comment_obj = new_obj
            else:
                obj.actived = False
                obj.operator = request.user
                comment_obj = obj
            obj.save()
            if comment:
                Comment.objects.create(
                    object_repr=comment_obj, content=comment,
                    creator=request.user, onidc=obj.onidc)
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=comment_obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    _extra = dict(total=total)
    context.update(_extra)
    return TemplateResponse(request, 'base/items_out.html', context)


outbound.description = "出库"
outbound.icon = 'fa fa-check'


@check_multiple_clients
def reoutbound(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "取消出库"
    queryset = queryset.filter(actived=False)
    if not queryset.exists():
        return "查无结果"

    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            obj.actived = True
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None

    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


reoutbound.description = "取消出库"
reoutbound.icon = 'fa fa-undo'


@check_multiple_clients
def release(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "释放机柜"
    rack_ids = [id for id in queryset.values_list('id', flat=True)]
    # fix: unknown your action: The QuerySet value
    if Online.objects.filter(rack_id__in=rack_ids).exists():
        mesg = "选择的机柜中仍有在线设备，无法释放"
        return mesg

    queryset = queryset.filter(actived=True)
    if request.POST.get('post'):
        for obj in queryset:
            o = copy.deepcopy(obj)
            if obj.client and obj.client.onlinenum() == 0:
                verb = "客户 {} 没有在线设备, 是否终止".format(force_text(obj.client))
                notify_user.send(
                    request.user,
                    recipient=request.user,
                    target=obj,
                    verb=verb,
                )

            obj.actived = False
            obj.client = None
            obj.cpower = 0
            obj.style = None
            obj.status = None
            obj.operator = request.user
            obj.tags.clear()

            if obj.jnum() != 0:
                verb = "机柜 {} 还有跳线存在, 请回收".format(force_text(obj))
                notify_user.send(
                    request.user,
                    recipient=request.user,
                    target=obj,
                    verb=verb,
                )

            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs),
                related_client=get_related_client_name(o)
            )
        return None
    context = construct_context(request, queryset, action, action_name)
    return TemplateResponse(request, 'base/base_confirmation.html', context)


release.description = "释放"
release.icon = 'fa fa-recycle'


@check_multiple_clients
def distribution(request, queryset):
    action = sys._getframe().f_code.co_name
    action_name = "分配机柜"
    queryset = queryset.filter(actived=False)
    onidc_id = request.user.onidc.id
    options = Option.objects.filter(actived=True)
    clients = shared_queryset(Client.objects.filter(actived=True), onidc_id)
    status = shared_queryset(options.filter(flag='Rack-Status'), onidc_id)
    styles = shared_queryset(options.filter(flag='Rack-Style'), onidc_id)
    if request.POST.get('post') and request.POST.getlist('items'):
        def construct_item(index):
            obj = queryset.get(pk=int(index))
            try:
                client = int(request.POST.get('client-' + str(index)))
            except BaseException:
                client = 0
            status = int(request.POST.get('status-' + str(index)))
            style = int(request.POST.get('style-' + str(index)))
            cpower = request.POST.get('cpower-' + str(index))
            comment = request.POST.get(('comment-' + index), None)
            return obj, client, status, style, cpower, comment

        for item in request.POST.getlist('items'):
            obj, client, status, style, cpower, _comment = construct_item(item)
            o = copy.deepcopy(obj)
            if client != 0:
                obj.client_id = client
            obj.status_id = status
            obj.style_id = style
            obj.cpower = cpower
            obj.actived = True
            obj.save()
            diffs = diff_dict(model_to_dict(o), model_to_dict(obj))
            log_action(
                user_id=request.user.pk,
                content_type_id=get_content_type_for_model(obj, True).pk,
                object_id=obj.pk,
                action_flag=action_name,
                message=json.dumps(list(diffs.keys())),
                content=json.dumps(diffs)
            )
        return None

    context = construct_context(request, queryset, action, action_name)
    _extra = dict(clients=clients, status=status, styles=styles)
    context.update(_extra)
    return TemplateResponse(request, 'rack/distribution.html', context)


distribution.description = "分配"
distribution.icon = 'fa fa-puzzle-piece'


def delete(request, queryset):
    model = queryset.model
    opts = model._meta
    action = sys._getframe().f_code.co_name
    action_name = "删除"

    modeladmin = admin.site._registry.get(model)
    # queryset = queryset.filter(actived=False)
    if not modeladmin.has_delete_permission(request):
        raise PermissionDenied
    # using = router.db_for_write(modeladmin.model)

    deletable_objects, model_count, perms_needed, protected = \
        get_deleted_objects(queryset, request, modeladmin.admin_site)

    if request.POST.get('post') and not protected:
        if perms_needed:
            raise PermissionDenied
        if queryset.count():
            for obj in queryset:
                log_action(
                    user_id=request.user.pk,
                    content_type_id=get_content_type_for_model(obj, True).pk,
                    object_id=obj.pk,
                    action_flag="删除"
                )
            if not SOFT_DELELE:
                queryset.delete()
            else:
                queryset.update(deleted=True, actived=False)
        return None

    if len(queryset) == 1:
        objects_name = force_text(opts.verbose_name)
    else:
        objects_name = force_text(opts.verbose_name_plural)

    meta, menus = construct_model_meta(request, model, action_name)

    context = dict(
        objects_name=objects_name,
        deletable_objects=[deletable_objects],
        model_count=dict(model_count).items(),
        queryset=queryset,
        perms_lacking=perms_needed,
        protected=protected,
        opts=opts,
        meta=meta,
        action=action,
        action_name=action_name,
        menus=menus,
    )

    request.current_app = modeladmin.admin_site.name

    return TemplateResponse(request, 'base/delete_confirmation.html', context)


delete.description = "删除"
delete.icon = 'fa fa-trash'
delete.required = 'delete'
