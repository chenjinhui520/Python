import paramiko
import configparser


class MyParamiko(object):
    def __init__(self, file):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.conf = configparser.ConfigParser()
        self.conf.read(file, encoding='utf-8')
        self.transport = paramiko.Transport(self.conf.get('ssh', 'hostname'), self.conf.getint('ssh', 'port'))
        self.transport.connect(username=self.conf.get('ssh', 'username'), password=self.conf.get('ssh', 'password'))
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def connect(self):
        self.client.connect(
            hostname=self.conf.get('ssh', 'hostname'),
            port=self.conf.getint('ssh', 'port'),
            username=self.conf.get('ssh', 'username'),
            password=self.conf.get('ssh', 'password'),
            timeout=self.conf.getint('ssh', 'timeout')
        )

    def exec_cmd(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode()

    def get_file(self, RemotePath, LocalPath):
        return self.sftp.get(remotepath=RemotePath, localpath=LocalPath)

    def put_file(self, LocalPath, RemotePath):
        return self.sftp.put(localpath=LocalPath, remotepath=RemotePath)

    def list_dir(self, RemoteDirPath):
        return self.sftp.listdir(RemoteDirPath)

    def create_dir(self, RemoteDirPath):
        return self.sftp.mkdir(RemoteDirPath)

    def remove_dir(self, RemoteDirPath):
        return self.sftp.rmdir(RemoteDirPath)

    def remove_file(self, FilePath):
        return self.sftp.remove(FilePath)

    def rename_dir_or_file(self, OldPath, NewPath):
        return self.sftp.rename(OldPath, NewPath)

    def dis_sftp_connect(self):
        self.sftp.close()
        print('sftp 连接已关闭')

    def dis_client_connect(self):
        self.client.close()
        print('client 连接已关闭')



