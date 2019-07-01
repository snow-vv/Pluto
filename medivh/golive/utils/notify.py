# -*- coding: UTF-8 -*-
import json

import re
import requests
from django.conf import settings
from hypchat import BearerAuth, _requests

from cmdb.utils import get_user_extra_by_user
from common.logger import log_error

_at_mention = re.compile('@[\w]+(?: |$)')


class HipChat(object):
    def __init__(self, token=settings.HIPCHAT_TOKEN, host=settings.HIPCHAT_HOST):
        self._req = _requests(auth=BearerAuth(token), verify=True)
        self.host = host

    def notification(self, room_id, message, color=None, notify=False, message_format=None):
        """
        Send a message to a room.
        """
        try:
            if not message_format:
                if len(_at_mention.findall(message)) > 0:
                    message_format = 'text'
                else:
                    message_format = 'html'
            data = {'message': message, 'notify': notify, 'message_format': message_format}
            if color:
                data['color'] = color
            self._req.post(self.host + '/v2/room/{}/notification'.format(room_id), data=data)
        except:
            log_error()


class DingDing(object):
    end_point = settings.DINGDING_ENDPOINT

    def send_message(self, content, phones):
        if self.end_point:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content,
                },
                "at": {
                    "atMobiles": list(map(str, phones)),
                    "isAtAll": False
                }
            }
            requests.post(url=self.end_point, json=data)


def plan_auditing_notify(plan):
    pass


def plan_passed_notify(plan):
    pass


def plan_start_notify(plan, execution):
    pass


def plan_done_notify(plan, execution):
    pass


def plan_release_done_notify(plan):
    content = '{}:{} 上线完毕。\n{}'.format(
        plan.id,
        plan.description,
        plan.notes,
    )
    user_extra = get_user_extra_by_user(plan.creator)
    phones = []
    if user_extra.phone:
        phones.append(user_extra.phone)
    DingDing().send_message(
        content=content,
        phones=phones,
    )


def plan_error_notify(plan, execution):
    pass


def task_finish_notify(task, plan, execution):
    pass


def task_error_notify(task, plan, execution):
    pass


def action_notify(action, execution):
    pass
