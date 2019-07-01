# -*- coding: UTF-8 -*-
import json

from django.core.management import BaseCommand
from cmdb.tasks import sync_ecs


class Command(BaseCommand):
    def handle(self, *args, **options):
        sync_ecs()