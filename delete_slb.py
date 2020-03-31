import boto3
import json
import datetime
import re
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DeleteSlb(object):

    def __init__(self):
        self.client = boto3.client('elbv2')

    def get_lb_arn(self, lb_names):
        response = self.client.describe_load_balancers(Names = lb_names)
        lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
        return lb_arns[0]

    def get_target_group_arn(self, lb_arn):
        response = self.client.describe_target_groups(LoadBalancerArn = lb_arn)
        target_group_arns = [ i['TargetGroupArn'] for i in response['TargetGroups'] ]
        return target_group_arns[0]

    def get_listen_arn(self, lb_arn):
        response = self.client.describe_listeners(LoadBalancerArn = lb_arn)
        listen_arns = [ i['ListenerArn'] for i in response['Listeners'] ]
        return listen_arns

    def delete_lb(self, lb_arn):
        response = self.client.delete_load_balancer(LoadBalancerArn = lb_arn)

    def delete_listen(self, listen_arn):
        response = self.client.delete_listener(ListenerArn = listen_arn)

    def delete_target_group(self, target_group_arn):
        response = self.client.delete_target_group(TargetGroupArn = target_group_arn)


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    lb_names = str(input('请输入要删除的负载均衡名称：')).strip()
    lb_names = re.sub(r'-\d{8,10}\.\w{2}-\w{4,9}-\d\.elb\.amazonaws\.com', '', lb_names)
    lb_names = re.sub(r'internal-', '', lb_names)
    lb_names = re.sub(r'-\w{16}\.elb\.\w{2}-\w{4,9}-\d\.amazonaws\.com', '', lb_names).split(',')
    slb = DeleteSlb()
    lb_arn = slb.get_lb_arn(lb_names)
    listen_arns = slb.get_listen_arn(lb_arn)
    target_group_arn = slb.get_target_group_arn(lb_arn)
    for listen_arn in listen_arns:
        slb.delete_listen(listen_arn)
    slb.delete_target_group(target_group_arn)
    slb.delete_lb(lb_arn)
