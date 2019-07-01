# -*- coding: UTF-8 -*-
import redis
from django.conf import settings

__shield_redis = None


def get_shield_redis():
    global __shield_redis
    if __shield_redis is None:
        __shield_redis = redis.StrictRedis.from_url(settings.SHIELD_REDIS_URL)
    return __shield_redis
