import boto3
import sys
import string
import time
from biz_util import get_biz_data
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class CreateEc2(object):

    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def create_instance(self, **kwargs):
        instances = self.ec2.create_instances(
            # 接口测试
            DryRun = False,
            ImageId = ami_id,
            # 实例类型,c5.large 2C4G
            InstanceType = instance_type,
            KeyName = 'nearme_keke_nso',
            # 最大启动实例数量
            MaxCount = instance_num,
            # 最小启动实例数量
            MinCount = instance_num,
            # 是否开启实例监控，另外收费，不建议开启
            Monitoring = {'Enabled': False},
            SubnetId = subnet_id,
            SecurityGroupIds = security_group_ids,
            # 实例控制台删除保护
            DisableApiTermination = True,
            # 启动 EBS 优化实例
            EbsOptimized = True,
            # IAM 角色，EMR 集群需要添加，其他不用
            #IamInstanceProfile = {'Arn': 'arn:aws:iam::406329597408:instance-profile/EMR_EC2_DefaultRole'},
            # 开启容量预留实例开关
            CapacityReservationSpecification = {
                'CapacityReservationPreference': 'open'
            },
            BlockDeviceMappings = disk_list,
            TagSpecifications = [
                {
                    'ResourceType': 'instance',
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
                },
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
        return instances

    def get_ec2_info(self, instances):
        self.ec2 = ec2
        ec2_infos = []
        for instance in instances:
            ec2_info = {}
            ip = instance.private_ip_address
            ec2_id = instance.instance_id
            ec2_info['ip'] = ip
            ec2_info['ec2_id'] = ec2_id
            ec2_infos.append(ec2_info)
        return ec2_infos

class Docker(object):

    def __init__(self):
        self.client = boto3.client('ec2')

    def create_ni(self, **kwargs):
        response = self.client.create_network_interface(
            Description = ip,
            Groups = security_group_ids,
            SecondaryPrivateIpAddressCount = sub_network_ip_num,
            SubnetId = sub_subnet_id)
        return response['NetworkInterface']['NetworkInterfaceId']

    def attach_ni(self, **kwargs):
        response = self.client.attach_network_interface(
            DeviceIndex = device_index,
            InstanceId = ec2_id,
            NetworkInterfaceId = network_interface_id)


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    vpc_id = module.get_vpcs()
    ami_id = module.get_amis()
    availab_zone = module.get_azs()
    subnet_id = module.get_subnets(vpc_id, availab_zone)
    security_group_ids = [module.get_security_group(vpc_id)]
    instance_type = module.get_model()
    biz = str(input('请输入一级业务分类 P：')).strip().lower()
    biz_id, department, department_id = get_biz_data(biz)
    instance_num = int(input('请输入需要创建的实例数量：').strip().lower())
    is_data_disk = str(input('请输入是否需要数据磁盘，Y/N：')).strip().upper()
    if is_data_disk == 'Y':
        disk_list = module.get_disks()
    elif is_data_disk == 'N':
        disk_list = []
    sub_network_num = int(input('请输入辅助网卡数量：').strip())
    sub_network_ip_num = int(input('请输入辅助网卡IP数量：').strip())
    ec2 = CreateEc2()
    paras = {}
    paras2 = {}
    paras3 = {}
    paras['ami_id'] = ami_id
    paras['instance_type'] = instance_type
    paras['instance_num'] = instance_num
    paras['subnet_id'] = subnet_id
    paras['security_group_ids'] = security_group_ids
    paras['disk_list'] = disk_list
    paras['biz'] = biz
    paras['biz_id'] = biz_id
    paras['department'] = department
    paras['department_id'] = department_id
    instances = ec2.create_instance(**paras)
    ec2_infos = ec2.get_ec2_info(instances)
    docker = Docker()
    sub_subnet_id = module.get_subnets(vpc_id, availab_zone)
    time.sleep(100)
    for ec2_info in ec2_infos:
        ip = ec2_info['ip']
        ec2_id = ec2_info['ec2_id']
        for device_index in range(1,sub_network_num):
            paras2['ip'] = ip
            paras2['sub_subnet_id'] = sub_subnet_id
            paras2['security_group_ids'] = security_group_ids
            paras2['sub_network_ip_num'] = sub_network_ip_num
            network_interface_id = docker.create_ni(**paras2)
            time.sleep(3)

            paras3['device_index'] = device_index
            paras3['ec2_id'] = ec2_id
            paras3['network_interface_id'] = network_interface_id
            docker.attach_ni(**paras3)
        print(ip)
