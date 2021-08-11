import glob
import re
import os, fnmatch
import sys
import shutil
from os import path
import datetime ,time 
import pyodbc
import logging
import socket

import SetUp

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def fn_MoveFiles (SourceDir ,DestDir):
    try:
        LOGGER.info('Moving From '+SourceDir+' To '+DestDir)

        file_list = [f for f in os.listdir(SourceDir) if os.path.isfile(os.path.join(SourceDir, f)) and f.endswith('.txt')]
        print(file_list)
        for file in file_list:
            if(path.exists(DestDir+'\\'+file)):
                LOGGER.warning('>>> Removing alredy exists file in Archive folder from Destination Directory <<< ')
                os.remove(DestDir+'\\'+file)
                shutil.move(SourceDir+'\\'+file, DestDir) 
            else :
                shutil.move(SourceDir+"\\"+file, DestDir) 
                LOGGER.info('File Archived Successfully')

    except Exception as e :
        LOGGER.warning("Issue Archiving File :: "+str(e))

def fn_OutLogMsg(msg):
    #sTime = time.strftime("%Y/%m/%d %H:%M:%S")
    msg = msg+"\r"
    vobf_Log_File_Obj.write(msg)


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
def py_Connect_MSSQL(DataBaseName):
    conct = pyodbc.connect(Driver='{SQL Server Native Client 11.0}',
                      Server=ServeRName,
                      Database=DataBaseName,
                      Trusted_Connection='yes',
                      autocommit=True)
    return  conct

def fn_getProcedureBody(ObjID ,DBName):  
    vr_conn=py_Connect_MSSQL(DBName)
    vr_crsr=vr_conn.cursor() 
    QyrProc =  """SELECT Object_definition(Object_id(name)) FROM  sys.objects WHERE  object_id ="""+str(ObjID)+""
    if QuerryExec is True:
        LOGGER.info(QyrProc)
    vr_crsr.execute(QyrProc)
    return vr_crsr.fetchone()[0]

def fn_Importdata(DBName):
    vr_conn=py_Connect_MSSQL(DBName)
    vr_crsr=vr_conn.cursor()
    vr_crsr.execute("DROP TABLE IF EXISTS TempImportData")
    Psql = """\
    SET NOCOUNT ON; EXEC USP_PDF_GetProcToImport @ImprtDuration=?;
    """
    vr_crsr.execute(Psql, vrImpDate)
    

def fn_SelectData(DBName):   
    vr_conn=py_Connect_MSSQL(DBName)
    vr_crsr=vr_conn.cursor()
    QyrGet =  """SELECT TOP 20 RowID ,ObjectID ,ObjectName,Type FROM TempImportData With(NOLOCK) WHERE Processed = 0 ORDER BY TYPE"""
    vr_crsr.execute(QyrGet)
    if QuerryExec is True:
        LOGGER.info(QyrGet)
    return vr_crsr.fetchall()

def fn_TotalCount(DBName):
    vr_conn=py_Connect_MSSQL(DBName)
    vr_crsr=vr_conn.cursor()
    Qyrcount =  """SELECT Count(1) FROM TempImportData With(NOLOCK) WHERE Processed = 0 """
    if QuerryExec is True:
        LOGGER.info(Qyrcount)
    vr_crsr.execute(Qyrcount)
    return vr_crsr.fetchone()[0]

def fn_ExceptionList(DBName):
    vr_conn=py_Connect_MSSQL(DBName)
    vr_crsr=vr_conn.cursor()
    Qyrexpcount =  """SELECT ObjectName,SUBSTRING(ErrorMsg ,0,100) FROM TempImportData With(NOLOCK) WHERE Processed = 2 And Status ='Error'"""
    if QuerryExec is True:
        LOGGER.info(Qyrexpcount)
    vr_crsr.execute(Qyrexpcount)
    return vr_crsr.fetchall()

