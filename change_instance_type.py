import re
import time
from ec2_network_util import GetEc2Module, get_region, write_region_conf


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    ips = str(input('请输入服务器 IP 列表：')).strip()
    ips = re.sub(r'\s', '', ips).split(',')
    module = GetEc2Module()
    instance_ids = module.get_instance_ids(ips)
    for instance_id in instance_ids:
        module.stop_ec2([instance_id])
        while True:
            ec2_info = module.get_instance_status([instance_id])
            status = ec2_info['status']
            old_instance_type = ec2_info['old_instance_type']
            if status == 'stopped':
                print('The current {} model is：{}'.format(instance_id, old_instance_type))
                instance_type = module.get_model()
                module.modify_instance_type(instance_id, instance_type)
                module.start_ec2([instance_id])
                break
            else:
                print('The current running status of the {} is：{}'.format(instance_id, status))
            time.sleep(10)
