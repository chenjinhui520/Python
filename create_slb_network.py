import boto3
import json
import datetime
import re
import configparser
import time
import sys
from ec2_network_util import GetEc2Module, get_region, write_region_conf
from biz_util import get_biz_data, get_lb_name
from cert_util import Certificate


class CreateSlb(object):

    def __init__(self):
        self.client = boto3.client('elbv2')

    def create_slb(self, **kwargs):
        response = self.client.create_load_balancer(
                                                        Name = lb_name,
                                                        Subnets = subnet_ids,
                                                        Scheme = scheme,
                                                        Type = 'network',
                                                        IpAddressType = 'ipv4',
                                                        Tags = [
                                                            {
                                                                'Key': 'biz',
                                                                'Value': biz
                                                            },
                                                            {
                                                                'Key': 'biz_id',
                                                                'Value': biz_id
                                                            },
                                                            {
                                                                'Key': 'department',
                                                                'Value': department
                                                            },
                                                            {
                                                                'Key': 'department_id',
                                                                'Value': department_id
                                                            }
                                                        ]
        )

        lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        return lb_arn

    def create_listen(self, **kwargs):
        response = self.client.create_listener(
                                                   LoadBalancerArn = lb_arn,
                                                   Protocol = protocol,
                                                   Port = port,
                                                   DefaultActions = [
                                                       {
                                                         'Type': 'forward',
                                                         'TargetGroupArn': target_group_arn
                                                       }
                                                   ]
        )

    def create_target_group(self, **kwargs):
        response = self.client.create_target_group(
                                                       Name = lb_name,
                                                       Protocol = protocol,
                                                       Port = backend_listen_port,
                                                       VpcId = vpc_id,
                                                       HealthCheckProtocol = heal_protocol,
                                                       HealthCheckPort = 'traffic-port',
                                                       HealthCheckEnabled = True,
                                                       HealthCheckIntervalSeconds = 30,
                                                       HealthyThresholdCount = 2,
                                                       UnhealthyThresholdCount = 2,
                                                       TargetType = target_type
        )
        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        return target_group_arn

    def register_target(self, **kwargs):
        response = self.client.register_targets(
                                                    TargetGroupArn = target_group_arn,
                                                    Targets = targets
        )

    def get_lb_info(self, lb_names):
        lb_info = {}
        response = self.client.describe_load_balancers(Names = lb_names)
        vpc_id = response['LoadBalancers'][0]['VpcId']
        subnet_ids = [ j['SubnetId'] for i in response['LoadBalancers'] for j in i['AvailabilityZones'] ]
        lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        dns_name = response['LoadBalancers'][0]['DNSName']
        lb_info['vpc_id'] = vpc_id
        lb_info['subnet_ids'] = subnet_ids
        lb_info['lb_arn'] = lb_arn
        lb_info['dns_name'] = dns_name
        return lb_info

    @staticmethod
    def get_targets(ids):
        targets = []
        for instance in ids:
            target = {}
            target['Id'] = instance
            targets.append(target)
        return targets



if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    lb_name = get_lb_name()
    module = GetEc2Module()
    scheme = module.get_scheme()
    vpc_id = module.get_vpcs()
    az_a = region + 'a'
    zone_a_subnet_id = module.get_subnets(vpc_id, az_a)
    az_b = region + 'b'
    zone_b_subnet_id = module.get_subnets(vpc_id, az_b)
    try:
        az_c = region + 'c'
        zone_c_subnet_id = module.get_subnets(vpc_id, az_c)
        subnet_ids = [zone_a_subnet_id, zone_b_subnet_id, zone_c_subnet_id]
    except ValueError:
        subnet_ids = [zone_a_subnet_id, zone_b_subnet_id]
    protocol = str(input('请输入 LB 侦听协议，TCP/UDP/TCP_UDP/TLS：')).strip().upper()
    backend_ips = str(input('请输入后端服务器 IP 列表：')).strip().lower()
    backend_ips = re.sub(r'\s', '', backend_ips).split(',')
    instance_ids = module.get_instance_ids(backend_ips)
    if protocol == 'TCP_UDP':
        target_type = 'instance'
        ids = instance_ids
        heal_protocol = 'TCP'
    else:
        target_type = 'ip'
        ids = backend_ips
    port = int(str(input('请输入前端侦听端口：')).strip().lower())
    backend_listen_port = int(str(input('请输入后端侦听端口：')).strip().lower())
    biz = str(input('请输入一级业务分类 P：')).strip().lower()
    biz_id, department, department_id = get_biz_data(biz)
    slb = CreateSlb()
    targets = slb.get_targets(ids)
    paras = {}
    paras['lb_name'] = lb_name
    paras['subnet_ids'] = subnet_ids
    paras['scheme'] = scheme
    paras['biz'] = biz
    paras['biz_id'] = biz_id
    paras['department'] = department
    paras['department_id'] = department_id
    lb_arn = slb.create_slb(**paras)
    paras2 = {}
    paras2['lb_name'] = lb_name
    paras2['protocol'] = protocol
    paras2['heal_protocol'] = heal_protocol
    paras2['backend_listen_port'] = backend_listen_port
    paras2['vpc_id'] = vpc_id
    paras2['target_type'] = target_type
    target_group_arn = slb.create_target_group(**paras2)
    paras3 = {}
    paras3['target_group_arn'] = target_group_arn
    paras3['targets'] = targets
    slb.register_target(**paras3)
    paras4 = {}
    paras4['lb_arn'] = lb_arn
    paras4['protocol'] = protocol
    paras4['port'] = port
    paras4['target_group_arn'] = target_group_arn
    slb.create_listen(**paras4)
    print(slb.get_lb_info([lb_name])['dns_name'])
