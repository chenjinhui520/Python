import boto3
import json
import datetime
import re
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DescribeSlb(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.ec2_client = boto3.client('ec2')

    def get_lb_arn(self, lb_names):
        response = self.elb_client.describe_load_balancers(Names = lb_names)
        lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
        return lb_arns

    def get_target_group_arn(self, lb_arn):
        response = self.elb_client.describe_target_groups(LoadBalancerArn = lb_arn)
        target_group_arns = [ i['TargetGroupArn'] for i in response['TargetGroups'] ]
        return target_group_arns

    def get_server(self, target_group_arn):
        response = self.elb_client.describe_target_health(TargetGroupArn = target_group_arn)
        server_ids = [ i['Target']['Id'] for i in response['TargetHealthDescriptions'] ]
        ports = set([ i['Target']['Port'] for i in response['TargetHealthDescriptions'] ])
        if len(server_ids[0]) < 16:
            ips = set(server_ids)
        else:
            ips = self.get_ip(server_ids)
        return ips, ports

    def get_ip(self, server_ids):
        response = self.ec2_client.describe_instances(InstanceIds = server_ids)
        ips = set([ j['PrivateIpAddress'] for i in response['Reservations'] for j in i['Instances'] ])
        return ips


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    lb_names = str(input('请输入要查询的负载均衡名称：')).strip()
    lb_names = re.sub(r'-\d{8,10}\.\w{2}-\w{4,9}-\d\.elb\.amazonaws\.com', '', lb_names)
    lb_names = re.sub(r'internal-', '', lb_names)
    lb_names = re.sub(r'-\w{16}\.elb\.\w{2}-\w{4,9}-\d\.amazonaws\.com', '', lb_names).split(',')
    slb = DescribeSlb()
    lb_arns = slb.get_lb_arn(lb_names)
    for lb_arn in lb_arns:
        target_group_arns = slb.get_target_group_arn(lb_arn)
        for target_group_arn in target_group_arns:
            ips, ports = slb.get_server(target_group_arn)
            print('后端 IP 列表：')
            for ip in ips:
                print(ip)
            print('后端侦听端口：')
            for port in ports:
                print(port)
