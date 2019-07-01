# -*- coding: UTF-8 -*-

import logging
import traceback

from django.conf import settings
from raven.contrib.django.raven_compat.models import client

info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')
profile_logger = logging.getLogger('profile_logger')
exception_logger = logging.getLogger('exception_logger')


def log_error():
    msg = traceback.format_exc()
    if settings.DEBUG:
        info_logger.debug(msg)
    error_logger.error(traceback.format_exc())
    client.captureException()
