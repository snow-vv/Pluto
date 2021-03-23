# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import ipaddress
from django.apps import apps
from django.dispatch import receiver
from django.db.models import signals
# from django.contrib.auth.signals import user_logged_in

from idcops.lib.utils import (
    get_content_type_for_model, fields_for_model,
    # get_client_ip
)
from idcops.models import (
    Device, Network, Rack, Unit, Pdu, User, Configure,
    IPAddress,
    # Syslog
)


def pdus_units_changed(sender, **kwargs):
    model = kwargs.pop('model', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action == 'pre_add':
        objects = model.objects.filter(pk__in=pk_set)
        for obj in objects:
            if not obj.actived:
                raise('actived current is `false`')
    if action == 'post_add':
        model.objects.filter(pk__in=pk_set).update(actived=False)
    if action in ["pre_remove", "post_remove"]:
        model.objects.filter(pk__in=pk_set).update(actived=True)


signals.m2m_changed.connect(
    pdus_units_changed, sender=Device.units.through,
    dispatch_uid='when_device_units_changed'
)


signals.m2m_changed.connect(
    pdus_units_changed, sender=Device.pdus.through,
    dispatch_uid='when_device_pdus_changed'
)


@receiver(signals.post_delete, sender=Device)
def update_units_pdus(**kwargs):
    instance = kwargs.pop('instance', None)
    instance.units.all().update(actived=True)
    instance.pdus.all().update(actived=True)


@receiver(signals.post_save, sender=Rack)
def rack_created_tasks(instance, created, **kwargs):
    onidc_id = instance.onidc_id
    creator_id = instance.creator_id
    if created and onidc_id:
        units = []
        pdus = []
        for unit in range(1, int(instance.unitc + 1)):
            name = str(unit).zfill(2)
            units.append(
                Unit(
                    onidc_id=onidc_id, name=name,
                    rack=instance, creator_id=creator_id
                )
            )
        Unit.objects.bulk_create(units)
        for pdu in range(1, int((instance.pduc + 2) / 2)):
            pdus.append(Pdu(onidc_id=onidc_id, creator_id=creator_id,
                            rack=instance, name='A' + str(pdu)))
            pdus.append(Pdu(onidc_id=onidc_id, creator_id=creator_id,
                            rack=instance, name='B' + str(pdu)))
        Pdu.objects.bulk_create(pdus)
    if not created and instance.client is not None:
        Unit.objects.filter(rack=instance).update(client=instance.client)
        Pdu.objects.filter(rack=instance).update(client=instance.client)


@receiver(signals.post_save, sender=Network)
def generate_ip_address(instance, created, **kwargs):
    onidc_id = instance.onidc_id
    creator_id = instance.creator_id
    client = instance.client
    if onidc_id and creator_id and created:
        ipaddr_pool = []
        for ip in instance.network:
            address = str(ip)
            number = int(ipaddress.ip_address(ip or 0))
            ipaddr_pool.append(
                IPAddress(
                    address=address, hostname=address, number=number,
                    onidc_id=onidc_id, creator_id=creator_id, client=client,
                )
            )
        IPAddress.objects.bulk_create(ipaddr_pool)


@receiver(signals.post_save, sender=User)
def initial_user_configuration(instance, created, **kwargs):
    if created:
        models = apps.get_app_config('idcops').get_models()
        exclude = ['onidc', 'deleted', 'mark', 'id', 'password']
        configures = []
        for model in models:
            fds = [f for f in fields_for_model(model) if f not in exclude]
            _fields = getattr(model._meta, 'list_display', fds)
            fields = _fields if isinstance(_fields, list) else fds
            content = {'list_only_date': 1, 'list_display': fields}
            config = dict(
                onidc=instance.onidc,
                creator=instance,
                mark='list',
                content_type=get_content_type_for_model(model),
                content=json.dumps(content),
            )
            configures.append(Configure(**config))
        Configure.objects.bulk_create(configures)


# @receiver(user_logged_in)
# def on_login(sender, user, request, **kwargs):
#     ip = get_client_ip(request)
#     # content_type = get_content_type_for_model(user._meta.model)
#     message = "{} 从 {} 登录成功".format(str(user), ip)
#     user_agent = request.META.get('HTTP_USER_AGENT')
#     Syslog.objects.create(
#         creator_id=user.id,
#         onidc_id=user.onidc_id,
#         object_repr=user,
#         action_flag='登录',
#         message=message,
#         object_desc=str(user),
#         content='{}, {}'.format(message, user_agent),
#         actived=True
#     )
