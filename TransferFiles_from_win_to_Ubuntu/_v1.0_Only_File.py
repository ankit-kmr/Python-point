import paramiko
import os

Win_path = 'C:\\Users\\Ankit\\Desktop\\Shared Drive Linux\\To_ubuntu'
Linux_path = '/home/ankit/Desktop/Shared_Path'

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname='192.168.29.127',username='ankit',password='ankit@123',port=22)

ftp_client=ssh_client.open_sftp()

for filesN in os.listdir(Win_path):
    w_path = os.path.join(Win_path,filesN)
    U_path = Linux_path+'/'+filesN
    
    if os.path.isfile(w_path):
        print('>>> Tranferring " {2} " from {0} to {1} '.format(w_path , U_path ,filesN))
        ftp_client.put(w_path,U_path)

ftp_client.close()
ssh_client.close()
