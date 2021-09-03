import pysvn
import os ,time
import sys
from AutoCheckout_Setup import SvnSetup
import logging
import pyodbc
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket


class AutoCheckout:

    def setup_logger(self,name, log_file, level=logging.INFO):
        """Function setup as many loggers as you want"""

        handler = logging.FileHandler(log_file)        
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        console = logging.StreamHandler()
        console.setLevel(level)
        logging.getLogger('').addHandler(console)
        logger.addHandler(handler)
        
        return logger

    #---------------------------------------------------------------------------
    def py_Connect_MSSQL(self):
        conct = pyodbc.connect(Driver='{SQL Server}',
                        Server='Xeon-s8',
                        Database='controlTeam_Prod_DB',
                        Trusted_Connection='yes',
                        autocommit=True)
        return  conct 

    #---------------------------------------------------------------------------
    def fn_DirectoryCheckout(self,Folder , Path ,SVNpath):
        
        global vErrFound

        if os.path.exists(Path+'\\'+Folder) and len(os.listdir(Path+'\\'+Folder))< 3:
            shutil.rmtree(Path+'\\'+Folder)
            LOGGER.info('Empty Dir removed >> '+Path+'\\'+Folder+'\n')

        if not os.path.exists(Path+'\\'+Folder):

            os.makedirs(Path+'\\'+Folder) # Creating Folder if not exists
            LOGGER.info('..New Direcory Created..')
            LOGGER.info('Dir>> '+Path+'\\'+Folder)

            # Taking SVN Checkout ...............
            try:
                Checkout ='svn checkout --depth immediates "[SvnLoc]" "[dirLoc]"'
                Checkout=Checkout.replace('[SvnLoc]',SVNpath)
                Checkout=Checkout.replace('[dirLoc]',Path+'\\'+Folder)
                LOGGER.info('SVN Checkout >>> '+Checkout+'\n')

                os.system(Checkout)
                LOGGER.info('>>> Checkout Done <<<')

                LOGGER.info('** Updating Core **')
                UPDCore ='svn update --set-depth infinity mom-empty "[corePath]"'
                UPDCore=UPDCore.replace('[corePath]',Path+'\\'+Folder+'\\Core')
                LOGGER.info(UPDCore)
                os.system(UPDCore)

                LOGGER.info('** Updating Reporting **')
                UPDRpt ='svn update --set-depth infinity mom-empty "[RptPath]"'
                UPDRpt=UPDRpt.replace('[RptPath]',Path+'\\'+Folder+'\\Reporting')
                LOGGER.info(UPDRpt)
                os.system(UPDRpt)

            except Exception as e:
                LOGGER.info('SVN RT_ERROR >>> '+str(e)+'\n')


                shutil.rmtree(Path+'\\'+Folder)
                LOGGER.info('Dir removed>> '+Path+'\\'+Folder+'\n')
                vErrFound =1
                pass

        else:
            LOGGER.info('..Directory already Exists['+Folder+']..\n')
            try:
                LOGGER.info('..Cleanup Core started..')
                UPDCore ='svn cleanup "[corePath]"'
                UPDCore=UPDCore.replace('[corePath]',Path+'\\'+Folder+'\\Core')
                LOGGER.info(UPDCore)
                os.system(UPDCore)

                LOGGER.info('..Cleanup Reporting started..')
                UPDRpt ='svn cleanup "[RptPath]"'
                UPDRpt=UPDRpt.replace('[RptPath]',Path+'\\'+Folder+'\\Reporting')
                LOGGER.info(UPDRpt)
                os.system(UPDRpt)

            except Exception as e:
                LOGGER.info('Cleanup RT_ERROR >>> '+str(e)+'\n')
                pass


            try:
                LOGGER.info('** Updating Core **')
                UPDCore ='svn update --set-depth infinity mom-empty "[corePath]"'
                UPDCore=UPDCore.replace('[corePath]',Path+'\\'+Folder+'\\Core')
                LOGGER.info(UPDCore)
                os.system(UPDCore)

                LOGGER.info('** Updating Reporting **')
                UPDRpt ='svn update --set-depth infinity mom-empty "[RptPath]"'
                UPDRpt=UPDRpt.replace('[RptPath]',Path+'\\'+Folder+'\\Reporting')
                LOGGER.info(UPDRpt)
                os.system(UPDRpt)
            
            except Exception as e:
                LOGGER.info('SVN RT_ERROR >>> '+str(e)+'\n')
                pass

    # ------------------------------------------------------------------------------
    def fn_Alertmailgenerator(self,HostName,LogFileName,Status):
            
            SERVER="<.outlook.com>"

            # me = 'ankit.kumar@corecard.com'
            # address_book = ['ankit.kumar@corecard.com'] #controlteam@corecard.com 'rbhargava@corecard.com','rahul.kumar@corecard.com'

            if Status == 0:
                header='<h4 style="color:green;">[SVN_AUTOMATED_CHECKOUT]_[SUCCESS]</h4>'
            else:
                header='<h4 style="color:red;">[SVN_AUTOMATED_CHECKOUT]_[FAILURE]</h4>'
            # Create message container - the correct MIME type is multipart/alternative.
            msg = MIMEMultipart()
            msg['Subject'] = "[ZERO1_SVN_AutoCheckout_RunningALERT]"
            msg['From'] = me
            msg['To'] = ','.join(address_book)
            
            
            # Send the message via local SMTP server.
            if Status==0 :
                # Create the body of the message (a plain-text and an HTML version).
                html1 = """\
                <html>
                <head>
                <style>
                table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                height: 50px;
                }
                </style>
                </head>
                <body>

                {Header}
                <table style="width:50%">
                <tr>
                    <th>HostName</th>
                    <th>LogFileName</th> 
                    <th>Status</th>
                </tr>
                <tr style="color:blue;">
                    <td><first_data></td>
                    <td><second_data></td>
                    <td><third_data></td>

                </tr>
                </table>

                </body>
                </html>
                """
                html1=html1.replace('<first_data>',HostName)
                html1=html1.replace('<second_data>',LogFileName)
                html1=html1.replace('<third_data>','SUCCESS')
            
                html1=html1.replace('{Header}',header)

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(html1, 'html')
                msg.attach(part1)

                try:
                    s = smtplib.SMTP(SERVER)
                    s.sendmail(me, address_book, msg.as_string())
                    s.quit()   
                    LOGGER.info('\n\r** ALERT SENT SUCCESSFULLY **')
                except:
                    LOGGER.info('RT_ERROR [Alert Mail Failed]')  
            
            else:
                
                with open(vr_CurrentDir+'\\OutFiles\\ExceptionOUT.xml','r') as infile:
                    ExcpMsg =''

                    for lines in infile:
                        ExcpMsg = ExcpMsg +'<p style="color:#414E72;font-family: courier;font-size: 100%;">'+lines+ '</br></br></p>'
                        print ('ExcpMsg =='+ str(ExcpMsg))  

                html2 = """\
                <html>
                <head>
                <style>
                table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                height: 50px;
                }
                </style>
                </head>
                <body>

                {Header}
                <table style="width:50%">
                <tr>
                    <th>HostName</th>
                    <th>LogFileName</th> 
                    <th>Status</th>
                </tr>
                <tr style="color:blue;">
                    <td><first_data></td>
                    <td><second_data></td>
                    <td><third_data></td>

                </tr>
                </table>

                <h4 style="color:red;">[Exception]</h4>"""+ExcpMsg+"""

                </body>
                </html>
                """
                html2=html2.replace('<first_data>',HostName)
                html2=html2.replace('<second_data>',LogFileName)
                html2=html2.replace('<third_data>','ERROR')
            
                html2=html2.replace('{Header}',header)

                # Record the MIME types of both parts - text/plain and text/html.
                part2 = MIMEText(html2, 'html')
                msg.attach(part2)
                
                try:
                    s = smtplib.SMTP(SERVER)
                    s.sendmail(me, address_book, msg.as_string())
                    s.quit()   
                    LOGGER.info('\n\r** EXCEPTION ALERT SENT SUCCESSFULLY **')
                except:
                    LOGGER.info('RT_ERROR [Alert Mail Failed]') 

