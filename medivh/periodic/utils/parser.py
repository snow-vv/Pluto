# -*- coding: UTF-8 -*-
from datetime import datetime
from periodic.utils.timezone import UTC, UTC8


def parse_UTC_to_UTC8(time_str):
    """
    UTC时间串转北京时间串
    :param time_str: 示例：2017-11-16T10:03:12Z
    :return: 示例：2017-11-16 19:03:11
    """
    t = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
    t = t.replace(tzinfo=UTC)
    local_t = t.astimezone(UTC8)
    local_t_str = str(local_t).split('+')[0]
    return local_t_str


def parse_to_dingding_msg(record):
    description = record.get('description')
    host_address = record.get('HostAddress')
    db_name = record.get('DBName')
    sql_text = record.get('SQLText')
    query_times = record.get('QueryTimes')
    lock_times = record.get('LockTimes')
    parse_row_counts = record.get('ParseRowCounts')
    return_row_counts = record.get('ReturnRowCounts')
    execution_starttime = parse_UTC_to_UTC8(record.get('ExecutionStartTime'))

    content = """主机名：{}
数据库主机地址：{}
数据库名：{}
执行时长：{}
锁定时长：{}
解析行数：{}
返回行数：{}
执行开始时间：{}
查询语句：{}
""".format(description, host_address, db_name, query_times, lock_times,
           parse_row_counts, return_row_counts, execution_starttime, sql_text)

    msg = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }

    return msg
