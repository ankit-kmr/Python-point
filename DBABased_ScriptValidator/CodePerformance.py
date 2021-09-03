import os ,sys,traceback
import datetime ,time 
import smtplib
from smtplib import *
import pyodbc
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
from email.mime.text import MIMEText
from pathlib import Path
import logging
formatter = logging.Formatter('%(asctime)s- %(levelname)s- %(message)s')
import csv

def py_Connect_MSSQL():
    conct = pyodbc.connect(Driver='{SQL Server}',
                    Server='hst',
                    Database='DBname',
                    Trusted_Connection='yes',
                    autocommit=True)
    return  conct 

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

def fn_WriteIntoOut(Authorname ,ScripTname ,ErrorMsg ,status ,priority):
    F2.write('\nAuthor   : '+Authorname)
    F2.write('\nFile     : '+ScripTname)
    F2.write('\nSuggestion : '+ErrorMsg)
    F2.write('\nStatus   : '+status)
    F2.write('\nPriority : '+priority)

    F2.write('\n-----------------------------------------------------------------------------------')

#---------------------------------------------------------------------------
def fn_ExecSpCall(PckgID , ExecDate , processName , Status ,mailsent):
    LOGGER.info('function fn_ExecSpCall is called >>> '+str(Status))

    sql = """\
    SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorExecutionLog @arg_PackageID=?, @arg_ExecDate=?, @arg_proceeName=?, @arg_Status=? ,@arg_Ismailsent=?;
    """
    values = (PckgID , ExecDate ,processName ,Status,mailsent )
    vr_crsr.execute(sql, values)

#---------------------------------------------------------------------------

