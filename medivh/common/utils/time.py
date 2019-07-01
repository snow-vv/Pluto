# -*- coding: UTF-8 -*-
import pytz
import datetime
import time
from django.conf import settings

tz = pytz.timezone(settings.TIME_ZONE)
now_stamp = time.time()
local_time = datetime.datetime.fromtimestamp(now_stamp)
utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
offset = local_time - utc_time
offset_seconds = offset.seconds


def from_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp - offset_seconds + 8 * 3600)


def to_timestamp(dt):
    if dt is None:
        return None
    return dt.timestamp() + offset_seconds - 8 * 3600


def str2datetime(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%MZ") + datetime.timedelta(hours=8)
