import os,sys,configparser


if __name__ == '__main__':
    config_PATH = os.path.join(os.path.dirname(__file__),'Setup.conf')
    config = configparser.ConfigParser()
    config.read(config_PATH)

    HostIP = config['WindowHost']['HostIP']
    UserName = config['WindowHost']['UserName']
    Password = config['WindowHost']['Password']
    Port = config['WindowHost']['Port']
    
    Remote_Dir = 'C:\\Users\\Ankit-PC\\Desktop\\SampleFiles\\RemoteDir'
    