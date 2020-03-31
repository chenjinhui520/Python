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

class Metric(object):

    def __init__(self):
        self.client = boto3.client('cloudwatch')

    def put_ec2_metric(self, instance_id):
        response = self.client.put_metric_alarm(
            # 警报名称
            AlarmName = 'StatusCheckFailed-Alarm',
            # 警报描述
            AlarmDescription = 'Automatic recovery of system status check failure',
            # 状态改变时是否执行动作
            ActionsEnabled = True,
            # 恢复状态
            #OKActions = [
            #    'arn:aws:sns:ap-southeast-1:406329597408:sns-ec2'
            #]
            # 警报状态
            AlarmActions = [
                'arn:aws:automate:ap-south-1:ec2:recover'
            ],
            # 数据不足状态
            #InsufficientDataActions = [
            #    'arn:aws:sns:ap-southeast-1:406329597408:sns-ec2'
            #],
            # 指标名称
            MetricName = 'StatusCheckFailed_System',
            # 名称空间
            Namespace = 'AWS/EC2',
            # 指标的统计方式
            Statistic = 'Maximum',
            # 资源信息
            Dimensions = [
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            # 收集指标所需花费的时间，单位秒
            Period = 300,
            # 统计单位
            Unit = 'Count',
            # 评估周期
            EvaluationPeriods = 2,
            # 此参数可以去掉
            #DatapointsToAlarm = 5,
            # 触发警报的阈值
            Threshold = 1,
            # 用于比较的算数运算符
            ComparisonOperator = 'GreaterThanOrEqualToThreshold',
            # 设置警报如何处理丢失的数据点，采用默认值即可
            #TreatMissingData = 'missing',
            # 仅用于基于百分位的警报
            #EvaluateLowSampleCountPercentile = '',
            # 此参数用不到，可以忽略
            #ThresholdMetricId = ''
        )
        return response



if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    instance_id = str(input('请输入实例ID：')).strip().lower()
    metric = Metric()
    resp = metric.put_ec2_metric(instance_id)
    print(resp)
