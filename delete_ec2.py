import boto3
import re
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class TerminateEc2(object):

    def __init__(self):
        self.client = boto3.client('ec2')

    def get_instance_ids(self, ips):
        response = self.client.describe_instances(
            Filters = [
                {
                    'Name': 'private-ip-address',
                    'Values': ips
                }
            ]
        )
        try:
            instance_ids = [ j['InstanceId'] for i in response['Reservations'] for j in i['Instances'] ]
        except Exception as error:
            print(error)
        return instance_ids

    def disable_termination(self, instance_ids):
        for instance_id in instance_ids:
            response = self.client.modify_instance_attribute(
                InstanceId = instance_id,
                DisableApiTermination = {
                    'Value': False
                }
            )

    def terminate_instance(self, instance_ids):
        response = self.client.terminate_instances(InstanceIds = instance_ids)

if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    ips = str(input('请输入 EC2 注销的 Ip 列表：')).strip().lower()
    ips = re.sub(r'\s', '', ips).split(',')
    ec2 = TerminateEc2()
    instance_ids = ec2.get_instance_ids(ips)
    ec2.disable_termination(instance_ids)
    ec2.terminate_instance(instance_ids)
