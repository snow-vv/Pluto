# -*- coding: UTF-8 -*-

import json
import math
import time
import datetime
from datetime import timedelta

import requests
from celery import shared_task
from django.core.mail import EmailMessage, get_connection

from common.exception import ExceedDingdingPostMsgLimitException
from common.logger import log_error
from common.utils.aliyun import aliyun_rds

from cmdb.models import RDS
from django.conf import settings
from periodic.utils.parser import parse_to_dingding_msg


def _get_slow_query_between(from_timestamp=None, to_timestamp=None):
    end_timestamp = to_timestamp if to_timestamp else time.time() // 60 * 60 - 3600 * 8     # 转为UTC时间
    start_timestamp = from_timestamp if from_timestamp else end_timestamp - settings.CRAWL_SLOW_LOG_TIME

    start_time = time.strftime("%Y-%m-%dT%H:%MZ", time.localtime(start_timestamp))
    end_time = time.strftime("%Y-%m-%dT%H:%MZ", time.localtime(end_timestamp))

    result = []
    rdses = RDS.objects.exclude(slow_log_dingding='').all()
    for rds in rdses:
        res = aliyun_rds.get_slow_log(
            'cn-qingdao',
            instance_id=rds.instance_id,
            start_time=start_time,
            end_time=end_time
        )

        total_count = res['TotalRecordCount']
        page_num = int(math.ceil(total_count / 30))
        page_num = min(page_num, 2)
        for page_count in range(1, page_num + 1):
            res = aliyun_rds.get_slow_log(
                'cn-qingdao',
                instance_id=rds.instance_id,
                start_time=start_time,
                end_time=end_time,
                page=page_count
            )
            result.append(res)

    return result


connection = get_connection(
    username=settings.EMAIL_USER,
    password=settings.EMAIL_PASSWORD,
)

def send_email(to_email_list, title, body):
    mail = EmailMessage(connection=connection)
    mail.from_email = settings.DEFAULT_FROM_EMAIL
    mail.subject = title
    mail.to = to_email_list
    mail.body = body
    mail.send()


@shared_task
def send_slow_log_to_emails():
    today = datetime.datetime.now()
    yesterday = today - timedelta(days=1)

    y_start = yesterday.replace(hour=0, minute=0, second=0)
    y_start_ts = y_start.timestamp() // 60 * 60 - 8 * 3600

    y_end = yesterday.replace(hour=23, minute=59, second=59)
    y_end_ts = y_end.timestamp() // 60 * 60 - 8 * 3600

    results = _get_slow_query_between(y_start_ts, y_end_ts)
    body = ''
    for result in results:
        s = sorted(
            result['Items']['SQLSlowRecord'],
            key=lambda x: x['QueryTimes'],
            reverse=True
        )
        s = filter(lambda x: '( 1=1 ) AND ( 1=1 )' not in x['SQLText'], s)
        y = list(s)
        for i in y:
            i['SQLText'] = i['SQLText'][:1024]

        z = json.dumps(y, indent=4, sort_keys=True)
        body += z
        body += '\n\n'
        body += '-' * 70
        body += '\n\n'

    send_email(
        settings.SLOW_QUERY_TO_EMAILS,
        '%s slow query' % today.strftime('%Y-%m-%d'),
        body
    )


@shared_task
def push_rds_slow_log_to_dingding(from_timestamp=None, to_timestamp=None):
    """
    拉取rds慢日志推送到钉钉
    :param from_timestamp: 慢日志开始时间，默认当前时间前推settings.CRAWL_SLOW_LOG_TIME
    :param to_timestamp: 慢日志结束时间，默认当前时间
    :return:
    """
    results = _get_slow_query_between(from_timestamp, to_timestamp)
    for result in results:
        try:
            for record in result['Items']['SQLSlowRecord']:
                record['description'] = rds.description
                msg = parse_to_dingding_msg(record)
                print(msg)

                resp = requests.post(rds.slow_log_dingding, json=msg)
                if json.loads(resp.content.decode()).get('errcode') != 0:
                    raise ExceedDingdingPostMsgLimitException()

        except ExceedDingdingPostMsgLimitException:
            log_error()
            break