#---------------------------------------------------------------------------
Obj = AutoCheckout() 
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

LogFolder ='LOG'
vr_CurrentDir =os.getcwd()
client =pysvn.Client()
vrHostName =socket.gethostname()
vErrFound = 0

if not os.path.exists(os.path.join(vr_CurrentDir,LogFolder)):
    print('==== Creating LOG Directory ====')
    os.makedirs(os.path.join(vr_CurrentDir,LogFolder))

VSLogileName = "AutoCheckoutTool_"+time.strftime("%Y%m%d_%H%M%S")+ "." + "txt"
vs_Log_File_Name    = os.path.join( LogFolder,VSLogileName)
LOGGER = Obj.setup_logger('first_logger', vs_Log_File_Name)

LOGGER.info("==================================================================================================================")
LOGGER.info("AUTHOR : Ankit K")
LOGGER.info("DESCRIPTION : Automated SVN Checkout")
LOGGER.info("==================================================================================================================")

LOGGER.info('.................................... START TAKING UPDATES ....................................')
vr_conn=Obj.py_Connect_MSSQL()
vr_crsr=vr_conn.cursor()

vobj = SvnSetup()
BranchPath_C = vobj.BranchDir_Credit
BranchPath_P = vobj.BranchDir_Plat
PlatRlsPackagePath = vobj.PlatRelaasePackage
PlatOntopPackagePath = vobj.PlatOntopPackage
creditRlsPackagePath = vobj.CreditReleasePackage
creditontopPackagePath = vobj.CreditOntopPackage
me = vobj.SenderMailAddress
address_book= vobj.receiverMailAddress

