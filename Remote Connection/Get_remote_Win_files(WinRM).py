import os,sys,configparser
from winrm.protocol import Protocol

import winrm

if __name__ == '__main__':
    config_PATH = os.path.join(os.path.dirname(__file__),'Setup.conf')
    config = configparser.ConfigParser()
    config.read(config_PATH)

    HostIP = config['PyWinRM']['HostIP']
    UserName = config['PyWinRM']['AdminUser']
    Password = config['PyWinRM']['Password']
    Port = config['PyWinRM']['Port']
    
    url = "%s://%s:%s/wsman" % ('https', HostIP, 5986)
    print('Endpoint == ',url)
    
    
    Remote_Dir = input('Enter Remote Directory Path: ')
    
    #cmd = ' powershell.exe dir '+ Remote_Dir
    
    cmd = ' powershell.exe Get-Content "{0}"'.format(Remote_Dir)  # To read a file content
    print("<< Command executing >> ",cmd)
    
    ps_conn = Protocol(endpoint = url,transport = "ntlm",username = UserName,password= Password,server_cert_validation='ignore')
    shell_id = ps_conn.open_shell()
    cmd_retrnID = ps_conn.run_command(shell_id,cmd)
    std_out, std_err, status_code = ps_conn.get_command_output(shell_id, cmd_retrnID)
    ps_conn.cleanup_command(shell_id, cmd_retrnID)
    ps_conn.close_shell(shell_id)
    
    print(std_out.decode('UTF-8'))
    print(std_err.decode('UTF-8'))
    

    

    

    