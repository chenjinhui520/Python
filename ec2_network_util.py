import boto3
import sys
import string
import json
import requests
import re
import time
import configparser


def tryint(s):     # 将元素中的数字转换为int后再排序
    try:
        return int(s)
    except ValueError:
        return s

def str2int(v_str):     # 将元素中的字符串和数字分割开
    return [tryint(sub_str) for sub_str in re.split('([0-9]+)', v_str)]

def sort_humanly(v_list):    # 以分割后的list为单位进行排序
    new_list = sorted(v_list, key=str2int)
    tmp = [ re.split('\.', i) for i in new_list ]
    try:
        for index, i in enumerate(tmp):
            if i[1] == 'xlarge':
                new_list.remove(i[0] + '.' + i[1])
                new_list.insert(new_list.index(i[0] + '.' + '2xlarge'), i[0] + '.' + i[1])
            elif i[1] == 'large':
                new_list.remove(i[0] + '.' + i[1])
                new_list.insert(new_list.index(i[0] + '.' + '2xlarge'), i[0] + '.' + i[1])
    except IndexError:
        pass
    return new_list

def get_region():
    regions = [
        'ap-southeast-1',
        'eu-west-3',
        'ap-south-1',
        'eu-central-1'
    ]
    for index, region in enumerate(regions):
        print('{:<2d})  {}'.format(index, region))
    region_index = int(input('请输入要选择的地域索引：').strip())
    return regions[region_index]

def write_region_conf(region):
    conf = configparser.ConfigParser()
    conf.read('/root/.aws/config')
    conf.set('default', 'region', region)
    conf.write(open('/root/.aws/config', 'w'))

