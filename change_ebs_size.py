import re
from ec2_network_util import GetEc2Module, get_region, write_region_conf


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    ips = str(input('请输入服务器 IP 列表：')).strip()
    ips = re.sub(r'\s', '', ips).split(',')
    old_ebs_size = str(input('请输入原始磁盘容量大小：')).strip()
    new_ebs_size = int(input('请输入新磁盘容量大小：').strip())
    module = GetEc2Module()
    instance_ids = module.get_instance_ids(ips)
    for instance_id in instance_ids:
        ebs_id = module.get_volumes(instance_id, old_ebs_size)
        module.modify_ebs(ebs_id, new_ebs_size)
