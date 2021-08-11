import pysvn
import os ,time
import sys
from Setup import SvnSetup
import logging
import pyodbc
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import socket

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
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
def py_Connect_MSSQL():
    conct = pyodbc.connect(Driver='{SQL Server}',
                      Server='Localhost',
                      Database='DBname',
                      Trusted_Connection='yes',
                      autocommit=True)
    return  conct 

#---------------------------------------------------------------------------
def fn_DirectoryCheckout(Folder , Path ,SVNpath):
    
    global vErrFound

    if os.path.exists(Path+'\\'+Folder) and len(os.listdir(Path+'\\'+Folder))< 3:
        shutil.rmtree(Path+'\\'+Folder)
        LOGGER.info('\nEmpty Dir removed >> '+Path+'\\'+Folder+'\n')

    if not os.path.exists(Path+'\\'+Folder):

        os.makedirs(Path+'\\'+Folder) # Creating Folder if not exists
        LOGGER.info('\n\r..New Direcory Created..')
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
            try:                     
                FEwrite.write('\n>>'+str(e))
            except Exception as e :
                LOGGER.info('Error writing exception file >>:'+str(e))
                pass

            shutil.rmtree(Path+'\\'+Folder)
            LOGGER.info('Dir removed>> '+Path+'\\'+Folder+'\n')
            vErrFound =1
            pass

    else:
        LOGGER.info('\n..Directory already Exists['+Folder+']..')
        try:
            LOGGER.info('..Cleanup started..')
            client.cleanup(Path+'\\'+Folder+'\\Core')
            client.cleanup(Path+'\\'+Folder+'\\Reporting')

        except Exception as e:
            LOGGER.info('Cleanup RT_ERROR >>> '+str(e)+'\n')
            
            try:                     
                FEwrite.write('\n>>'+str(e))
            except Exception as e :
                LOGGER.info('Error writing exception file >>:'+str(e))
                pass
            vErrFound =1
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
            try:                     
                FEwrite.write('\n>>'+str(e))
            except Exception as e :
                LOGGER.info('Error writing exception file >>:'+str(e))
                pass
            vErrFound =1
            pass

# ------------------------------------------------------------------------------
def fn_Alertmailgenerator(HostName,LogFileName,Status):
        
        SERVER="corecard-com.mail.protection.outlook.com"

        # me = 'ankit.kumar@corecard.com'
        # address_book = ['ankit.kumar@corecard.com'] #controlteam@corecard.com 'rbhargava@corecard.com','rahul.kumar@corecard.com'

        if Status == 0:
            header='<h4 style="color:green;">[SVN_AUTOMATED_CHECKOUT]_[SUCCESS]</h4>'
        else:
            header='<h4 style="color:red;">[SVN_AUTOMATED_CHECKOUT]_[FAILURE]</h4>'
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg['Subject'] = "[SVN_AutoCheckout_RunningALERT]"
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
LOGGER = setup_logger('first_logger', vs_Log_File_Name)

LOGGER.info("==================================================================================================================")
LOGGER.info("AUTHOR : Ankit K")
LOGGER.info("DESCRIPTION : Automated SVN Checkout")
LOGGER.info("==================================================================================================================")

# ======================================================================
FEwrite = open(vr_CurrentDir+'\\OutFiles\\ExceptionOUT.xml','w+')
# ======================================================================   
vr_conn=py_Connect_MSSQL()
vr_crsr=vr_conn.cursor()

vobj = SvnSetup()
BranchPath = vobj.BranchDir

me = vobj.SenderMailAddress
address_book= vobj.receiverMailAddress

vrBranchdir = {}


try:
    vr_crsr.execute ("""SELECT Name ,SVN_Location FROM SVN_BranchOrPackages WITH(NOLOCK) WHERE isactive =1""")
    Fetchdata = vr_crsr.fetchall()

    for data in Fetchdata:
        if '/Branch' in data[1]:
            vrBranchdir[data[0]]=data[1]
        

    if vrBranchdir is not None:
        print(vrBranchdir)
        print('\n')
        for key,val in vrBranchdir.items():
            LOGGER.info('------ Branch Checkout Started >> '+key)
            
            fn_DirectoryCheckout(key , BranchPath ,val)


except Exception as e :
    LOGGER.info('\nRT_ERROR >>> '+str(e))
    try:                     
        FEwrite.write('\n>>'+str(e))
    except Exception as e :
        LOGGER.info('Error writing exception file >>:'+str(e))
        pass
    vErrFound =1

FEwrite.close()

# ***************************************************
fn_Alertmailgenerator(vrHostName,VSLogileName,vErrFound)

# ***************************************************