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


class RegisterTarget(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.ec2_client = boto3.client('ec2')

    def register_target(self, target_group_arn, targets):
        response = self.elb_client.register_targets(
            TargetGroupArn = target_group_arn,
            Targets = targets
        )

    def deregister_target(self, target_group_arn, targets):
        response = self.elb_client.deregister_targets(
            TargetGroupArn = target_group_arn,
            Targets = targets
        )

    def get_lb_arn(self, lb_names):
        response = self.elb_client.describe_load_balancers(Names = lb_names)
        lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
        return lb_arns[0]

    def get_target_type(self, lb_arn):
        target_dict = {}
        response = self.elb_client.describe_target_groups(LoadBalancerArn = lb_arn)
        target_type = response['TargetGroups'][0]['TargetType']
        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        target_dict['target_type'] = target_type
        target_dict['target_group_arn'] = target_group_arn
        return target_dict

    def get_instance_ids(self, ips):
        response = self.ec2_client.describe_instances(
            Filters = [
                {
                    'Name': 'private-ip-address',
                    'Values': ips
                }
            ]
        )
        instance_ids = [ j['InstanceId'] for i in response['Reservations'] for j in i['Instances'] ]
        if len(instance_ids) < len(ips):
            print('部分IP不存在，请查证！')
        return instance_ids

    @staticmethod
    def get_ip_targets(ips, port):
        targets = []
        for ip in ips:
            target = {}
            target['Id'] = ip
            target['Port'] = port
            targets.append(target)
        return targets

    @staticmethod
    def get_instance_targets(instance_ids, port):
        targets = []
        for instance_id in instance_ids:
            target = {}
            target['Id'] = instance_id
            target['Port'] = port
            targets.append(target)
        return targets



if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    lb_names = str(input('请输入要注册的负载均衡名称：')).strip()
    lb_names = re.sub(r'-\d{8,10}\.\w{2}-\w{4,9}-\d\.elb\.amazonaws\.com', '', lb_names)
    lb_names = re.sub(r'internal-', '', lb_names)
    lb_names = re.sub(r'-\w{16}\.elb\.\w{2}-\w{4,9}-\d\.amazonaws\.com', '', lb_names).split(',')
    mode = str(input('注册/反注册，Y/N：')).strip().upper()
    ips = str(input('请输入后端服务器 IP 列表：')).strip().lower()
    ips = re.sub(r'\s', '', ips).split(',')
    port = int(str(input('请输入后端侦听端口：')).strip().lower())
    slb = RegisterTarget()
    lb_arn = slb.get_lb_arn(lb_names)
    target_type = slb.get_target_type(lb_arn)['target_type']
    target_group_arn = slb.get_target_type(lb_arn)['target_group_arn']
    if target_type == 'ip':
        targets = slb.get_ip_targets(ips, port)
    elif target_type == 'instance':
        instance_ids = slb.get_instance_ids(ips)
        targets = slb.get_instance_targets(instance_ids, port)
    if mode == 'Y':
        slb.register_target(target_group_arn, targets)
    elif mode == 'N':
        slb.deregister_target(target_group_arn, targets)