class GetEc2Module(object):

    def __init__(self):
        self.client = boto3.client('ec2')

    def get_vpcs(self):
        response = self.client.describe_vpcs()
        vpcs = [ j['Value'] for i in response['Vpcs'] for j in i['Tags'] if j['Key'] == 'Name' ]
        cidrs = [ i['CidrBlock'] for i in response['Vpcs'] ]
        vpc_ids = [ i['VpcId'] for i in response['Vpcs'] ]
        for index, vpc in enumerate(vpcs):
            print('{:<2d})  {:<35s}VPC网段：{}'.format(index, vpc, cidrs[index]))
        vpc_index = int(input('请输入要选择的 VPC 索引：').strip())
        return vpc_ids[vpc_index]

    def get_azs(self, **kwargs):
        response = self.client.describe_availability_zones()
        azs = [ az['ZoneName'] for az in response['AvailabilityZones'] ]
        for index, az in enumerate(azs):
            print('{:<2d})  {}'.format(index, az))
        az_index = int(input('请输入要选择的可用区索引：').strip())
        return azs[az_index]

    def get_subnets(self, vpc_id, availab_zone):
        response = self.client.describe_subnets(
            Filters = [
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id
                    ]
                },
                {
                    'Name': 'availability-zone',
                    'Values': [
                        availab_zone
                    ]
                }
            ],
            MaxResults = 500)
        subnet_dict = {}
        for subnet in response['Subnets']:
            if subnet['AvailableIpAddressCount'] > 100:
                subnet_dict[subnet['Tags'][0]['Value']] = [subnet['SubnetId'], subnet['AvailableIpAddressCount']]
        subnet_name_list = [ subnet_name_list for subnet_name_list in subnet_dict.keys() ]
        subnet_name_list.sort()
        for index, subnet_name in enumerate(subnet_name_list):
            print('{:<2d})  {:<35s}可用IP地址数：{}'.format(index, subnet_name, subnet_dict[subnet_name][1]))
        subnet_index = int(input('请输入要选择的子网索引：').strip())
        return subnet_dict[subnet_name_list[subnet_index]][0]

    def get_amis(self):
        response = self.client.describe_images(Owners = ['self'])
        amis = response['Images']
        ami_dict = {}
        for ami in amis:
            try:
                tag = [ tag['Value'] for tag in ami['Tags'] if tag['Key'] == 'Zh' ][0]
            except Exception:
                tag = 'no_tag'
            ami_dict[tag] = ami['ImageId']
        del ami_dict['no_tag']
        ami_name_list = [ ami_name_list for ami_name_list in ami_dict.keys() ]
        ami_name_list.sort()
        for index, ami_name in enumerate(ami_name_list):
            print('{:<2d})  {}'.format(index, ami_name))
        ami_index = int(input('请输入要选择的镜像索引：').strip())
        return ami_dict[ami_name_list[ami_index]]

    def get_security_group(self, vpc_id):
        sg_list = []
        target_str = 'browser-ap|rom-elb|rom-basic|ocloud-mysql|ocloud-elb|tifeng|LB-COMMON|sg_oppo_qa'
        response = self.client.describe_security_groups(
            Filters = [
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc_id
                    ]
                }
            ]
        )
        security_groups = response['SecurityGroups']
        for security_group in security_groups:
            sg_dict = {}
            sg_dict['sg_name'] = security_group['GroupName']
            sg_dict['sg_id'] = security_group['GroupId']
            for inbound in security_group['IpPermissions']:
                try:
                    inbound['IpRanges'] = [ ips['CidrIp'] for ips in inbound['IpRanges'] ]
                    if inbound['IpProtocol'] == '-1':
                        inbound['IpProtocol'] = '全部'
                    elif inbound['FromPort'] == -1 or inbound['ToPort'] == -1:
                        inbound['Port'] = '全部'
                    elif inbound['FromPort'] == inbound['ToPort']:
                        inbound['Port'] = inbound['FromPort']
                    elif inbound['FromPort'] < inbound['ToPort']:
                        inbound['Port'] = str(inbound['FromPort']) + '-' + str(inbound['ToPort'])

                    del inbound['Ipv6Ranges']
                    del inbound['PrefixListIds']
                    del inbound['UserIdGroupPairs']
                    del inbound['FromPort']
                    del inbound['ToPort']
                except KeyError:
                    pass
            for outbound in security_group['IpPermissionsEgress']:
                try:
                    outbound['IpRanges'] = [ ips['CidrIp'] for ips in outbound['IpRanges'] ]
                    if outbound['IpProtocol'] == '-1':
                        outbound['IpProtocol'] = '全部'
                    elif outbound['FromPort'] == -1 or outbound['ToPort'] == -1:
                        outbound['Port'] = '全部'
                    elif outbound['FromPort'] == outbound['ToPort']:
                        outbound['Port'] = outbound['FromPort']
                    elif outbound['FromPort'] < outbound['ToPort']:
                        outbound['Port'] = str(outbound['FromPort']) + '-' + str(outbound['ToPort'])

                    del outbound['Ipv6Ranges']
                    del outbound['PrefixListIds']
                    del outbound['UserIdGroupPairs']
                    del outbound['FromPort']
                    del outbound['ToPort']
                except KeyError:
                    pass
            sg_dict['inbounds'] = security_group['IpPermissions']
            sg_dict['outbounds'] = security_group['IpPermissionsEgress']
            sg_list.append(sg_dict)
        sg_names = [ i['sg_name'] for i in sg_list if re.match(target_str, i['sg_name']) ]
        for index, sg_name in enumerate(sg_names):
            print('{:<2d})  {}'.format(index, sg_name))
        sg_index = int(input('请输入要选择的安全组索引：').strip())
        sg_id = [ i['sg_id'] for i in sg_list if i['sg_name'] == sg_names[sg_index] ][0]
        return sg_id

    @staticmethod
    def get_disks():
        disk_list = []
        disk_type_list = ['standard', 'sc1', 'st1', 'gp2', 'io1']
        disk_num = int(input('请输入数据磁盘的数量：').strip())
        letter_list = list(string.ascii_lowercase)[1:]
        disk_names = ['{}{}'.format('/dev/sd', letter_list[num]) for num in range(disk_num)]
        for disk_name in disk_names:
            for index, disk_type_temp in enumerate(disk_type_list):
                print('{:<2d})  {}'.format(index, disk_type_temp))
            disk_type_index = int(input('请输入要选择的磁盘类型索引：').strip())
            disk_type = disk_type_list[disk_type_index]
            if disk_type == 'io1':
                disk_io_num = int(input('请输入预配置 IO 峰值，最大比率 50:1：').strip())
            disk_size = int(input('请输入磁盘大小，单位 GB：').strip().lower())
            disk_dict = {}
            disk_dict['DeviceName'] = disk_name
            disk_dict['Ebs'] = {}
            disk_dict['Ebs']['DeleteOnTermination'] = True
            disk_dict['Ebs']['VolumeType'] = disk_type
            disk_dict['Ebs']['VolumeSize'] = disk_size
            disk_dict['Ebs']['Encrypted'] = False
            if disk_type == 'io1':
                disk_dict['Ebs']['Iops'] = disk_io_num
            disk_list.append(disk_dict)
        return disk_list

    @staticmethod
    def get_model():
        st_dict = {}
        target_str = 'a1|c1|x1|z1|c3|c4|t2|t3|m1|m2|m3|m4|r3'
        #resp = requests.get('https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/ap-southeast-1/index.json').json()
        #with open('/usr/local/conf/index.json', 'w') as f:
        #    f.write(json.dumps(resp))
        with open('/usr/local/conf/index.json', 'r') as f:
            resp = json.loads(f.read())
        body = resp['products']
        for k in body.keys():
            try:
                instance_family = body[k]['attributes']['instanceFamily']
                instance_type = body[k]['attributes']['instanceType']
                cpu = body[k]['attributes']['vcpu']
                memory = body[k]['attributes']['memory']
                storage = body[k]['attributes']['storage']
                network = body[k]['attributes']['networkPerformance']
                if all([cpu != 'NA', memory != 'NA', storage != 'NA', network != 'NA']) and not re.match(target_str, instance_type):
                    st_dict[instance_type] = {}
                    st_dict[instance_type]['instanceFamily'] = instance_family
                    st_dict[instance_type]['vcpu'] = cpu
                    st_dict[instance_type]['memory'] = memory
                    st_dict[instance_type]['storage'] = storage
                    st_dict[instance_type]['networkBandwidth'] = network
            except KeyError:
                pass

        machine_types = list(set([ i['instanceFamily'] for i in st_dict.values() ]))
        machine_types.remove('Micro instances')
        machine_types.sort()

        for index, machine_type in enumerate(machine_types):
            print('{:<2d})  {}'.format(index, machine_type))
        machine_index = int(input('请输入要选择的机型索引：').strip())
        machine_type = machine_types[machine_index]

        model_names = [ i for i in st_dict.keys() if st_dict[i]['instanceFamily'] == machine_type ]
        model_names = sort_humanly(model_names)

        for index, model_name in enumerate(model_names):
            print('{:<2d})  {:<20s} CPU: {:<10s} 内存: {:<16s} 存储: {:<30s}'.format(index, model_name, st_dict[model_name]['vcpu'], st_dict[model_name]['memory'], st_dict[model_name]['storage']))
        model_index = int(input('请输入要选择的机型索引：').strip())
        return model_names[model_index]

    @staticmethod
    def get_scheme():
        schemes = ['internet-facing', 'internal']
        for index, scheme in enumerate(schemes):
            print('{:<2d}) {}'.format(index, scheme))
        scheme_index = int(input('请选择负载均衡方案编号：').strip())
        return schemes[scheme_index]

    def modify_instance_type(self, instance_id, instance_type):
        response = self.client.modify_instance_attribute(
            InstanceId = instance_id,
            InstanceType = {
                'Value': instance_type
            }
        )

    def modify_user_data(self, instance_id):
        with open('/usr/local/conf/aws_recover.sh', 'r') as f:
            user_data = f.read()
        response = self.client.modify_instance_attribute(
            InstanceId = instance_id,
            UserData = {
                'Value': user_data
            }
        )

    def stop_ec2(self, instance_ids):
        response = self.client.stop_instances(
            InstanceIds = instance_ids
        )

    def start_ec2(self, instance_ids):
        response = self.client.start_instances(
            InstanceIds = instance_ids
        )

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

    def modify_s3_iam(self, instance_id):
        response = self.client.associate_iam_instance_profile(
            IamInstanceProfile = {
                'Arn': 'arn:aws:iam::406329597408:instance-profile/EMR-ROLE',
                'Name': 'EMR-ROLE'
            },
            InstanceId = instance_id
        )

    def get_instance_status(self, instance_ids):
        response = self.client.describe_instances(
            InstanceIds = instance_ids
        )
        ec2_info = {}
        status = [ j['State']['Name'] for i in response['Reservations'] for j in i['Instances'] ][0]
        old_instance_type = [ j['InstanceType'] for i in response['Reservations'] for j in i['Instances'] ][0]
        ec2_info['status'] = status
        ec2_info['old_instance_type'] = old_instance_type
        return ec2_info

    def modify_ebs(self, ebs_id, new_ebs_size):
        response = self.client.modify_volume(VolumeId = ebs_id, Size = new_ebs_size)
        return response

    def get_volumes(self, instance_id, old_ebs_size):
        response = self.client.describe_volumes(
            Filters = [
                {
                     'Name': 'attachment.instance-id',
                     'Values': [
                        instance_id
                     ]
                },
                {
                     'Name': 'size',
                     'Values': [
                        old_ebs_size
                     ]
                }
            ]
        )

        try:
            ebs_id = response['Volumes'][0]['VolumeId']
            return ebs_id
        except IndexError:
            print(instance_id)
        except Exception as error:
            print(error)



if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    vpc = module.get_vpcs()
    print(vpc)
