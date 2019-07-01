# -*- coding: UTF-8 -*-
from common.exception import SlbException
from common.utils.aliyun import aliyun_slb


def check_slb_num(slb):
    """
    检查slb机器数量是否满足灰度条件，若weight>0的机器数大于1，则可灰度
    :param slb: SLB instance
    :return: None
    """
    res = aliyun_slb.info('cn-qingdao', slb.instance_id)
    servers = res['BackendServers']['BackendServer']
    servers_has_weight = list(filter(lambda x: x['Weight'] > 0, servers))
    if len(servers_has_weight) < 2:
        raise SlbException(message="slb:{}当前机器数n={}，不满足灰度条件(n>=2)".format(slb.name, len(servers_has_weight)))
