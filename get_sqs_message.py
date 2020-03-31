import boto3
import math
import json
from datetime import datetime
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

class SQS(object):

    def __init__(self):
        self.client = boto3.client('sqs')
        self.ec2_client = boto3.client('ec2')

    def get_message(self, url):
        response = self.client.receive_message(
            QueueUrl = url,
            AttributeNames = [
                'All'
            ],
            MaxNumberOfMessages = 10
        )
        try:
            messages = []
            handle = [ i['ReceiptHandle'] for i in response['Messages'] ]
            region = [ json.loads(i['Body'])['region'] for i in response['Messages'] ]
            resource = [ json.loads(i['Body'])['resources'] for i in response['Messages'] ]
            service = [ json.loads(i['Body'])['detail']['service'] for i in response['Messages'] ]
            event_type = [ json.loads(i['Body'])['detail']['eventTypeCode'] for i in response['Messages'] ]
            start_time = [ json.loads(i['Body'])['detail']['startTime'] for i in response['Messages'] ]
            end_time = [ json.loads(i['Body'])['detail']['endTime'] for i in response['Messages'] ]
            for i in range(len(resource)):
                message = {}
                message['handle'] = handle[i]
                message['region'] = region[i]
                message['service'] = service[i]
                if message['service'] == 'EC2':
                    message['resource'] = self.get_ip(resource[i])
                else:
                    message['resource'] = resource[i]
                message['event_type'] = event_type[i]
                message['start_time'] = datetime.strptime(start_time[i], '%a, %d %b %Y %H:%M:%S GMT')
                message['end_time'] = datetime.strptime(end_time[i], '%a, %d %b %Y %H:%M:%S GMT')
                message['status_code'] = response['ResponseMetadata']['HTTPStatusCode']
                #if message['status_code'] == 200:
                #    self.del_message(url, message['handle'])
                messages.append(message)
        except KeyError:
            pass
        return messages

    def del_message(self, url, handle):
        response = self.client.delete_message(
            QueueUrl = url,
            ReceiptHandle = handle
        )

    def get_ip(self, instance_ids):
        response = self.ec2_client.describe_instances(InstanceIds = instance_ids)
        ips = [ j['PrivateIpAddress'] for i in response['Reservations'] for j in i['Instances'] ]
        return ips


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    sgp_ec2_url = 'https://sqs.ap-southeast-1.amazonaws.com/406329597408/SNS-BACKNOTICE'
    sgp_redis_url = 'https://sqs.ap-southeast-1.amazonaws.com/406329597408/SNS-REDIS'
    sgp_rds_url = 'https://sqs.ap-southeast-1.amazonaws.com/406329597408/SQS-RDS'
    eu_3_ec2_url = 'https://sqs.eu-west-3.amazonaws.com/406329597408/SQS-EC2'
    eu_3_redis_url = 'https://sqs.eu-west-3.amazonaws.com/406329597408/SQS-REDIS'
    eu_3_rds_url = 'https://sqs.eu-west-3.amazonaws.com/406329597408/SQS-RDS'
    sqs = SQS()
    sgp_ec2_messages = sqs.get_message(sgp_ec2_url)
    sgp_redis_messages = sqs.get_message(sgp_redis_url)
    sgp_rds_messages = sqs.get_message(sgp_rds_url)
    eu_3_ec2_messages = sqs.get_message(eu_3_ec2_url)
    eu_3_redis_messages = sqs.get_message(eu_3_redis_url)
    eu_3_rds_messages = sqs.get_message(eu_3_rds_url)
    print(json.dumps(sgp_ec2_messages, cls = DateEncoder))
    print(json.dumps(sgp_redis_messages, cls = DateEncoder))
    print(json.dumps(sgp_rds_messages, cls = DateEncoder))
    print(json.dumps(eu_3_ec2_messages, cls = DateEncoder))
    print(json.dumps(eu_3_redis_messages, cls = DateEncoder))
    print(json.dumps(eu_3_rds_messages, cls = DateEncoder))
