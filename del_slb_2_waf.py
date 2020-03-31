import boto3
import json
import math
from ec2_network_util import get_region, write_region_conf


class ModifyWaf(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.waf_client = boto3.client('waf-regional')

    def get_lb_arn(self, lb_names):
        try:
            response = self.elb_client.describe_load_balancers(Names = lb_names)
            lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
            return lb_arns
        except Exception:
            pass

    @staticmethod
    def get_txt():
        with open('/tmp/dns.txt', 'r') as t:
            lb_names = t.read().splitlines()
        return lb_names

    def del_alb_2_waf(self, lb_arn):
        response = self.waf_client.disassociate_web_acl(ResourceArn = lb_arn)


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    waf = ModifyWaf()
    lb_names = waf.get_txt()
    max_num = 20
    num_sum = len(lb_names)/max_num
    num_sum = math.ceil(num_sum)
    for index in range(num_sum):
        start = index * max_num
        end = (index + 1) * max_num
        lb_arns = waf.get_lb_arn(lb_names[start:end])
        if lb_arns:
            for lb_arn in lb_arns:
                lb_arn = str(lb_arn)
                waf.del_alb_2_waf(lb_arn)
