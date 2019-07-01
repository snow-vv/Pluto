# -*- coding: UTF-8 -*-

import json
import time

from django.middleware.common import MiddlewareMixin

from common.logger import profile_logger


# gevent 时间会不对？
class ProfileMiddleware(MiddlewareMixin):
    def process_request(self, request):
        self.time_start = time.time()
        self.clock_start = time.process_time()

    def process_response(self, request, response):
        self.time_end = time.time()
        self.clock_end = time.process_time()

        format_string = (
            '!medivh {client_ip} {method} {path} {time:.6f} {clock:.6f} '
            '{status} {session_key} {user_id} {params}'
        )

        params = request.GET.copy()
        params.update(request.POST)
        user = getattr(request, 'user', None)
        message = format_string.format(
            client_ip=request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0],
            method=request.method,
            path=request.path,
            time=self.time_end - self.time_start,
            clock=self.clock_end - self.clock_start,
            status=response.status_code,
            user_id=user.id if user else '-',
            params=json.dumps(params),
            session_key='-'
        )
        profile_logger.info(message)
        return response
