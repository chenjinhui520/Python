import requests
import json
import re
import time
import hashlib


class cmdb_biz_request(object):

    def __init__(self):
        self.key = 'ocloud'
        self.secret = 'fb1f26103ab544c2ba222e48f87bdac2'
        self.url = 'http://cmdb-api.ops.oppo.local/api/v1/hosts/pool/instances'
        self.timestamp = int(time.time())
        self.params = self._complete_params_sign(self.timestamp, self.key, self.secret)

    def api_request(self):
        response = requests.get(self.url, params = self.params)
        response = response.json()
        total_num = response.get('data').get('totalNum')
        hosts = response.get('data').get('hosts')
        for host in hosts:
            ip = host.get('real_ip')
            server_type = host.get('server_type')
            if host.get('server_type') == 'aws_vm':
                temp_bizs = set()
                ip = host.get('real_ip')
                bizs = host.get('fullPathList')
                if bizs:
                    for biz in bizs:
                        biz = str(biz)
                        biz = re.match(r'^\/(\w+-?)+', biz)
                        if biz:
                            biz = biz.group()
                        temp_bizs.add(biz)
                else:
                    temp_bizs = {''}
                cmdb_data = ip + ',' + str(temp_bizs)
                with open('/tmp/cmdb_ec2_list.txt', 'a+') as cmdb:
                    cmdb.write(cmdb_data + '\n')

    @staticmethod
    def _complete_params_sign(timestamp, key, secret):
        params = {}
        params['pageNo'] = 1
        params['pageSize'] = 10
        params['ts'] = timestamp
        params['appKey'] = key
        params_str = '&'.join(['%s=%s' % (k, params[k]) for k in sorted(params.keys())])
        total_str = "%s&appSecret=%s" % (params_str, secret)
        md5 = hashlib.md5()
        md5.update(total_str.encode("utf-8"))
        params['sign'] = md5.hexdigest()
        return params



if __name__ == '__main__':
    cmdb = cmdb_biz_request()
    cmdb.api_request()
