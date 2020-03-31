import boto3
import sys
import string
import json
import time
import re
from biz_util import get_biz_data
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class Ebs(object):

    def __init__(self):
        self.ec2 = boto3.client('ec2')

    def create_ebs(self, **kwargs):
        response = self.ec2.create_volume(
            AvailabilityZone=availab_zone,
            Encrypted=False,
            Size=size,
            VolumeType='st1',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [
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
                }
            ]
        ) 
        return response['VolumeId']

    def attach_ebs(self, **kwargs):
        response = self.ec2.attach_volume(
            Device=device_name,
            InstanceId=instance_id,
            VolumeId=ebs_id,
        ) 


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    biz = str(input('请输入一级业务分类 P：')).strip().lower()
    biz_id, department, department_id = get_biz_data(biz)
    ips = str(input('请输入服务器 IP 列表：')).strip().lower()
    ips = re.sub(r'\s', '', ips).split(',')
    size = int(input('请输入磁盘大小：').strip())
    device_name = '/dev/sdd'
    module = GetEc2Module()
    ebs = Ebs()
    availab_zone = module.get_azs()
    instance_ids = module.get_instance_ids(ips)
    paras = {}
    paras2 = {}
    for instance_id in instance_ids:
        paras['availab_zone'] = availab_zone
        paras['size'] = size
        paras['biz'] = biz
        paras['biz_id'] = biz_id
        paras['department'] = department
        paras['department_id'] = department_id
        ebs_id = ebs.create_ebs(**paras)
        paras2['instance_id'] = instance_id
        paras2['ebs_id'] = ebs_id
        paras2['device_name'] = device_name
        time.sleep(10)
        ebs.attach_ebs(**paras2)
