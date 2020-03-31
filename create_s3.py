import boto3
import json
import datetime
import re
import configparser
from biz_util import get_biz_data
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class CreateS3(object):

    def __init__(self):
        self.client = boto3.client('s3')
        self.conf = configparser.ConfigParser()
        self.conf.read('/root/.aws/config')
        self.s3_region = self.conf.get('default', 'region')

    def create_s3(self, bucket_name, region):
        response = self.client.create_bucket(
            ACL = 'private',
            Bucket = bucket_name,
            CreateBucketConfiguration = {
                'LocationConstraint': region
            },
            ObjectLockEnabledForBucket = False
        )
        return response['Location']

    def put_s3_policy(self, bucket_name):
        policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AddPerm",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Action": "s3:GetObject",
                            "Resource": "arn:aws:s3:::%s/*"%(bucket_name)
                        }
                    ]
                 }
        response = self.client.put_bucket_policy(Bucket = bucket_name, Policy = json.dumps(policy))

    def put_folder(self, bucket_name):
        response = self.client.put_object(Bucket = bucket_name, Key = ('do_not_delete/' + '/'))

    def upload_file(self, bucket_name):
        with open('/usr/local/conf/test.txt', 'rb') as data:
            self.client.upload_fileobj(
                Fileobj = data,
                Bucket = bucket_name,
                Key = 'do_not_delete/test.txt',
                ExtraArgs = {
                    'ContentType': 'text/html'
                })

    def put_s3_tag(self, biz, biz_id, department, department_id, bucket):
        tags = {
            'TagSet': [
                {
                    'Key': 'biz',
                    'Value': biz
                },
                {
                    'Key': 'biz_id',
                    'Value': biz_id
                },
                {
                    'Key': 'department',
                    'Value': department
                },
                {
                    'Key': 'department_id',
                    'Value': department_id
                }
            ]
        }
        self.client.put_bucket_tagging(Bucket = bucket, Tagging = tags)


class Create_user_role(object):

    def __init__(self):
        self.client = boto3.client('iam')

    def create_user(self, user_name):
        response = self.client.create_user(UserName = user_name)

    def create_policy(self, bucket_name):
        policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "VisualEditor0",
                            "Effect": "Allow",
                            "Action": [
                                "s3:DeleteObject",
                                "s3:PutObject",
                                "s3:GetObject",
                                "s3:PutObjectAcl"
                            ],
                            "Resource": [
                                "arn:aws:s3:::%s/*"%(bucket_name),
                                "arn:aws:s3:::%s"%(bucket_name)
                            ]
                        }
                    ]
                }
        response = self.client.create_policy(PolicyName = bucket_name, PolicyDocument = json.dumps(policy))
        return response.get('Policy').get('Arn')

    def attach_policy_to_user(self, user_name, policy_arn):
        response = self.client.attach_user_policy(UserName = user_name, PolicyArn = policy_arn)

    def create_ak(self, user_name):
        response = self.client.create_access_key(UserName = user_name)
        ak = response.get('AccessKey').get('AccessKeyId')
        sk = response.get('AccessKey').get('SecretAccessKey')
        return ak, sk


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    biz = str(input('请输入一级业务分类 P：')).strip().lower()
    biz_id, department, department_id = get_biz_data(biz)
    s3_name = str(input('请输入S3资源的名称：')).strip()
    s3_name = re.sub(r'\.', '-', s3_name)
    s3 = CreateS3()
    s3.create_s3(s3_name, s3.s3_region)
    #s3.put_s3_policy(s3_name)
    s3.put_s3_tag(biz, biz_id, department, department_id, s3_name)
    s3.put_folder(s3_name)
    s3.upload_file(s3_name)
    user = Create_user_role()
    user.create_user(s3_name)
    policy_arn = user.create_policy(s3_name)
    user.attach_policy_to_user(s3_name, policy_arn)
    ak, sk = user.create_ak(s3_name)
    endpoint = 's3.' + s3.s3_region + '.amazonaws.com' + '/' + s3_name + '/'
    print(s3_name)
    print(ak)
    print(sk)
    print(s3.s3_region)
    print(endpoint)
