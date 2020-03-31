import boto3
import json
import datetime
import re
from cert_util import Certificate
from biz_util import get_lb_name
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class CreateSlb(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.ec2_client = boto3.client('ec2')

    def create_slb(self, lb_name, subnet_ids, security_group, tags):
        response = self.elb_client.create_load_balancer(
                                                        Name = lb_name,
                                                        Subnets = subnet_ids,
                                                        SecurityGroups = security_group,
                                                        Tags = tags,
                                                        Scheme = 'internet-facing',
                                                        Type = 'application',
                                                        IpAddressType = 'ipv4'
        )

        lb_arn = response.get('LoadBalancers')[0].get('LoadBalancerArn')
        return lb_arn

    def create_https_listen(self, lb_arn, cert_arn, target_group_arn):
        response = self.elb_client.create_listener(
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

    def create_target_group(self, lb_name, gw_or_backend_port, vpc_id, health_check_port, target_type):
        response = self.elb_client.create_target_group(
                                                       Name = lb_name,
                                                       Protocol = 'HTTP',
                                                       Port = gw_or_backend_port,
                                                       VpcId = vpc_id,
                                                       HealthCheckProtocol = 'HTTP',
                                                       HealthCheckPort = health_check_port,
                                                       HealthCheckEnabled = True,
                                                       HealthCheckPath = '/',
                                                       HealthCheckIntervalSeconds = 30,
                                                       HealthCheckTimeoutSeconds = 5,
                                                       HealthyThresholdCount = 2,
                                                       UnhealthyThresholdCount = 2,
                                                       Matcher = {
                                                           'HttpCode': '200-499'
                                                       },
                                                       TargetType = target_type
        )
        target_group_arn = response.get('TargetGroups')[0].get('TargetGroupArn')
        return target_group_arn

    def register_target(self, target_group_arn, targets):
        response = self.elb_client.register_targets(
                                                    TargetGroupArn = target_group_arn,
                                                    Targets = targets
        )

    def get_server(self, target_group_arn):
        response = self.elb_client.describe_target_health( TargetGroupArn = target_group_arn )
        targets = [ i['Target'] for i in response['TargetHealthDescriptions'] ]
        return targets

    def get_ip(self, server_ids):
        response = self.ec2_client.describe_instances(InstanceIds = server_ids)
        ips = set([ j['PrivateIpAddress'] for i in response['Reservations'] for j in i['Instances'] ])
        return ips

    def des_target_group(self, lb_arn):
        response = self.elb_client.describe_target_groups( LoadBalancerArn = lb_arn )
        target_group_info = {}
        target_group_info['gw_or_backend_port'] = response.get('TargetGroups')[0].get('Port')
        target_group_info['health_check_port'] = response.get('TargetGroups')[0].get('HealthCheckPort')
        target_group_info['target_group_arn'] = response.get('TargetGroups')[0].get('TargetGroupArn')
        target_group_info['target_type'] = response.get('TargetGroups')[0].get('TargetType')
        return target_group_info

    def des_vpcs(self):
        self.ec2_client.describe_vpc_endpoints()

    def get_lb_info(self, lb_names):
        lb_info = {}
        lb_response = self.elb_client.describe_load_balancers(Names = lb_names)
        vpc_id = lb_response.get('LoadBalancers')[0].get('VpcId')
        subnet_ids = [ i['SubnetId'] for i in response['LoadBalancers']['AvailabilityZones'] ]
        security_groups = [ i['SecurityGroups'] for i in response['LoadBalancers'] ]
        lb_arn = lb_response.get('LoadBalancers')[0].get('LoadBalancerArn')
        dns_name = lb_response.get('LoadBalancers')[0].get('DNSName')
        lb_info['vpc_id'] = vpc_id
        lb_info['subnet_ids'] = subnet_ids
        lb_info['security_groups'] = security_groups
        lb_info['lb_arn'] = lb_arn
        lb_info['dns_name'] = dns_name
        return lb_info

    def describe_tag(self, lb_arns):
        response = self.elb_client.describe_tags(ResourceArns = lb_arns)
        tags = response.get('TagDescriptions')[0].get('Tags')
        return tags


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    old_lb_name = str(input('请输入旧的负载均衡名称：')).strip()
    module = GetEc2Module()
    slb = CreateSlb()
    vpc_id = module.get_vpcs()
    az1 = module.get_azs()
    zone_a_subnet_id = module.get_subnets(vpc_id, az1)
    az2 = module.get_azs()
    zone_b_subnet_id = module.get_subnets(vpc_id, az2)
    try:
        az3 = module.get_azs()
        zone_c_subnet_id = module.get_subnets(vpc_id, az3)
        old_subnet_ids = [zone_a_subnet_id, zone_b_subnet_id, zone_c_subnet_id]
    except ValueError:
        old_subnet_ids = [zone_a_subnet_id, zone_b_subnet_id]
    old_security_groups = slb.get_lb_info([old_lb_name]).get('security_groups')[0]
    old_lb_arn = slb.get_lb_info([old_lb_name]).get('lb_arn')
    old_vpc_id = slb.get_lb_info([old_lb_name]).get('vpc_id')
    old_gw_or_backend_port = slb.des_target_group(old_lb_arn).get('gw_or_backend_port')
    old_health_check_port = slb.des_target_group(old_lb_arn).get('health_check_port')
    old_target_type = slb.des_target_group(old_lb_arn).get('target_type')
    old_target_group_arn = slb.des_target_group(old_lb_arn).get('target_group_arn')
    old_targets = slb.get_server(old_target_group_arn)
    old_tags = slb.describe_tag([old_lb_arn])
    new_lb_name = get_lb_name()
    new_lb_arn = slb.create_slb(new_lb_name, old_subnet_ids, old_security_groups, old_tags)
    new_target_group_arn = slb.create_target_group(new_lb_name, old_gw_or_backend_port, old_vpc_id, old_health_check_port, old_target_type)
    slb.register_target(new_target_group_arn, old_targets)
    cert_object = Certificate()
    cert_arn = cert_object.get_cert()
    slb.create_https_listen(new_lb_arn, cert_arn, new_target_group_arn)
    print(slb.get_lb_info([new_lb_name]).get('dns_name'))
