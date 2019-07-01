# -*- coding: UTF-8 -*-

import requests, hashlib


def gravatar_url(email, size=40):
    """Construct the gravatar url."""
    gravatar_url = ''.join(['http://www.gravatar.com/avatar/',
                            hashlib.md5(email.lower()).hexdigest(), '?s=%d' % size])

    res = requests.get(gravatar_url + '&d=404')
    if res.status_code == 404:
        return None

    return gravatar_url
