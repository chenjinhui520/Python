import time
import os
import requests
import json


SERVER_URL = 'http://127.0.0.1:8000/performs/'


def execute_cmd(cmd):
    return os.popen(cmd).read().strip()

def get_ip():
    cmd = "ifconfig eth0|sed -n '2p'|awk '{print $2}'|awk -F':' '{print $2}'"
    cxt = execute_cmd(cmd)
    return cxt

def get_cpu():
    cmd = "top -n 1|grep 'Cpu'|awk '{print $8}'"
    cxt = execute_cmd(cmd)
    return 100 - float(cxt)


'''
内存计算公式：
空闲使用率 = (free + buffer) * 100 / total
已使用率 = 100 - 空闲使用率
'''
def get_ram():
    cmd = "free -m|grep 'Mem'"
    cxt = execute_cmd(cmd)
    Mem = cxt.split()
    total = float(Mem[1])
    free = float(Mem[3])
    buffer = float(Mem[5])
    return 100 - ((free + buffer) * 100 / total)


def Result():
    _rt_dict = dict()
    _rt_dict['ip'] = get_ip()
    _rt_dict['cpu'] = get_cpu()
    _rt_dict['ram'] = get_ram()
    _rt_dict['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    return _rt_dict


def send(msg):
    try:
        requests.post(url=SERVER_URL, data=json.dumps(msg),
                      headers={'Content-Type': 'application/json',
                               'app_key': 'b67ce06839ab5a738ba42f137facc317',
                               'app_secret': 'dcba76322b0c7a92806da218ec0e56b3'})
    except Exception as e:
        print(e)
    return ''

