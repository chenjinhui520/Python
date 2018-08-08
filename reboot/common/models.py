from reboot.common.dbutils import MySQLconnection
import time
import paramiko

class Performs(object):

    # msg = {u'ip': u'192.168.0.3', u'ram': 31.810766721044047,
    # u'cpu': 2.9000000000000057, u'time': u'2018-02-10 18:30:11'}

    @classmethod
    def add(cls, msg):
        _ip = msg.get('ip')
        _cpu = msg.get('cpu')
        _ram = msg.get('ram')
        _time = msg.get('time')
        sql = 'insert into performs(ip,cpu,ram,time) values(%s,%s,%s,%s)'
        MySQLconnection.execute_sql1(sql, args=(_ip, _cpu, _ram, _time), fetch=False)

    @classmethod
    def get_list(cls, ip):
        _sql = 'select cpu,ram,time from performs where ip=%s and time >= %s order by time asc'
        _args = (ip, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 3600)))
        _count, _rt_list = MySQLconnection.execute_sql1(_sql, args=_args, fetch=True)
        datetime_list = []
        cpu_list = []
        ram_list = []
        for _cpu, _ram, _time in _rt_list:
            cpu_list.append(_cpu)
            ram_list.append(_ram)
            datetime_list.append(_time.strftime('%H:%M:%S'))
        return datetime_list, cpu_list, ram_list

# 远程执行命令类
class Ssh(object):
    def __init__(self, host, cmds):
        self.__host = host
        self.__cmds = cmds
        self.__port = 22
        self.__username = 'vagrant'
        self.__password = 'vagrant'

    def ssh_execute(self):
        _rt_list = []
        ssh = paramiko.SSHClient()
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.__host, self.__port, self.__username, self.__password, timeout=2)
            for _cmd in self.__cmds:
                stdin, stdout, stderr = ssh.exec_command(_cmd)
                _rt_list.append([_cmd, stdout.read(), stderr.read()])
        except BaseException as e:
            print(e)
        finally:
            ssh.close()
        return _rt_list



