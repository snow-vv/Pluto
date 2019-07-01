import json

import six
from common.views import JsonView
from shield.utils.redis import get_shield_redis


class IpBlackListApiView(JsonView):
    permissions = ['shield.black_ips']

    def get(self, request):
        return {
            'list': [
                {
                    'ip': str(key, encoding="utf-8"),
                    'extra_data': str(value, encoding="utf-8"),
                } for key, value in six.iteritems(get_shield_redis().hgetall('ip_rule'))
                ]
        }


class AddBlackIPApiView(JsonView):
    permissions = ['shield.add_black_ip']

    def post(self, request, ip):
        get_shield_redis().hset('ip_rule', ip, json.dumps({}))
        return {}


class DeleteBlackIPApiView(JsonView):
    permissions = ['shield.rm_black_ip']

    def post(self, request, ip):
        get_shield_redis().hdel('ip_rule', ip)
        return {}
