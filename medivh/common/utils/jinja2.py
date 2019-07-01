# -*- coding: UTF-8 -*-
import datetime
import json

import re
from django.conf import settings
from django.contrib.messages.api import get_messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment, Markup, escape, evalcontextfilter

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){1}')


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'%s<br/>' % p for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


def environment(**options):
    options['line_comment_prefix'] = '##'
    env = Environment(**options)
    env.globals.update({
        # #### function #####
        'static': staticfiles_storage.url,
        'url': reverse,
        'int': int,

        'get_messages': get_messages,  # for message framework

        'str': str,
        'isinstance': isinstance,
        'list': list,
        'dict': dict,
        'datetime': datetime,

        # #### variable #####
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'json': json
    })
    env.filters.update({
        'jsonify': lambda data: json.dumps(data),
    })
    env.filters.update({
        'nl2br': nl2br
    })
    return env