def fn_PerformanceFileProcess(vr_PackageID, PerfPackagePath , PerfFileName):

    try:
        global vr_errStatus
        vrperffilePath = os.path.join (PerfPackagePath ,'Core\\DataBaseServer') # --> Performance file location

        csv.register_dialect('myDialect',
                        delimiter='|',
                        skipinitialspace=True,
                        quoting=csv.QUOTE_NONE)

        with open(vrperffilePath+'\\'+PerfFileName, 'r') as csvfile:
            reader = csv.reader(csvfile, dialect='myDialect')
            #reader = csv.reader(csvfile, delimiter='|', quotechar='"',doublequote=True)
            for row in reader:
                if len(row) ==0:
                    continue
                
                if row: 
                    try :
                        status = str(row[1].strip())
                        
                        Ustatus = status.upper()

                        if Ustatus == 'NEW':
                            filename = row[0]
                            filename = str(row[0].strip())

                            trm_filename = filename.replace(filename[0:int(filename.find('\\'))] , '')

                            LOGGER.info('\nFiles >>'+ trm_filename)

                            LOGGER.info('Files Location >>'+ PerfPackagePath+trm_filename)

                            if not os.path.exists(PerfPackagePath+trm_filename):
                                LOGGER.info('\n..This File Does not Exists..')
                                try:
                                    FEwrite.write(PerfPackagePath+trm_filename+'\n>>..This File Does not Exists..\n')
                                except Exception as e :
                                    LOGGER.info('Error writing exception file >>:'+str(e))
                                    pass

                            sql = """\
                            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
                            """

                            values = (vr_PackageID , PerfPackagePath+trm_filename ,'Err555' ,'PerformanceCheck Issue' )
                            vr_crsr.execute(sql, values)
                            V_data = list(vr_crsr.fetchone())
                            
                            if V_data[0] != 0:
                                #-----------------------------------------------------------------------
                                sqlNew = """\
                                SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
                                """

                                values = (vr_PackageID , PerfPackagePath+trm_filename)
                                vr_crsr.execute(sqlNew, values)

                                V_AuthorDATA = list(vr_crsr.fetchone()) 
                                                 
                                if V_AuthorDATA[0] !=0:
                                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,str(row[2]) ,status ,row[3] )
                                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                    authorList.append(V_AuthorDATA[1])

                        else:
                            if (len(row[0])<1 or len(row[1])<1 or len(row[2])<1 or len(row[3])<1):
                                LOGGER.info(' ..Exception in File [fields are invalid].. ')
                                try:
                                    vr_errStatus = 3
                                    FEwrite.write('\n..Exception in File[fields are invalid]..')
                                except Exception as e :
                                    LOGGER.info('Error writing exception file >>:'+str(e))
                                    pass
                                

                    except Exception as e:
                        try:
                            vr_errStatus = 3
                            FEwrite.write('\n>>'+str(e))
                        except Exception as e :
                            LOGGER.info('Error writing exception file >>:'+str(e))
                            pass
                
                else:
                    LOGGER.info(' ..Exception in File.. ')
                    break

    except Exception as e :
        vr_errStatus = 3
        LOGGER.info('FATAL >> '+ str(e))
        try:
            vr_errStatus = 3
            FEwrite.write('\nFATAL >>'+str(e))
        except Exception as e :
            LOGGER.info('Error writing exception file >>:'+str(e))
            pass
        pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def fn_SendPerformanceMail(SenderList , filePath ,PerfFileName ,ClientName):

    # ----------
    F2.close()
    # ----------
    global varIsmailsent 
    # -----------------------------------------------------------------------------------------------------------------------------------
    vr_crsr.execute('Select SVN_Location From [SVN_BranchOrPackages] with(nolock) Where Shared_Path =?',(filePath))
    vr_svnLoc = vr_crsr.fetchone()[0]

    if vr_svnLoc is None or vr_svnLoc =='':
        vr_svnLoc=str(filePath)
    # -----------------------------------------------------------------------------------------------------------------------------------

    html = """\
        <html>
        <head>
        <style>
        </style>
        </head>
        <body>

        <style>
        .GreyText
        {
            color:#800000;
            font-family:Arial;font-weight: bold;font-size: 88%;
        }
        .BlueText
        {
            color:#0040ff;
            font-family:Arial;font-weight: bold;font-size: 88%;
        }
        </style>

        <p style="color:crimson;font-family: courier;font-size: 100%;">Hi Team,</br></br>Please review all the recomendation made against your sql files by our DBA team.</br>
        It will be good if these recomendations followed and modified code checked in to the next upcoming branch or in the package itself if not deployed.</br></br>
        Once Done modification please change the status NEW to DONE ,Inside the File at their respective Package\\Branch.</p>

        <p style="color:#4F2A25;font-family: courier;font-size: 100%;">And Please Do not manipulate the file format .</p>
        
        <span class="GreyText">File Location: </span>&nbsp;<span class="BlueText">"""+str(vr_svnLoc)+"""</span>

        <p style="color:#808080;font-family:Arial;font-weight: bold;font-size: 97%;">Thanks</br>Control Team </p>

        </body>
        </html>
        """

    

    
    if ClientName == 'CREDIT':
        FROM = 'controlteamcredit@corecard.com'

    else :
        FROM = "controlteam@corecard.com"

    Qry = """Select Ltrim(Rtrim(Mail_recipients)) FROM CPS_Emails WITH(NOLOCK) WHERE EnvironmentName='<Client>' and ProcessName ='DBAPerformanceReview'"""
    Qry = Qry.replace('<Client>',ClientName)
    vr_crsr.execute (Qry)
    Vr_To = list(vr_crsr.fetchone())[0].split(';')

    SenderList = list(dict.fromkeys(SenderList))
    SenderList.extend(Vr_To)  # --- Adding the default receipient addressese .
    print('\n'+ClientName+' Authors are :')
    print(SenderList)
        
    
    SenderList.append('mai')


    sqlqry ="""Select Ltrim(Rtrim(Mail_copy_recipients)) FROM CPS_Emails WITH(NOLOCK) WHERE EnvironmentName='<Client>' and ProcessName ='DBAPerformanceReview'"""
    sqlqry = sqlqry.replace('<Client>',ClientName)
    vr_crsr.execute (sqlqry)
    Vr_cc = list(vr_crsr.fetchone())


    # # ---------------------- for local testing ------------------------- #
    # FROM = 'ID'
    # SenderList = ['ID']
    # Vr_cc = ['ID']
    # # ---------------------- for local testing ------------------------- #
    
    
    msg = MIMEMultipart()
    msg['Subject'] = '['+ClientName+"] DBA - Code Performance Review"
    msg['From'] = FROM
    msg['To'] = ','.join(SenderList)
    msg['Cc'] = ','.join(Vr_cc)
    
    f = open(v_CurrentDir+'\\OutFiles\\Performace_OUT.xml')

    PerfFileName = PerfFileName.replace('.csv','.txt')

    attachment = MIMEText(f.read())
    attachment.add_header('Content-Disposition', 'attachment', filename=PerfFileName)           
    msg.attach(attachment)

    part1 = MIMEText(html, 'html')

    msg.attach(part1)

    try:
        server = smtplib.SMTP(SERVER)
        server.sendmail(FROM, SenderList, msg.as_string())
        server.quit()    
        LOGGER.info('\n... Performance mail sent successfully ...\n\r')
        varIsmailsent =1
                            
    except Exception as e:
        vr_errStatus = 3
        LOGGER.info('FATAL_[mailing] :'+str(e))
        pass 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fn_SendexceptionMail (filePath ,PerfFileName ,ClientName):
    try:
        FEwrite.close()
        # -------------------------------
        global varIsmailsent

        with open(v_CurrentDir+'\\OutFiles\\ExceptionFile.xml','r') as infile:
            ExcpMsg =''
            for lines in infile:
                ExcpMsg = ExcpMsg +'<p style="color:#4777FA;font-family: courier;font-size: 100%;">'+lines+ '</br></br></p>'
                print ('ExcpMsg =='+ str(ExcpMsg))  
        

        if ( len(ExcpMsg) > 0) :

            # -----------------------------------------------------------------------------------------------------------------------------------
            vr_crsr.execute('Select SVN_Location From [SVN_Files] with(nolock) Where Shared_Path =?',(filePath+'\\'+PerfFileName))
            vr_svnLoc = vr_crsr.fetchone()[0]
            if vr_svnLoc is None :
                vr_svnLoc=str(filePath)
            # -----------------------------------------------------------------------------------------------------------------------------------
            
        
            Qry = """Select Ltrim(Rtrim(Mail_copy_recipients)) From CPS_Emails with(nolock) Where ProcessName = ? and EnvironmentName =? """
            Args = ('DBAExceptionMail',ClientName)
            vr_crsr.execute(Qry ,Args)
            Vr_cc = list(vr_crsr.fetchone())

            Qry = """Select Ltrim(Rtrim(Mail_recipients)) From CPS_Emails with(nolock) Where ProcessName = ? and EnvironmentName =? """
            Args = ('DBAExceptionMail',ClientName)
            vr_crsr.execute(Qry ,Args)
            Vr_To = list(vr_crsr.fetchone())[0].split(';')

            TO= Vr_To
            TO.append('ID')

            print ('+++++++++++++++++++ DBAExceptionMail +++++++++++++++++++++')
            print(TO)
            print(Vr_cc)
            print ('+++++++++++++++++++ DBAExceptionMail +++++++++++++++++++++')

            # ---------------------- for local testing ------------------------- #
            FROM = 'ID'
            TO = ['ID']
            Vr_cc = ['ID']
            # ---------------------- for local testing ------------------------- #

            htmlBody = """\
            <html>
            <head>
            <style>
            </style>
            </head>
            <body>

            <style>
            .GreyText
            {
                color:#800000;
                font-family:Arial;font-weight: bold;font-size: 88%;
            }
            .BlueText
            {
                color:#0040ff;
                font-family:Arial;font-weight: bold;font-size: 88%;
            }
            </style>

            <p style="color:crimson;font-family: courier;font-size: 100%;">Exceptions Occured In Below File </br></br></p>
        
            <span class="GreyText">File Location: </span>&nbsp;<span class="BlueText">"""+str(vr_svnLoc)+"""</span>

            <h4 style="color:red;">[Exception]</h4>"""+ExcpMsg+"""

            </body>
            </html>
            """
            #html=html.replace('{para}',ErrorFile)
        
            msg = MIMEMultipart(
            "alternative", None, [MIMEText(ExcpMsg),MIMEText(htmlBody,'html')])
            msg['Subject'] = '['+ClientName+"] DBA - Code Performance Review_[Exception]"
            msg['From'] = FROM
            msg['To'] = ','.join(TO)
            msg['Cc'] = ','.join(Vr_cc)


            try:
                server = smtplib.SMTP(SERVER)
                server.sendmail(FROM, TO, msg.as_string())
                server.quit()    
                LOGGER.info('......Performance Exception mail sent successfully........')
                varIsmailsent = 3
                                    
            except Exception as e:
                vr_errStatus = 3
                LOGGER.info('Mail Exception occurs :'+str(e))
                pass 

        
            
    except Exception as e:
        vr_errStatus = 3
        LOGGER.info('Exception occurs :'+str(e))
        pass        
