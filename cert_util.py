import boto3
import json
import datetime
from ec2_network_util import GetEc2Module, get_region, write_region_conf


class Certificate(object):

    def __init__(self):
        self.client = boto3.client('acm')

    def get_cert(self):
        response = self.client.list_certificates(MaxItems = 100)
        cert_dict = {}
        domain_list = [ i['DomainName'] for i in response['CertificateSummaryList'] ]
        cert_list = response.get('CertificateSummaryList')
        for cert in cert_list:
            cert_dict[cert['DomainName']] = cert['CertificateArn']
        for index, domain_name in enumerate(domain_list):
            print('{})  {}'.format(index, domain_name))
        cert_index = int(input('请输入要选择的证书索引：').strip())
        cert_arn = cert_dict[domain_list[cert_index]]
        return cert_arn

    def describe_cert(self, cert_arn):
        response = self.client.describe_certificate(CertificateArn = cert_arn)
        sub_domains = response['Certificate']['SubjectAlternativeNames']
        return sub_domains


if __name__ == '__main__':
    region = get_region()
    write_region_conf(region)
    module = GetEc2Module()
    cert = Certificate()
    cert_arn = cert.get_cert()
    sub_domains = cert.describe_cert(cert_arn)
    for sub_domain in sub_domains:
        print(sub_domain)