def fn_DropCreateObject(DataList ,DBName):

    for Fdata in DataList :
        vr_conn=py_Connect_MSSQL(DBName)
        vr_crsr=vr_conn.cursor()

        data =list(Fdata)
      
        try:
            result =''
            ErrMsg=''

            vrObjectID = str(data[1])
            vrObjectName = data[2].strip(' ')
            vrType =data[3].strip(' ')
            # -------------------------------------------------
            StrBody_DBO =fn_getProcedureBody(data[1] ,DBName)
            # -------------------------------------------------
            #print('\n\r'+StrBody_DBO)
            #UprStrBody_DBO = StrBody_DBO.upper()

            if vrType =='FN' or vrType =='IF' or vrType =='TF':
                LOGGER.info('ObjectID :'+vrObjectID+' >>> ObjectName :'+vrObjectName+' >>> ObjectType :'+vrType)
                exp1=re.findall(r'(?i)CREATE\s*FUNCTION\s*',StrBody_DBO)
                exp2=re.findall(r'(?i)CREATE\s*FUNCTION\s*DBO',StrBody_DBO)
                exp3=re.findall(r'(?i)CREATE\s*FUNCTION\s*.\[DBO\]',StrBody_DBO)

    
                if exp2:
                    print(exp2)
                    LOGGER.info('\n === exp 2 ===')
                    result = re.sub(r"CREATE\s*FUNCTION\s*DBO.", "CREATE FUNCTION Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                    
                
                elif exp3:
                    print(exp3)
                    LOGGER.info('\n === exp 3 ===')
                    result = re.sub(r"CREATE\s*FUNCTION\s*.\[DBO\].", "CREATE FUNCTION Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                    
                
                elif exp1:
                    LOGGER.info('\n === exp 1 ===')
                    result = re.sub(r"CREATE\s*FUNCTION\s*", "CREATE FUNCTION Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                
        
            if vrType =='P' :
                LOGGER.info('ObjectID :'+vrObjectID+' >>> ObjectName :'+vrObjectName+' >>> ObjectType :'+vrType)
                exp1=re.findall(r'(?i)CREATE\s*PROCEDURE\s*.',StrBody_DBO)
                exp2=re.findall(r'(?i)CREATE\s*PROCEDURE\s*DBO.',StrBody_DBO)
                exp3=re.findall(r'(?i)CREATE\s*PROCEDURE\s*.\[DBO\]',StrBody_DBO)
                
                                    
                if exp3:
                    print(exp3)
                    LOGGER.info('\n === exp 3 ===')
                    result = re.sub(r"CREATE\s*PROCEDURE\s*\[DBO\].", "CREATE PROCEDURE Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                    
                
                elif exp2:
                    print(exp2)
                    LOGGER.info('\n === exp 2 ===')
                    result = re.sub(r"CREATE\s*PROCEDURE\s*DBO.", "CREATE PROCEDURE Schema_1.", StrBody_DBO,flags=re.IGNORECASE)
                    
                
                elif exp1:
                    print(exp1)
                    LOGGER.info('\n === exp 1 ===')
                    result = re.sub(r"CREATE\s*PROCEDURE\s*", "CREATE PROCEDURE Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                    
                    
            
            if vrType =='V' :
                LOGGER.info('ObjectID :'+vrObjectID+' >>> ObjectName :'+vrObjectName+' >>> ObjectType :'+vrType)
                exp1=re.findall(r'(?i)CREATE\s*VIEW\s*',StrBody_DBO)
                exp2=re.findall(r'(?i)CREATE\s*VIEW\s*\sDBO.',StrBody_DBO)
                exp3=re.findall(r'(?i)CREATE\s*VIEW\s*.\[DBO\]',StrBody_DBO)
                
                
                if exp3:
                    result = re.sub(r"CREATE\s*VIEW\s*.\[DBO\].", "CREATE VIEW Schema_1.", StrBody_DBO, flags=re.IGNORECASE)


                elif exp2:
                    result = re.sub(r"CREATE\s*VIEW\s*\sDBO.", "CREATE VIEW Schema_1.", StrBody_DBO, flags=re.IGNORECASE)                    
                
                
                elif exp1:
                    result = re.sub(r"CREATE\s*VIEW\s*", "CREATE VIEW Schema_1.", StrBody_DBO, flags=re.IGNORECASE)
                    
            
            # ****************************************************
            sql = """\
            SET NOCOUNT ON ;EXEC USP_PDF_DBOToSchemaImport  @vPrint=?, @IsdropON=?, @VrObjectType=?, @VrObjectID=? ,@VrObjectName=? ,@VrCreateBody=?;
            """
            values = (0 , 1 ,vrType ,vrObjectID ,vrObjectName ,result )
            vr_crsr.execute(sql, values)

            V_data = list(vr_crsr.fetchone())
            ErrMsg =V_data[1]

            if V_data[0]== 3:
                LOGGER.info('\n'+vrObjectName+'::'+ErrMsg)
                

        except Exception as e :
            LOGGER.info(vrObjectName +':: FATAL >>>['+str(e)+']')
            pass


def Fn_executeData (DB_name ,Impdays ,rec):
    fn_OutLogMsg('\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    fn_OutLogMsg ('DB Name :: '+DB_name)
    fn_OutLogMsg ('Date of execution :: '+time.strftime("%Y-%m-%d %H:%M:%S"))
    fn_OutLogMsg ('Schema import started for number of days :: '+Impdays)
    # .........................................
    fn_Importdata(DB_name) #-- To get all import data
    # .........................................
    # .........................................
    vrTotalCount = fn_TotalCount(DB_name)
    fn_OutLogMsg ('Schema Import Started for number of object :: '+ str(vrTotalCount))
    # .........................................
    while rec == True :
        Rtrn =fn_SelectData(DB_name)
        rL = len(Rtrn)
        if rL > 0:
            #----------------------------------------
            fn_DropCreateObject(Rtrn ,DB_name)
            #----------------------------------------
        else:
            rec = False
    
    # .........................................
    vrexpList = fn_ExceptionList(DB_name)   #-- to fetch all the exception data
    
    fn_OutLogMsg ('Got exception while execution :: '+ str(len(vrexpList)))
    fn_OutLogMsg ('\nException object list :')
    for i in vrexpList :
        j =list(i)
        pattern = re.compile(r'\s+')
        errmsg = re.sub(pattern, ' ', j[1])
        #errmsg =errmsg.replace(" ", "") 
        fn_OutLogMsg ('>> '+j[0]+'   ==>[ '+errmsg+']')
    # .........................................

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #

#-- Making the refrence to the Setup class objects
vrobj = SetUp.SetUp()
ServeRName =vrobj.SERVERNAME
CI_DB = vrobj.CI_DB
CAuth_DB = vrobj.CAuth_DB
CL_DB = vrobj.CL_DB
Capp_DB = vrobj.Capp_DB
Corecredit_DB = vrobj.Corecredit_DB
CC_DB = vrobj.CoreCollect_DB

vrImpDate = str(vrobj.ImportDate)
QuerryExec = vrobj.QuerryExec

GetcwDir =os.getcwd()   #-- To get current working directory
List_AllDBs =[]
List_AllDBs.extend([CI_DB ,CAuth_DB ,CL_DB,Capp_DB,Corecredit_DB,CC_DB]) # can append any no of DBs passsed in setup

if QuerryExec:
    print('OK')
else:
    QuerryExec =False

Label_Log_folder=GetcwDir+'\\LOG\\'
if not os.path.exists(Label_Log_folder):
    print("Creating LOG Folder :: "+Label_Log_folder)
logfilename = "LogFile_"+time.strftime("%Y-%m-%d %H%M%S")+ "." + "log"
vs_Log_File_Name	= 	os.path.join(Label_Log_folder+logfilename)
LOGGER = setup_logger('first_logger', vs_Log_File_Name)

LOGGER.info("==================================================================================================================")
LOGGER.info("AUTHOR : Ankit k")
LOGGER.info("DESCRIPTION : Auto Import schema from DBO to SCHEMA_1")
LOGGER.info("==================================================================================================================")

LOGGER.info("\n\rCurrent Working Directory >>> "+GetcwDir)

LogFolder =GetcwDir+'\\RESULT_OUT\\'
Archived =LogFolder+'\\ARCHIVE\\'
if not os.path.exists(LogFolder):
    LOGGER.info("Creating OUT LOG Folder :: "+LogFolder)
    os.makedirs(LogFolder ,exist_ok= False)
    
if not os.path.exists(Archived):
    LOGGER.info("Creating Archive Folder :: "+Archived)
    os.makedirs(Archived ,exist_ok= False)

vs_Log_File_Name    = os.path.join(  LogFolder+"OutFile_"+time.strftime("%Y-%m-%d %H%M%S")+ "." + "txt")
vobf_Log_File_Obj   = open(vs_Log_File_Name,"w+")

# Moving existing Result files to Archive Folder ...........
fn_MoveFiles (LogFolder ,Archived)

try:
    # -----------------------------------------
    for DBName in List_AllDBs:

        if List_AllDBs[0]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreIssue DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================

            
        elif List_AllDBs[1]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreAuth DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================
        
        elif List_AllDBs[2]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreLibrary DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================
        
        elif List_AllDBs[3]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreApp DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================

        elif List_AllDBs[4]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreCredit DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================
            
        elif List_AllDBs[5]:
            if DBName is not None and DBName !='':
                LOGGER.info ('\n******************* CoreCollect DB ***************************')
                # ========================================
                Fn_executeData(DBName ,vrImpDate ,rec=True)
                # ========================================  
 
    # -----------------------------------------
   
except Exception as e:
    LOGGER.info(str(e))
    #exit()