# ================================================================================================================================
SERVER = "server"

v_CurrentDir = os.getcwd()
v_PackageDict = {}

LogFolder ='Log'
vs_Log_File_Name    = os.path.join(  LogFolder+"\CodePerformerLogFile_"+time.strftime("%Y%m%d_%H%M%S")+ "." + "txt")
LOGGER = setup_logger('first_logger', vs_Log_File_Name)

LOGGER.info("==================================================================================================================")
LOGGER.info("AUTHOR : Ankit k")
LOGGER.info("DESCRIPTION : This utility send mails regarding Code performance review")
LOGGER.info("==================================================================================================================")

vr_conn=py_Connect_MSSQL()
vr_crsr=vr_conn.cursor()

vr_crsr.execute ("""SET NOCOUNT ON; EXEC USP_PDF_GetAllActiveSVNLocForValidations""")
Fetchdata = vr_crsr.fetchall()

for data in Fetchdata :
    v_PackageDict[str(data[0])]=data[5]

print(v_PackageDict)
print('\n')

# ================================================================================================================================

for PerfpckgID,vrClient in v_PackageDict.items():

    try :

        ts = time.time()
        CURRENT_TIMESTAMP = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        

        vr_crsr.execute('Select Shared_Path From [SVN_BranchOrPackages] with(nolock) Where Package_ID =?',(PerfpckgID))
        PerfpckgPATH = vr_crsr.fetchone()[0]

        PerfPackagePath = os.path.join (PerfpckgPATH ,'Core\\DataBaseServer')
        
        if os.path.exists(PerfPackagePath):

            for fi in os.listdir(PerfPackagePath):
                uprfi = fi.upper()

                if '.CSV' in uprfi and 'PERFORMANCE_' in uprfi:
                    LOGGER.info('\n\rPerformace FileName['+PerfpckgID+']'+': '+fi)
                    
                    authorList = []
                    v_authorList = []
                    v_SendMail = 1

                    vr_errStatus = 1
                    varIsmailsent = 0

                    F2= open(v_CurrentDir+'\\OutFiles\\Performace_OUT.xml','w+')
                    FEwrite = open(v_CurrentDir+'\\OutFiles\\ExceptionFile.xml','w+')

                    #--------------------------------------------------------
                    fn_ExecSpCall(PerfpckgID , CURRENT_TIMESTAMP , 'Code Performance' , 0,0)
                    #--------------------------------------------------------
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    fn_PerformanceFileProcess(PerfpckgID,PerfpckgPATH , fi)
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    for lemnt in authorList:
                        ilst = lemnt.split(',')

                        for e in ilst :
                            v_authorList.append(e)

                    results = list(dict.fromkeys(v_authorList))  # mmoving redundent IDs 
                    print('\nAuthors are :')
                    print(results)
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    if results is not None and len(results)>0:
                        try:
                            # =========================================================
                            fn_SendPerformanceMail(results ,PerfpckgPATH,fi,vrClient)
                            # =========================================================
                        except SMTPResponseException as e:
                            print(e.smtp_code)
                            print(e.smtp_error)

                            try:
                                FEwrite.write('* '+str(e.smtp_error)+'\n')
                            except Exception as e :
                                LOGGER.info('Error Writing >>:'+str(e))
                                pass
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    fn_SendexceptionMail (PerfPackagePath ,fi ,vrClient)
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    #--------------------------------------------------------
                    fn_ExecSpCall(PerfpckgID , CURRENT_TIMESTAMP , 'Code Performance' , vr_errStatus ,varIsmailsent)
                    #--------------------------------------------------------

        else :
            LOGGER.info('NOT EXISTS >> '+ PerfPackagePath)

        
        
    except Exception as e :
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)[-1]
        LOGGER.info('FATAL >> '+ str(e))
        #--------------------------------------------------------
        fn_ExecSpCall(PerfpckgID , CURRENT_TIMESTAMP , 'Code Performance' , 3,0)
        #--------------------------------------------------------
        pass
        
vr_conn.commit()
vr_conn.close()

        
    