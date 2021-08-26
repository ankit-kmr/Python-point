import paramiko
import os

LocalPath = 'C:\\Users\\Ankit\\Desktop\\Python Programs\\Basics\\Practice Work\\Win-VM\\RemoteFile_sample.txt'
RemotePath = 'C:\\Users\\Ankit-PC\\Desktop\\SampleFiles\\RemoteFile_sample.txt'

try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname='192.168.29.35',username='ankit-pc',password='Test@123' ,port = 22)

    ftp_client=ssh_client.open_sftp()

    print("connected !!!")
    
    print('>>> Copying file from {0} to {1} '.format(RemotePath , LocalPath))
    ftp_client.get(RemotePath,LocalPath)
    
    ftp_client.close()
    ssh_client.close()
    
except paramiko.AuthenticationException as e:
    print(str(e))
