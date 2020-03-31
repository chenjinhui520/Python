import boto3
import math
import json
import numpy as np
from datetime import datetime, timedelta
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

now = datetime.now()
one_day_before = now + timedelta(days = -1)
start_time = one_day_before.strftime('%Y-%m-%d %H:%M:%S')
end_time = now.strftime('%Y-%m-%d %H:%M:%S')
class Metric(object):

    def __init__(self):
        self.client = boto3.client('cloudwatch')

    def get_alb_metric(self, metric_name, lb, unit):
        response = self.client.get_metric_data(
            MetricDataQueries = [
                {
                    'Id': 'alb_count',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/ApplicationELB',
                            'MetricName': metric_name,
                            'Dimensions': [
                                {
                                    'Name': 'LoadBalancer',
                                    'Value': lb
                                }
                            ]
                        },
                        'Period': 300,
                        'Stat': 'Sum',
                        'Unit': unit
                    }
                }
            ],
            StartTime = start_time,
            EndTime = end_time
        )
        return response

    @staticmethod
    def get_txt():
        with open('/tmp/bbb.txt', 'r') as f:
            lbs = f.read().splitlines()
        return lbs


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    metric_name = 'ProcessedBytes'
    #metric_name = 'RequestCount'
    unit = 'Bytes'
    #unit = 'Count'
    metric = Metric()
    lbs = metric.get_txt()
    for lb in lbs:
        resp = metric.get_alb_metric(metric_name, lb, unit)
        data = [ int(j) for i in resp['MetricDataResults'] for j in i['Values'] ]
        if data:
            avg_value = round((np.mean(data))/1000/1000, 3)
            max_value = round(max(data)/1000/1000, 3)
            with open('/tmp/lb_req_byte.txt', 'a+') as f:
                f.write(str(avg_value) + ',' + str(max_value) + ',' + lb + '\n')
            #print(avg_value, max_value, lb)
