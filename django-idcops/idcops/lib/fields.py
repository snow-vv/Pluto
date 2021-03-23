# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ipaddress

from django.db import models
from django.db.models.fields import CharField, Field
from django import forms
from django.core.exceptions import ValidationError


MAX_NETWORK_ADDRESS_LENGTH = 44


def network_validator(value):
    """Validator for CIDR notaion."""
    try:
        ipaddress.ip_network(value, strict=False)
    except ipaddress.NetmaskValueError as exc:
        raise ValidationError(exc.message)


class IPNetwork(Field):
    """Field for network with CIDR notation."""

    def __init__(self, *args, **kwargs):
        self.default_validators = [network_validator]
        kwargs['max_length'] = MAX_NETWORK_ADDRESS_LENGTH
        super(IPNetwork, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return CharField(
            max_length=MAX_NETWORK_ADDRESS_LENGTH
        ).db_type(connection)

    def to_python(self, value):
        if isinstance(value, ipaddress.IPv4Network):
            return value
        if value is None:
            return value
        try:
            return ipaddress.ip_network(value)
        except ValueError as exc:
            raise ValidationError(
                str(exc),
                code='invalid',
                params={'value': value},
            )

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return ipaddress.ip_network(value)

    def get_db_prep_save(self, value, connection, **kwargs):
        return str(value)

    def get_db_prep_value(self, value, connection, **kwargs):
        return str(value)


class NullableFormFieldMixin(object):
    def to_python(self, value):
        """Returns a Unicode object."""
        if value in self.empty_values:
            return None
        return super(NullableFormFieldMixin, self).to_python(value)


class NullableCharFormField(NullableFormFieldMixin, forms.CharField):
    pass


class NullableGenericIPAddressFormField(
    NullableFormFieldMixin, forms.GenericIPAddressField
):
    pass


class NullableCharFieldMixin(object):
    """
    Mixin for char fields and descendants which will replace empty string value
    ('') by null when saving to the database.
    It's especially useful when field is marked as unique and at the same time
    allows null/blank (`models.CharField(unique=True, null=True, blank=True)`)
    """
    _formfield_class = NullableCharFormField

    def get_prep_value(self, value):
        r = super(NullableCharFieldMixin, self).get_prep_value(value) or None
        return r

    def formfield(self, **kwargs):
        defaults = {}
        if self._formfield_class:
            defaults['form_class'] = self._formfield_class
        defaults.update(kwargs)
        return super(NullableCharFieldMixin, self).formfield(**defaults)


class NullableCharField(NullableCharFieldMixin, models.CharField):
    pass


class NullableGenericIPAddressField(
    NullableCharFieldMixin,
    models.GenericIPAddressField
):
    _formfield_class = NullableGenericIPAddressFormField
