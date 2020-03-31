import re
import time
import json
from ec2_network_util import GetEc2Module, get_region, write_region_conf


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    ips = str(input('请输入服务器 IP 列表：')).strip().lower()
    ips = re.sub(r'\s', '', ips).split(',')
    module = GetEc2Module()
    instance_ids = module.get_instance_ids(ips)
    for instance_id in instance_ids:
        try:
            module.modify_s3_iam(instance_id)
        except Exception as error:
            print(error)