vrBranchdir_C = {}
vrBranchdir_P = {}
vrPlatPackage ={}
vrPlatPackageOntop ={}
vrcreditPackage ={}
vrcreditPackageOntop ={}

try:
    vr_crsr.execute ("""SELECT Name ,SVN_Location FROM SVN_BranchOrPackages WITH(NOLOCK) WHERE isactive =1""")
    Fetchdata = vr_crsr.fetchall()

    for data in Fetchdata:
        if '/Branch' in data[1]:
            if 'Plat_' not in data[0]:
                vrBranchdir_C[data[0]]=data[1]
            else:
                vrBranchdir_P[data[0]]=data[1]
        
        elif '/PlatProcessingReleasePackage' in data[1]:
            vrPlatPackage[data[0]]=data[1]
        
        elif '/PlatProcessingReleasePackage_onTop' in data[1]:
            vrPlatPackageOntop[data[0]]=data[1]

        elif '/CreditProcessingReleasePackage' in data[1]:
            vrcreditPackage[data[0]]=data[1]
        
        elif '/CreditProcessingReleasePackage_onTop' in data[1]:
            vrcreditPackageOntop[data[0]]=data[1]    
   
        

    if vrBranchdir_C is not None and BranchPath_C !='':
        print(vrBranchdir_C)
        print('\n')
        for key,val in vrBranchdir_C.items():
            LOGGER.info('\n\r------Credit Branch Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , BranchPath_C ,val)
    
    if vrBranchdir_P is not None and BranchPath_P !='':
        print(vrBranchdir_P)
        print('\n')
        for key,val in vrBranchdir_C.items():
            LOGGER.info('\n\r------Plat Branch Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , BranchPath_P ,val)

    if vrPlatPackage is not None and PlatRlsPackagePath !='':
        print(vrPlatPackage)
        print('\n')
        for key,val in vrPlatPackage.items():
            LOGGER.info('\n\r------ PlatPackage Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , PlatRlsPackagePath ,val)

    if vrPlatPackageOntop is not None and PlatOntopPackagePath !='':
        print(vrPlatPackageOntop)
        print('\n')
        for key,val in vrPlatPackageOntop.items():
            LOGGER.info('\n\r------ PlatOntop Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , PlatOntopPackagePath ,val)

    if vrcreditPackage is not None and creditRlsPackagePath !='':
        print(vrcreditPackage)
        print('\n')
        for key,val in vrcreditPackage.items():
            LOGGER.info('\n\r------ CreditPackage Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , creditRlsPackagePath ,val)

    if vrcreditPackageOntop is not None and creditontopPackagePath !='':
        print(vrcreditPackageOntop)
        print('\n')
        for key,val in vrcreditPackageOntop.items():
            LOGGER.info('\n\r------ CreditOntop Checkout Started >> '+key)
            
            Obj.fn_DirectoryCheckout(key , creditontopPackagePath ,val)


except Exception as e :
    LOGGER.info('\nRT_ERROR >>> '+str(e))

LOGGER.info('.................................... STOP TAKING UPDATES ....................................')
# ***************************************************
Obj.fn_Alertmailgenerator(vrHostName,VSLogileName,vErrFound)
# ***************************************************