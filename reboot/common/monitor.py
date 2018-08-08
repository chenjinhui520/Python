from reboot.common.dbutils import MySQLconnection


CNT = 1
CPU_PERCENT = 0.2
RAM_PERCENT = 50

def has_alarm(ip):
    # CPU&RAM 大于80%
    _sql = 'select cpu,ram from performs where ip=%s order by time desc limit %s'
    _args = (ip, CNT)
    count, rt_list = MySQLconnection.execute_sql1(sql=_sql, args=_args, fetch=True)
    cpu = False
    ram = False
    for _cpu, _ram in rt_list:
        if _cpu > CPU_PERCENT:
            cpu = True
        if _ram >RAM_PERCENT:
            ram = True
    return cpu, ram

def monitor():
    ip_list = ['10.0.2.15',]
    for ip in ip_list:
        cpu, ram = has_alarm(ip)
        content = ['<b>主機{ip}資源報警</b><br>'.format(ip=ip)]
        if cpu:
            content.append('CPU 告警!')
        if ram:
            content.append('RAM 告警!')
        content = ''.join(content).strip(',')
        print(content)
    return ''


if __name__ == '__main__':
    monitor()



