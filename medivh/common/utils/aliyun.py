# -*- coding: UTF-8 -*-

import json
from django.conf import settings
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import CreateInstanceRequest
from aliyunsdkecs.request.v20140526 import AllocatePublicIpAddressRequest
from aliyunsdkecs.request.v20140526 import DescribeInstanceStatusRequest
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from aliyunsdkecs.request.v20140526 import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526 import AuthorizeSecurityGroupRequest
from aliyunsdkslb.request.v20140515 import AddBackendServersRequest
from aliyunsdkslb.request.v20140515 import SetBackendServersRequest
from aliyunsdkrds.request.v20140815 import ModifySecurityIpsRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstanceIPArrayListRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancerAttributeRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancersRequest
from aliyunsdkrds.request.v20140815 import DescribeDBInstancesRequest
from aliyunsdkrds.request.v20140815 import DescribeSlowLogRecordsRequest


class ALiYun(object):
    def __init__(self):
        self.key_id = settings.ALIYUN_ACCESS_KEY
        self.key_secret = settings.ALIYUN_KEY_SECRET

    def get_client(self, region):
        clt = client.AcsClient(self.key_id, self.key_secret, region)
        return clt

    def json_format(self, response):
        if isinstance(response, bytes):
            response = response.decode()
        return json.loads(response)


class ECS(ALiYun):
    # 查询ecs信息
    def infos(self, region, page=1):
        clt = self.get_client(region)
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_PageNumber(page)
        result = clt.do_action_with_exception(request)
        return self.json_format(result)

    def info(self, region, instance_id):
        clt = self.get_client(region)
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_InstanceIds(json.dumps([instance_id]))
        result = self.json_format(clt.do_action(request))
        result = result['Instances']['Instance'][0]
        return result

    def create(self, region, instancetype, internetchargetype, securitygroupid, instancename, password, imageid):
        '''创建ecs实例'''
        clt = self.get_client(region)
        request = CreateInstanceRequest.CreateInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceType(instancetype)
        request.set_InternetChargeType(internetchargetype)
        request.set_InternetMaxBandwidthOut('100')
        request.set_SecurityGroupId(securitygroupid)
        request.set_InstanceName(instancename)
        request.set_Password(password)
        request.set_ImageId(imageid)
        result = self.json_format(clt.do_action(request))
        return result

    # 给安全组添加允许ip
    def authorize_security_group(self, region, security_group_id, ip):
        clt = self.get_client(region)
        request = AuthorizeSecurityGroupRequest.AuthorizeSecurityGroupRequest()
        request.set_accept_format('json')
        request.set_SecurityGroupId(security_group_id)
        request.set_IpProtocol('all')
        request.set_PortRange('-1/-1')
        request.set_SourceCidrIp(ip)
        result = self.json_format(clt.do_action(request))
        return result

    # 设置ECS实例的PublicIP
    def setip(self, region, instance_id):
        clt = self.get_client(region)
        request = AllocatePublicIpAddressRequest.AllocatePublicIpAddressRequest()
        request.set_accept_format('json')
        request.set_InstanceId(instance_id)
        ipinfo = self.json_format(clt.do_action(request))
        return ipinfo

    # 检查状态
    def status(self, region):
        clt = self.get_client(region)
        request = DescribeInstanceStatusRequest.DescribeInstanceStatusRequest()
        request.set_accept_format('json')
        statusinfo = self.json_format(clt.do_action(request))
        return statusinfo

    # 启动ECS实例
    def start(self, region, instance_id):
        clt = self.get_client(region)
        request = StartInstanceRequest.StartInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(instance_id)
        return self.json_format(clt.do_action(request))

    # 停止ECS实例
    def stop(self, region, instance_id):
        clt = self.get_client(region)
        request = StopInstanceRequest.StopInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(instance_id)
        return self.json_format(clt.do_action(request))

    # 删除实例
    def rm(self, region, instance_id):
        clt = self.get_client(region)
        request = DeleteInstanceRequest.DeleteInstanceRequest()
        request.set_accept_format('json')
        request.set_InstanceId(instance_id)
        return self.json_format(clt.do_action(request))


class SLB(ALiYun):
    # 给负载均衡添加服务器
    def add_backend_server(self, region, load_balancer_id, service_id, weight):
        clt = self.get_client(region)
        request = AddBackendServersRequest.AddBackendServersRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(load_balancer_id)
        request.set_BackendServers(json.dumps([{'ServerId': service_id, 'Weight': weight}]))
        result = json.loads(clt.do_action(request))
        return result

    def set_weight(self, region, load_balancer_id, service_id, weight):
        clt = self.get_client(region)
        request = SetBackendServersRequest.SetBackendServersRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(load_balancer_id)
        request.set_BackendServers(json.dumps([{'ServerId': service_id, 'Weight': weight}]))
        result = self.json_format(clt.do_action_with_exception(request))
        return result

    def info(self, region, load_balancer_id):
        clt = self.get_client(region)
        request = DescribeLoadBalancerAttributeRequest.DescribeLoadBalancerAttributeRequest()
        request.set_accept_format('json')
        request.set_LoadBalancerId(load_balancer_id)
        result = self.json_format(clt.do_action_with_exception(request))
        return result

    def infos(self, region):
        clt = self.get_client(region)
        request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        request.set_accept_format('json')
        result = self.json_format(clt.do_action_with_exception(request))
        return result


class RDS(ALiYun):
    # 查询rds信息
    def infos(self, region, page=1):
        clt = self.get_client(region)
        request = DescribeDBInstancesRequest.DescribeDBInstancesRequest()
        request.set_accept_format('json')
        request.set_PageNumber(page)
        result = clt.do_action_with_exception(request)
        return self.json_format(result)

    # 给rds添加ip白名单
    def get_rds_security_ip(self, region, instance_id, ip_array_name):
        clt = self.get_client(region)
        request = DescribeDBInstanceIPArrayListRequest.DescribeDBInstanceIPArrayListRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(instance_id)
        result = json.loads(clt.do_action(request))

        for item in result['Items']['DBInstanceIPArray']:
            if item['DBInstanceIPArrayName'] == ip_array_name:
                return item['SecurityIPList'].split(',')
        return result

    def add_rds_security_ip(self, region, instance_id, ips, ip_array_name):
        if not isinstance(ips, (list, set, tuple)):
            ips = [ips]
        ips = self.get_rds_security_ip(region, instance_id, ip_array_name) + ips
        clt = self.get_client(region)
        request = ModifySecurityIpsRequest.ModifySecurityIpsRequest()
        request.set_accept_format('json')
        request.set_DBInstanceId(instance_id)
        request.set_SecurityIps(','.join(ips))
        request.set_DBInstanceIPArrayName(ip_array_name)
        result = json.loads(clt.do_action(request))
        return result

    # 获取慢日志
    def get_slow_log(self, region, instance_id, start_time, end_time, page=1):
        clt = self.get_client(region)
        request = DescribeSlowLogRecordsRequest.DescribeSlowLogRecordsRequest()
        request.set_accept_format('json')
        request.set_PageNumber(page)
        request.set_DBInstanceId(instance_id)
        request.set_StartTime(start_time)
        request.set_EndTime(end_time)
        result = self.json_format(clt.do_action_with_exception(request))
        return result


aliyun_ecs = ECS()
aliyun_slb = SLB()
aliyun_rds = RDS()
