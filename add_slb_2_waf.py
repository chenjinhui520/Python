import boto3
import math
import json
import datetime
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

class ModifyWaf(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.waf_client = boto3.client('waf-regional')

    def get_lb_arn(self, lb_names):
        response = self.elb_client.describe_load_balancers(Names = lb_names)
        lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
        return lb_arns

    @staticmethod
    def get_txt():
        with open('/tmp/dns.txt', 'r') as t:
            lb_names = t.read().splitlines()
        return lb_names

    def add_alb_2_waf(self, web_acl_id, lb_arn):
        response = self.waf_client.associate_web_acl(WebACLId = web_acl_id, ResourceArn = lb_arn)

    def del_alb_2_waf(self, lb_arn):
        response = self.waf_client.disassociate_web_acl(ResourceArn = lb_arn)

    def del_web_acl(self, web_acl_id, token):
        response = self.waf_client.delete_web_acl(WebACLId = web_acl_id, ChangeToken = token)

    def get_token(self):
        response = self.waf_client.get_change_token()
        return response['ChangeToken']

    def list_rule(self):
        response = self.waf_client.list_rules(Limit = 100)
        rule_ids = [ i['RuleId'] for i in response['Rules'] ]
        return rule_ids

    def delete_rule(self, rule_id, tocken):
        response = self.waf_client.delete_rule(RuleId = rule_id, ChangeToken = token)

    def list_regex(self):
        response = self.waf_client.list_regex_match_sets()
        regexs = [ i['RegexMatchSetId'] for i in response['RegexMatchSets'] ]
        return regexs

    def del_regex(self, regex, token):
        response = self.waf_client.delete_regex_match_set(RegexMatchSetId = regex, ChangeToken = token)

if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    #module = GetEc2Module()
    #web_acl_id = str(input('请输入 WEB ACL ID：')).strip()
    lb_arn = str(input('请输入 LB_ARN：')).strip()
    waf = ModifyWaf()
    waf.del_alb_2_waf(lb_arn)
    #token = waf.get_token()
    #rule_ids = waf.list_rule()
    #regexs = waf.list_regex()
    #for regex in regexs:
    #    waf.del_regex(regex, token)
#    for rule_id in rule_ids:
#        waf.delete_rule(rule_id, token)
#    waf.del_web_acl(web_acl_id, tocken)
#    lb_names = waf.get_txt()
#    max_num = 20
#    num_sum = len(lb_names)/max_num
#    num_sum = math.ceil(num_sum)
#    for index in range(num_sum):
#        start = index * max_num
#        end = (index + 1) * max_num
#        lb_arns = waf.get_lb_arn(lb_names[start:end])
#        for lb_arn in lb_arns:
#            lb_arn = str(lb_arn)
#            try:
#                waf.add_alb_2_waf(web_acl_id, lb_arn)
#            except Exception as error:
#                print(error)
