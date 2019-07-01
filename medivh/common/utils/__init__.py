# -*- coding: UTF-8 -*-
def _ensure_type(t, value):
    if not isinstance(value, t):
        raise TypeError('value is not of type {}: ({}){}'.format(
            repr(t), repr(type(value)), repr(value)
        ))


def ensure_isinstance_of(value, t):
    """
    :type value: t
    :type t: type | (type, type) | (type, type, type)
    """
    _ensure_type(t, value)


def to_dict(l):
    r = {}
    for x in l:
        key = x['name']
        value = x['value']
        if key in r:
            r[key] = ','.join([r[key], value])
        else:
            r[key] = value
    return r
