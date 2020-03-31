response = client.put_metric_alarm(
    # 警报名称
    AlarmName='string',
    # 警报描述
    AlarmDescription='string',
    # 更改后是否立即生效，默认值为 True
    ActionsEnabled=True|False,
    # 当警报从其他状态转变为 OK 状态所需要执行的操作
    OKActions=[
        'string',
    ],
    # 当警报从其他状态转变为 alarm 状态所需要执行的操作
    AlarmActions=[
        'string',
    ],
    # 当警报从其他状态转变为 insufficient_data 状态所需要执行的操作
    InsufficientDataActions=[
        'string',
    ],
    # 与警报关联的指标名称
    MetricName='string',
    # 命名空间
    Namespace='string',
    # 统计信息
    Statistic='SampleCount'|'Average'|'Sum'|'Minimum'|'Maximum',
    # 百分比统计
    ExtendedStatistic='string',
    # 尺寸
    Dimensions=[
        {
            'Name': 'string',
            'Value': 'string'
        },
    ],
    # 期间
    Period=123,
    # 统计的单位
    Unit='Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None',
    # 评估期
    EvaluationPeriods=123,
    # 触发警报必须违反的数据点数
    DatapointsToAlarm=123,
    # 阈值
    Threshold=123.0,
    # 比较指定的统计信息和阈值时要使用的算术运算
    ComparisonOperator='GreaterThanOrEqualToThreshold'|'GreaterThanThreshold'|'LessThanThreshold'|'LessThanOrEqualToThreshold'|'LessThanLowerOrGreaterThanUpperThreshold'|'LessThanLowerThreshold'|'GreaterThanUpperThreshold',
    # 设置此警报如何处理丢失的数据点
    TreatMissingData='string',
    # 仅用于基于百分位数的警报
    EvaluateLowSampleCountPercentile='string',
    # 指标，列表
    Metrics=[
        {
            'Id': 'string',
            'MetricStat': {
                'Metric': {
                    'Namespace': 'string',
                    'MetricName': 'string',
                    'Dimensions': [
                        {
                            'Name': 'string',
                            'Value': 'string'
                        },
                    ]
                },
                'Period': 123,
                'Stat': 'string',
                'Unit': 'Seconds'|'Microseconds'|'Milliseconds'|'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|'Percent'|'Count'|'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|'Count/Second'|'None'
            },
            'Expression': 'string',
            'Label': 'string',
            'ReturnData': True|False,
            'Period': 123
        },
    ],
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ],
    ThresholdMetricId='string'
)
