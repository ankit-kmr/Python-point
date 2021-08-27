import paramiko
import os,sys,configparser

def fn_connectHOST():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname = HostIP,username = UserName,password = Password ,port = Port )
    return ssh
    
    
def fn_getFilesDetails( Remote_path ):
    global HostIP , UserName , Password ,Port
    try:
        config_PATH = os.path.join(os.path.dirname(__file__),'Setup.conf')
        config = configparser.ConfigParser()
        config.read(config_PATH)

        HostIP = config['OpenSSH']['HostIP']
        UserName = config['OpenSSH']['UserName']
        Password = config['OpenSSH']['Password']
        Port = config['OpenSSH']['Port']
        
        try:
            ssh_conn = fn_connectHOST()
            print('Connected to "{0}" with User "{1}"'.format(HostIP,UserName))
        except paramiko.AuthenticationException as e:
            print(":: Authentication issue :: ",str(e))
            sys.exit(1)
            
        cmd = 'dir '+ Remote_path +' /s /b /o:gn'
        stdin, stdout, stderr = ssh_conn.exec_command(cmd)
        
        Out = stdout.read().decode('UTF-8')  # converting byte-object to string 
        Paths = Out.split('\n')
        Reslt_List = [i.strip('\r').strip() for i in Paths]
        Reslt_List = list(map(lambda item: item.replace(Remote_path,""), Reslt_List))

        print('\n\r')
        print(Reslt_List)
        print('\n\r')
             
        ssh_conn.close()
              
    except Exception as e:
        print(":: Exception Occured :: ", str(e))
        print(stderr.read())
        sys.exit(1)
    
if __name__ == '__main__':
    Remote_Dir = input('Enter Remote Directory Path: ')
    sys.exit(fn_getFilesDetails(Remote_Dir))