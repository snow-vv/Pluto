# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
from django.urls import reverse_lazy
from django.utils import formats, timezone
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide useful API
    to know what fields have been changed.

    The main value is to allow simply changing the values and then saving the
    object only if it is "really changed"
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return list(self.diff.keys())

    @property
    def get_d1(self):
        return self.__initial

    @property
    def get_d2(self):
        return self._dict

    @property
    def changed_field_names(self):
        data = {}
        for field_name in self.changed_fields:
            field = self._meta.get_field(field_name)
            data[field.name] = field.verbose_name
        return data

    @property
    def _dict(self):
        exclude = ['operator_id', 'creator_id', 'created', 'modified']
        opts = self._meta
        data = {}
        keys = [f.attname for f in opts.fields]
        for f in chain(opts.many_to_many):
            if self.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(
                    self).values_list('pk', flat=True))
        original = {k: self.__dict__.get(k) for k in keys if k not in exclude}
        data.update(**original)
        for key, value in data.items():
            if isinstance(value, timezone.datetime):
                value = formats.localize(timezone.template_localtime(value))
            data.update(**{key: value})
        return data

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    class Meta:
        abstract = True


class AbsoluteUrlMixin(object):
    def get_absolute_url(self):
        opts = self._meta
        if opts.proxy:
            opts = opts.concrete_model._meta
        return reverse_lazy(
            'admin:{}_{}_change'.format(
                opts.app_label, opts.model_name
            ), args=(self.pk,)
        )


class NamedMixin(models.Model):
    """Describes an abstract model with a unique ``name`` field."""
    name = models.CharField(_('name'), max_length=255, unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

    class NonUnique(models.Model):
        """Describes an abstract model with a non-unique ``name`` field."""
        name = models.CharField(verbose_name=_("name"), max_length=75)

        class Meta:
            abstract = True
            ordering = ['name']

        def __str__(self):
            return self.name
