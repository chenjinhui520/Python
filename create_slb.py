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
                                                        SecurityGroups = security_groups,
                                                        Scheme = scheme,
                                                        Type = 'application',
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

        lb_arn = response.get('LoadBalancers')[0].get('LoadBalancerArn')
        return lb_arn

    def create_https_listen(self, lb_arn, target_group_arn, cert_arn):
        response = self.client.create_listener(
                                                   LoadBalancerArn = lb_arn,
                                                   Protocol = 'HTTPS',
                                                   Port = 443,
                                                   SslPolicy = 'ELBSecurityPolicy-TLS-1-2-2017-01',
                                                   Certificates = [
                                                       {
                                                         'CertificateArn': cert_arn
                                                       }
                                                   ],
                                                   DefaultActions = [
                                                       {
                                                         'Type': 'forward',
                                                         'TargetGroupArn': target_group_arn
                                                       }
                                                   ]
        )

    def create_http_listen(self, lb_arn, target_group_arn):
        response = self.client.create_listener(
                                                   LoadBalancerArn = lb_arn,
                                                   Protocol = 'HTTP',
                                                   Port = 80,
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
                                                       Protocol = 'HTTP',
                                                       Port = backend_listen_port,
                                                       VpcId = vpc_id,
                                                       HealthCheckProtocol = 'HTTP',
                                                       HealthCheckPort = 'traffic-port',
                                                       HealthCheckEnabled = True,
                                                       #HealthCheckPath = health_check_path,
                                                       HealthCheckIntervalSeconds = 30,
                                                       HealthCheckTimeoutSeconds = 5,
                                                       HealthyThresholdCount = 2,
                                                       UnhealthyThresholdCount = 2,
                                                       Matcher = {
                                                           'HttpCode': '200-499'
                                                       },
                                                       TargetType = 'ip'
        )
        target_group_arn = response.get('TargetGroups')[0].get('TargetGroupArn')
        return target_group_arn

    def register_target(self, target_group_arn, targets):
        response = self.client.register_targets(
                                                    TargetGroupArn = target_group_arn,
                                                    Targets = targets
        )

    def get_lb_info(self, lb_names):
        lb_info = {}
        response = self.client.describe_load_balancers(Names = lb_names)
        vpc_id = response['LoadBalancers'][0]['VpcId']
        subnet_ids = [ j['SubnetId'] for i in response['LoadBalancers'] for j in i['AvailabilityZones'] ]
        security_groups = [ i['SecurityGroups'] for i in response['LoadBalancers'] ]
        lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
        dns_name = response['LoadBalancers'][0]['DNSName']
        lb_info['vpc_id'] = vpc_id
        lb_info['subnet_ids'] = subnet_ids
        lb_info['security_groups'] = security_groups
        lb_info['lb_arn'] = lb_arn
        lb_info['dns_name'] = dns_name
        return lb_info

    @staticmethod
    def get_targets(backend_ips):
        targets = []
        for backend_ip in backend_ips:
            target = {}
            target['Id'] = backend_ip
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
    security_groups = [module.get_security_group(vpc_id)]
    backend_listen_port = int(str(input('请输入后端侦听端口：')).strip().lower())
    backend_ips = str(input('请输入后端服务器 IP 列表：')).strip().lower()
    backend_ips = re.sub(r'\s', '', backend_ips).split(',')
    #health_check_path = str(input("请输入健康检查URL：")).strip()
    biz = str(input('请输入一级业务分类 P：')).strip().lower()
    biz_id, department, department_id = get_biz_data(biz)
    slb = CreateSlb()
    targets = slb.get_targets(backend_ips)
    para1 = {}
    para1['lb_name'] = lb_name
    para1['subnet_ids'] = subnet_ids
    para1['security_groups'] = security_groups
    para1['scheme'] = scheme
    para1['biz'] = biz
    para1['biz_id'] = biz_id
    para1['department'] = department
    para1['department_id'] = department_id
    lb_arn = slb.create_slb(**para1)
    para2 = {}
    para2['lb_name'] = lb_name
    para2['backend_listen_port'] = backend_listen_port
    para2['vpc_id'] = vpc_id
    #para2['health_check_path'] = heal_check_path
    target_group_arn = slb.create_target_group(**para2)
    slb.register_target(target_group_arn, targets)
    if scheme == 'internet-facing':
        cert_object = Certificate()
        cert_arn = cert_object.get_cert()
        slb.create_https_listen(lb_arn, target_group_arn, cert_arn)
        #slb.create_http_listen(lb_arn, target_group_arn)
    elif scheme == 'internal':
        slb.create_http_listen(lb_arn, target_group_arn)
    print(slb.get_lb_info([lb_name])['dns_name'])
