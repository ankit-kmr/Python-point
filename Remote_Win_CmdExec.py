import paramiko
import os,sys,re
'''
Out = stdout.read().decode('UTF-8')  # converting byte-object to string 
List = Out.split('\n')
res = [i.strip('\r').strip() for i in List]
print(res)
'''

#LocalPath = 'C:\\Users\\Ankit\\Desktop\\Python Programs\\Basics\\Practice Work\\Win-VM\\RemoteFile_sample.txt'
RemotePath = 'C:\\Users\\Ankit-PC\\Desktop\\SampleFiles'

OutFilePath = 'C:\\Users\\Ankit-PC\\Desktop\\SampleFiles\\OutFiles'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='192.168.29.35',username='ankit-pc',password='Test@123' ,port = 22)
    ftp_conn=ssh.open_sftp() # for file transfer ....
    print("connected !!!")
 
    cmd = 'dir '+ RemotePath +' > '+os.path.join(OutFilePath +'\Details_format_1.txt')
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    
    cmd = 'dir '+ RemotePath +' /s /b /o:gn > '+os.path.join(OutFilePath +'\Details_format_2.txt')
    print(cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    '''
    /S Displays files in specified directory and all subdirectories.
    /B Uses bare format (no heading information or summary).
    /O List by files in sorted order.
    Then in :gn, g sorts by folders and then files, and n puts those files in alphabetical order.
    '''
    
    ftp_conn.close()
    ssh.close()
    
except paramiko.AuthenticationException as e:
    print("Exception >>>",str(e))
    sys.exit(1)