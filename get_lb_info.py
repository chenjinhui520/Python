import boto3
import json
import datetime
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

class DescribeSlb(object):

    def __init__(self):
        self.elb_client = boto3.client('elbv2')
        self.ec2_client = boto3.client('ec2')
        self.acm_client = boto3.client('acm')

    def get_lb_infos(self, next_mark = ''):
        response = self.elb_client.describe_load_balancers(PageSize = 400, Marker = next_mark)
        lb_arns = [ i['LoadBalancerArn'] for i in response['LoadBalancers'] ]
        cnames = [ i['DNSName'] for i in response['LoadBalancers'] ]
        lbs = dict(zip(lb_arns, cnames))
        lb_infos = []
        for k, v in lbs.items():
            lb_info = {}
            health = self.get_target_group_arn(k)
            target_group_arn = health['target_group_arn']
            upstream = self.get_server(target_group_arn)
            try:
                cert_arn = self.get_lb_cert_arn(k)
                cert = self.get_lb_cert(cert_arn)
            except KeyError:
                cert = 'None'
            del health['target_group_arn']
            lb_info['cname'] = v
            lb_info['cert'] = cert
            lb_info['upstream'] = upstream
            lb_info['health'] = health
            lb_infos.append(lb_info)
        try:
            next_mark = response['NextMarker']
            if next_mark:
                self.get_lb_infos(next_mark)
        except KeyError:
            pass
        for lb_info in lb_infos:
            with open('/tmp/alb_list.txt', 'a+') as f:
                f.write(json.dumps(lb_info) + '\n')
        #print(lb_infos)
        #return lb_infos

    def get_target_group_arn(self, lb_arn):
        response = self.elb_client.describe_target_groups(LoadBalancerArn = lb_arn)
        targets = response['TargetGroups'][0]
        target_group_arn = targets['TargetGroupArn']
        health_check_protocol = targets['HealthCheckProtocol']
        health_check_port = targets['HealthCheckPort']
        health_check_interval = targets['HealthCheckIntervalSeconds']
        health_check_timeout = targets['HealthCheckTimeoutSeconds']
        health_check_threshold_count = targets['HealthyThresholdCount']
        unhealth_check_threshold_count = targets['UnhealthyThresholdCount']
        try:
            health_check_path = targets['HealthCheckPath']
        except KeyError:
            health_check_path = 'None'
        health = {}
        health['target_group_arn'] = target_group_arn
        health['health_check_protocol'] = health_check_protocol
        health['health_check_port'] = health_check_port
        health['health_check_interval'] = health_check_interval
        health['health_check_timeout'] = health_check_timeout
        health['health_check_threshold_count'] = health_check_threshold_count
        health['unhealth_check_threshold_count'] = unhealth_check_threshold_count
        health['health_check_path'] = health_check_path
        return health

    def get_server(self, target_group_arn):
        server = self.elb_client.describe_target_health(TargetGroupArn = target_group_arn)
        server_ids = [ i['Target']['Id'] for i in server['TargetHealthDescriptions'] ]
        port_temp = [ i['Target']['Port'] for i in server['TargetHealthDescriptions'] ]
        if port_temp:
            port = [ i['Target']['Port'] for i in server['TargetHealthDescriptions'] ][0]
        else:
            port = 'None'
        if not server_ids:
            ips = 'None'
        elif len(server_ids[0]) < 16:
            ips = server_ids
        else:
            ips = self.get_ip(server_ids)
        upstream = {}
        upstream['ips'] = ips
        upstream['port'] = port
        return upstream

    def get_ip(self, server_ids):
        try:
            instances = self.ec2_client.describe_instances(InstanceIds = server_ids)
            ips = [ j['PrivateIpAddress'] for i in instances['Reservations'] for j in i['Instances'] ]
            return ips
        except Exception as error:
            print(error)

    def get_lb_cert_arn(self, lb_arn):
        response = self.elb_client.describe_listeners(LoadBalancerArn = lb_arn)
        cert_arn = [ i['Certificates'][0]['CertificateArn'] for i in response['Listeners'] ][0]
        return cert_arn

    def get_lb_cert(self, cert_arn):
        response = self.acm_client.describe_certificate(CertificateArn = cert_arn)
        cert = response['Certificate']['DomainName']
        return cert


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    slb = DescribeSlb()
    slb.get_lb_infos()
