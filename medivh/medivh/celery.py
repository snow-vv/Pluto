from __future__ import absolute_import, unicode_literals

import os
import raven
from celery import Celery
from django.conf import settings
from raven.contrib.celery import register_logger_signal, register_signal
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medivh.settings')


class Celery(Celery):
    """wrap for celery.Celery."""

    def on_configure(self):
        # check if sentry settings provided
        if not settings.SENTRY_CELERY_ENDPOINT:
            return

        client = raven.Client(settings.SENTRY_CELERY_ENDPOINT)

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


app = Celery('medivh')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
