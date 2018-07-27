from ssh_client_utils.myparamiko import MyParamiko

client = MyParamiko('ssh.conf')

client.connect()

print(client.exec_cmd('date'))
print(client.list_dir('/usr/local/nginx'))

# client.get_file('/usr/local/maven.tar.gz', 'D:/get/maven.tar.gz')

# client.dis_sftp_connect()
client.dis_client_connect()
