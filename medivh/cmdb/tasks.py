# -*- coding: UTF-8 -*-
import math
from celery import shared_task

from common.utils.aliyun import aliyun_ecs, aliyun_slb, aliyun_rds
from cmdb.models import ECS, SLB, RDS
from common.utils.time import str2datetime


@shared_task
def sync_ecs():
    res = aliyun_ecs.infos('cn-qingdao', )
    total = res['TotalCount']

    count = 0
    while True:
        count += 1
        res = aliyun_ecs.infos('cn-qingdao', count)

        for instance in res['Instances']['Instance']:
            ecs = ECS.objects.filter(instance_id=instance['InstanceId']).first()
            if ecs:
                ecs.ip = instance['InnerIpAddress']['IpAddress'][0]
                ecs.cpu = instance['Cpu']
                ecs.memory = instance['Memory']
                ecs.description = instance['Description']
                ecs.public_ip = instance['PublicIpAddress']['IpAddress'][0]
                ecs.name = instance['InstanceName']
                ecs.created_time = str2datetime(instance['CreationTime'])
                ecs.save()
            else:
                ecs = ECS.objects.create(
                    ip=instance['InnerIpAddress']['IpAddress'][0],
                    instance_id=instance['InstanceId'],
                    cpu=instance['Cpu'],
                    memory=instance['Memory'],
                    description=instance['Description'],
                    public_ip=instance['PublicIpAddress']['IpAddress'][0],
                    name=instance['InstanceName'],
                    created_time=str2datetime(instance['CreationTime']),
                )
        if res['PageSize'] * res['PageNumber'] >= total:
            break


@shared_task
def sync_slb():
    res = aliyun_slb.infos('cn-qingdao', )

    for instance in res['LoadBalancers']['LoadBalancer']:
        slb = SLB.objects.filter(instance_id=instance['LoadBalancerId']).first()
        if slb:
            slb.instance_id = instance['LoadBalancerId']
            slb.name = instance['LoadBalancerName']
            slb.description = instance['AddressType']
            slb.save()
        else:
            slb = SLB.objects.create(
                instance_id=instance['LoadBalancerId'],
                name=instance['LoadBalancerName'],
                ip=instance['Address'],
                description=instance['AddressType'],
            )


@shared_task
def sync_rds():
    res = aliyun_rds.infos('cn-qingdao', )
    total = res['TotalRecordCount']
    page_num = int(math.ceil(total / 30))  # 默认每页30条记录

    for page_count in range(1, page_num + 1):
        res = aliyun_rds.infos('cn-qingdao', page_count)

        for instance in res['Items']['DBInstance']:
            rds = RDS.objects.filter(instance_id=instance['DBInstanceId']).first()
            if rds:
                rds.region_id = instance['RegionId']
                rds.description = instance['DBInstanceDescription']
                rds.status = instance['DBInstanceStatus']
                rds.save()
            else:
                rds = RDS.objects.create(
                    instance_id=instance['DBInstanceId'],
                    region_id=instance['RegionId'],
                    description=instance['DBInstanceDescription'],
                    status=instance['DBInstanceStatus'],
                )
