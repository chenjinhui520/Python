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
        module.stop_ec2([instance_id])
        while True:
            status = module.get_instance_status([instance_id])['status']
            if status == 'stopped':
                #module.modify_user_data(instance_id)
                module.start_ec2([instance_id])
                break
            else:
                print('The current running status of the {} is：{}'.format(instance_id, status))
            time.sleep(10)
