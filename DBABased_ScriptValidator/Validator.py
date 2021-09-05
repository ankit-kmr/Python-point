import glob
import re
import os, fnmatch
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import datetime ,time 
import pyodbc
import logging
import socket
from collections import Counter

import ValidatorAlertMail
#from SVN_Autocheckout import AutoCheckout    # will auto start calling Checkout class

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
                      Server='Xserver',
                      Database='Ankit_validatorDB',
                      Trusted_Connection='yes',
                      autocommit=True)
    return  conct 

#---------------------------------------------------------------------------
def fn_WriteIntoOut(Authorname ,ScripTname ,ErrorMsg ,FileSvnLoc):
    global varIsmailsent

    F2.write('</br><span class="BlackText">Author Name :</span><span class="BlueText">'+' '+Authorname+'</span>')
    F2.write('</br><span class="BlackText">Script Name :</span><span class="BlueText">'+' '+ScripTname+'</span>')
    F2.write('</br><span class="BlackText">Error Message :</span><span class="RedText">'+' '+ErrorMsg+'</span>')
    F2.write('</br><span class="BlackText">Svn Location :</span><span class="BlueText">'+' '+FileSvnLoc+'</span>')

    F2.write('</br>------------------------------------------------------------------')

    varIsmailsent =1 
#---------------------------------------------------------------------------
def fn_ExecSpCall(PckgID , ExecDate , processName , Status ,mailsent):
    LOGGER.info('function fn_ExecSpCall is called >>> '+str(Status))

    sql = """\
    SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorExecutionLog @arg_PackageID=?, @arg_ExecDate=?, @arg_proceeName=?, @arg_Status=? ,@arg_Ismailsent=?;
    """
    values = (PckgID , ExecDate ,processName ,Status,mailsent )
    vr_crsr.execute(sql, values)
#---------------------------------------------------------------------------
def fn_GetError (ErrCode):
    LOGGER.info('function fn_GetError is called [ErrCode] =='+ ErrCode)
    ErrCode = "".join(ErrCode.split())
    
    vr_crsr.execute('Select LTRIM(ErrorDescription) From [DBO].[ValidatorErrorLookup] with(nolock) Where Eid =?',(ErrCode))
    try :
        ErrReason = vr_crsr.fetchone()[0]
    except :
        ErrReason = ''
    return ErrReason
#---------------------------------------------------------------------------
def fn_OrphanCheck (PackageID ,Foldername , DirectoryLoc ,ErrCode) :
    Usp_scripts = []

    scr1=os.listdir(DirectoryLoc)
    ptrn = "*.SQL"
    for sc1 in scr1: 
        if fnmatch.fnmatch(sc1.upper(), ptrn):
            Usp_scripts.append(sc1)
    
    fi_open=open(DirectoryLoc+'\\'+Foldername[2:(len(Foldername))]+'.txt')
    fi=fi_open.read().split('\n')
    fi=[element.upper() for element in fi] ; fi
    
    fi = [x.strip(' ') for x in fi]
    
    for t in Usp_scripts:
        y=t
        t=t.upper()
        
        if(t not in fi):
            LOGGER.info('function fn_OrphanCheck is called ....')
            Error =  fn_GetError(ErrCode)
            
            sql = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
            """
            values = (PackageID , DirectoryLoc+'\\'+y ,ErrCode ,Error )
            vr_crsr.execute(sql, values)
            V_data = list(vr_crsr.fetchone())
            
            #-----------------------------------------------------------------------
            sqlNew = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
            """
            values = (PackageID , DirectoryLoc+'\\'+y )
            vr_crsr.execute(sqlNew, values)

            V_AuthorDATA = list(vr_crsr.fetchone())
            
            if V_AuthorDATA[0] != 0:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                return V_AuthorDATA[1]

#---------------------------------------------------------------------------
def fn_DuplicateEntryCheck (PackageID ,Foldername , DirectoryLoc ,ErrCode) :
    fi_open=open(DirectoryLoc+'\\'+Foldername[2:(len(Foldername))]+'.txt')
    fi=fi_open.read().split('\n')  
    fi = [x.strip(' ') for x in fi]
    
    scripts = [k for k,v in Counter(fi).items() if v >1]

    for y in scripts:
       
        LOGGER.info('function fn_DuplicateEntryCheck is called ....')
        Error =  fn_GetError(ErrCode)
        
        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (PackageID , DirectoryLoc+'\\'+y ,ErrCode ,Error )
        vr_crsr.execute(sql, values)
        V_data = list(vr_crsr.fetchone())
        
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (PackageID , DirectoryLoc+'\\'+y )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())
        
        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            return V_AuthorDATA[1]

#-----------------------------------------------------------------------------------------------------
def fn_FileNotFound (PackageID ,Foldername , DirectoryLoc ,ErrCode) :
    i_scripts = []
    f_scripts = []

    scr1=os.listdir(DirectoryLoc)
    ptrn = "*.SQL"
    for sc1 in scr1: 
        if fnmatch.fnmatch(sc1.upper(), ptrn):
            i_scripts.append(sc1.upper())
    
    fi_open=open(DirectoryLoc+'\\'+Foldername[2:(len(Foldername))]+'.txt')
    fi=fi_open.read().split('\n') 
    fi = [x.strip(' ') for x in fi]
    
    for s in fi: 
        if fnmatch.fnmatch(s.upper(), ptrn):
            f_scripts.append(s)

    for t in f_scripts:
        y = t
        t = t.upper()
        
        if(t not in i_scripts):
            LOGGER.info('function fn_FileNotFound called ....')
            Error =  fn_GetError(ErrCode)
            
            sql = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
            """
            values = (PackageID , DirectoryLoc+'\\'+y ,ErrCode ,Error )
            vr_crsr.execute(sql, values)
            V_data = list(vr_crsr.fetchone())
            
            #-----------------------------------------------------------------------
            sqlNew = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
            """
            values = (PackageID , DirectoryLoc+'\\'+y )
            vr_crsr.execute(sqlNew, values)

            V_AuthorDATA = list(vr_crsr.fetchone())
            
            if V_AuthorDATA[0] != 0:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                return V_AuthorDATA[1]

#---------------------------------------------------------------------------
def fn_SynFound (packageID ,Scriptloc ,ErrCode):
    LOGGER.info('\nCaliing function fn_SynFound ....')
    Error = fn_GetError(ErrCode)

    sql = """\
    SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
    """
    values = (packageID , Scriptloc ,ErrCode ,Error )
    vr_crsr.execute(sql, values)
    V_data = list(vr_crsr.fetchone())
    
    #-----------------------------------------------------------------------
    sqlNew = """\
    SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
    """
    values = (packageID , Scriptloc )
    vr_crsr.execute(sqlNew, values)

    V_AuthorDATA = list(vr_crsr.fetchone())

    if V_AuthorDATA[0] != 0:
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
        return V_AuthorDATA[1]
#-----------------------------------------------------------------------------------------------------
def fn_checkQUOTED_IDENTIFIER (packageID ,Scriptloc ,ErrCode ,files) :
    
    exp_checkidentifier=re.findall(r'\sSET\s*QUOTED_IDENTIFIER\s*OFF',files)

    if(exp_checkidentifier):
        LOGGER.info('exp_checkidentifier expression passed ....')
        Error = fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,ErrCode ,Error )
        vr_crsr.execute(sql, values)
        V_data = list(vr_crsr.fetchone())
        
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]
#-----------------------------------------------------------------------------------------------------
def fn_AlterColumnCheck (packageID ,Scriptloc ,ErrCode ,files) :

    exp12=re.findall(r'\sALTER\s*TABLE\s.*\s*ALTER\s*COLUMN\s*[a-zA-Z0-9_]+',files)

    if(exp12):
        LOGGER.info('fn_AlterColumnCheck expression passed ....')
        Error = fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            
            return V_AuthorDATA[1]
#-----------------------------------------------------------------------------------------------------
def fn_DropColumnCheck (packageID ,Scriptloc ,ErrCode ,files) :

    exp13=re.findall(r'\sALTER\s*TABLE\s.*\s*DROP\s*COLUMN\s*[a-zA-Z0-9_]+',files)

    if(exp13):
        LOGGER.info('fn_DropColumnCheck expression passed ....')
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            
            return V_AuthorDATA[1]
#-----------------------------------------------------------------------------------------------------
def fn_CheckNocountON (packageID ,Scriptloc ,ErrCode ,files ) :
    
    exp_NocountCheck=re.findall(r'\s*NOCOUNT\s*ON',files)

    if not(exp_NocountCheck):
        LOGGER.info('fn_CheckNocountON expression passed ....')
        Error=fn_GetError(ErrCode)
        
        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]
#-----------------------------------------------------------------------------------------------------

def fn_CheckTabelAlter (packageID ,Scriptloc ,ErrCode ,files ) :
    exp1_A=re.findall(r'\sCREATE\s*TABLE\s.*',files)
    exp1_B=re.findall(r'\sALTER\s*TABLE\s.*',files)
    exp2=re.findall(r'\sTABLE\s*\[DBO\]',files)
    exp3=re.findall(r'\sTABLE\s*DBO.',files)

    if(exp1_A or exp1_B) and not ((exp2) or (exp3)):
        LOGGER.info('fn_CheckTabelAlter expression passed ....')
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~                   
            return V_AuthorDATA[1]

def fn_checkTrigger (packageID ,Scriptloc ,ErrCode ,files ) :
    exp4=re.findall(r'\sTRIGGER\s.*',files)
    exp5=re.findall(r'\sTRIGGER\s*\[DBO\]',files)
    exp6=re.findall(r'\sTRIGGER\s*DBO.',files)    

    if(exp4) and not ((exp5) or (exp6)):    
        LOGGER.info('fn_checkTrigger expression passed ....')
        Error=fn_GetError(ErrCode)      

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]

def fn_checkViewPresent (packageID ,Scriptloc ,ErrCode ,files ) :  
    exp7=re.findall(r'\sCREATE\s*VIEW\s*',files)
    exp8=re.findall(r'\sALTER\s*VIEW\s*',files)  

    if(exp7) and (exp8):
        LOGGER.info('fn_checkViewPresent expression passed ....')
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
            return V_AuthorDATA[1]                   
    
def fn_checkIndex (packageID ,Scriptloc ,ErrCode ,files ) :     

    exp11=re.findall(r'\sCREATE\s*[a-zA-Z0-9_]+\s*INDEX',files)
    exp12=re.findall(r'\sCREATE\s*INDEX',files)

    if(exp11 or exp12):  
        LOGGER.info('fn_checkIndex expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]

def fn_UIDCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    exp9=re.findall(r'\sUID\s*=\s*USER_ID()',files)

    if(exp9):  
        LOGGER.info('fn_UIDCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
            return V_AuthorDATA[1]

def fn_AsteriskCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    exp3=re.findall(r'\sSELECT\s*\*\s*FROM\s*[a-zA-Z0-9_]+',files)

    if(exp3):  
        LOGGER.info('fn_AsteriskCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
            return V_AuthorDATA[1]

def fn_ProcDBOCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    exp1=re.findall(r'\sPROCEDURE\s*.\[DBO\]',files)
    exp2=re.findall(r'\sPROCEDURE\s*\sDBO',files)

    if(exp1) or (exp2):  
        LOGGER.info('fn_ProcDBOCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
            return V_AuthorDATA[1]

def fn_CheckDropProc (packageID ,Scriptloc ,ErrCode ,files ) :                             
    exp8=re.findall(r'\sDROP\s*PROCEDURE\s*IF\s*EXISTS\s*',files)
    exp9=re.findall(r'\sCREATE\s*OR\s*ALTER\s*PROCEDURE\s',files)

    if(exp8) and (exp9):  
        LOGGER.info('fn_CheckDropProc expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]

def fn_DBBIndexCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    
    exp11=re.findall(r'\sCREATE\s*INDEX',files)

    if(exp11):  
        LOGGER.info('fn_DBBIndexCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
            return V_AuthorDATA[1]
            

def fn_SynonymsDBOCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    
    inpString = files.splitlines()
    for i in inpString:
        exp1=re.findall(r'CREATE\s*SYNONYM\s.*',i)
        exp2=re.findall(r'CREATE\s*SYNONYM\s*\[DBO\]',i)
        exp3=re.findall(r'CREATE\s*SYNONYM\s*DBO.',i)

        if(exp1) and not(exp2 or exp3):  
            LOGGER.info('fn_SynonymsDBOCheck expression passed ....')    
            Error=fn_GetError(ErrCode)

            sql = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
            """
            values = (packageID , Scriptloc ,str(ErrCode) ,Error )
            vr_crsr.execute(sql, values)

            V_data = list(vr_crsr.fetchone())
            #-----------------------------------------------------------------------
            sqlNew = """\
            SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
            """
            values = (packageID , Scriptloc )
            vr_crsr.execute(sqlNew, values)

            V_AuthorDATA = list(vr_crsr.fetchone())

            if V_AuthorDATA[0] != 0:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
                return V_AuthorDATA[1]


def fn_IndexMaxDOPCheck (packageID ,Scriptloc ,ErrCode ,files ) : 
    exp_core1=re.findall(r'\sCREATE\s*[a-zA-Z0-9_]+\s*INDEX',files)
    exp_core2=re.findall(r'\sCREATE\s*INDEX',files)

    exp_idx1A = re.findall(r'MAXDOP=2',files)
    exp_idx1B = re.findall(r'MAXDOP\s*=\s*2',files)
    exp_idx1C = re.findall(r'\sMAXDOP\s*=\s*2',files)

    if (exp_core1 or exp_core2 ) and not (exp_idx1A or exp_idx1B or exp_idx1C ):
        LOGGER.info('fn_IndexMaxDOPCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]

def fn_IndexONLINECheck (packageID ,Scriptloc ,ErrCode ,files ) : 
    exp_core1=re.findall(r'\sCREATE\s*[a-zA-Z0-9_]+\s*INDEX',files)
    exp_core2=re.findall(r'\sCREATE\s*INDEX',files)

    exp_idx2A = re.findall(r'ONLINE=ON',files)
    exp_idx2B = re.findall(r'\sONLINE\s*=\s*ON',files)
    exp_idx2C = re.findall(r'ONLINE\s*=\s*ON',files)

    if (exp_core1 or exp_core2 ) and not (exp_idx2A or exp_idx2B or exp_idx2C):
        LOGGER.info('fn_IndexONLINECheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
            return V_AuthorDATA[1]

def fn_ReportingIndexCheck (packageID ,Scriptloc ,ErrCode ,files ) :                             
    
    exp_core2=re.findall(r'\sCREATE\s*[a-zA-Z0-9_]+\s*INDEX',files)
    exp_not1=re.findall(r'\sPROCEDURE\s*',files)

    if(exp_core2) and not (exp_not1):
        LOGGER.info('fn_ReportingIndexCheck expression passed ....')    
        Error=fn_GetError(ErrCode)

        sql = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorErrorDetails  @arg_PackgeID=?, @arg_FileLoc=?, @arg_ErrorCode=?, @arg_ErrorMsg=?;
        """
        values = (packageID , Scriptloc ,str(ErrCode) ,Error )
        vr_crsr.execute(sql, values)

        V_data = list(vr_crsr.fetchone())
        #-----------------------------------------------------------------------
        sqlNew = """\
        SET NOCOUNT ON ;EXEC USP_PDF_GetValidatorAuthorDetails  @arg_PackgeID=?, @arg_FileLoc=?;
        """
        values = (packageID , Scriptloc )
        vr_crsr.execute(sqlNew, values)

        V_AuthorDATA = list(vr_crsr.fetchone())

        if V_AuthorDATA[0] != 0:
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            fn_WriteIntoOut(V_AuthorDATA[0] ,V_data[2] ,Error ,V_data[1])
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
            return V_AuthorDATA[1]

# ------------------------------------------------------------------------------------------------------------
def fn_Mailsend (mailsubj , SendTO , CC , MailData,client) :

    SERVER = "outlook.com"
    
    if client =='Cr':
        FROM = 'controlteamCr@mai.cm'
    elif client =='P':
        FROM = "controlteam@mai.cm"

    # For local Testing ===============
    FROM = "ankit.kumar@mai.cm"
    SendTO =["ankit.kumar@mai.cm"]
    CC =["ankit.kumar@mai.cm"]
    # For local Testing ===============
    
    MailData = MailData.replace(u'\u2013', u' ') #-- fixes for ASCII Code error
        
    print(MailData)

    msg = MIMEMultipart(
    "alternative", None, [MIMEText(MailData,'html')])
    msg['Subject'] = mailsubj
    msg['From'] = FROM
    msg['To'] = ','.join(SendTO)
    msg['Cc'] = ','.join(CC)


    try:
        server = smtplib.SMTP(SERVER)
        server.sendmail(FROM, SendTO, msg.as_string())
        server.quit()    
        LOGGER.info('\n......Mail Sent successfully['+client+']........\n')
        
                            
    except Exception as e:
        LOGGER.info('FATAL[Mail sending] :'+str(e))
        pass 


# ========================================================================================================================================
AlrtObj = ValidatorAlertMail.ValidatorAlertSetup()
# ===================================================
vrHostName =socket.gethostname()
v_CurrentDir = str(os.getcwd())
Status ='SUCCESS'
EFwrite = open(v_CurrentDir+'\\OutFiles\\ValidatorExceptions.xml','w+')

# -----------------------------------------------------

v_PackageDict = {}

v_CrDirectory = []
v_PDirectory = []

v_CrAuthor = []
v_PAuthor = []

Label_Log_folder='Log\\'
logfilename = "LogFile_"+time.strftime("%Y%m%d%H%M%S")+ "." + "log"

vs_Log_File_Name	= 	os.path.join(Label_Log_folder+logfilename)
LOGGER = setup_logger('second_logger', vs_Log_File_Name)

LOGGER.info("==================================================================================================================")
LOGGER.info("AUTHOR : Ankit k")
LOGGER.info("DESCRIPTION : This Utility validates checkins for the standard checkin criteria of NoDownTime Upgrade")
LOGGER.info("==================================================================================================================")

LOGGER.info('\ncurrentDir >>'+v_CurrentDir+'\n')

vr_conn=py_Connect_MSSQL()
vr_crsr=vr_conn.cursor()
#---------------------------------------------------------------------------------
vr_crsr.execute ("""UPDATE ValidationErrorFilesSummary SET MarkDeleted =1""")
#---------------------------------------------------------------------------------

vr_crsr.execute ("""SET NOCOUNT ON; EXEC USP_PDF_GetAllActiveSVNLocForValidations""")
Fetchdata = vr_crsr.fetchall()

for data in Fetchdata :
    v_PackageDict[str(data[0])]=data[5]

print(v_PackageDict)
print('\n')
# ========================================================================================================================================
for path,client in v_PackageDict.items() :
    if client=='P' :
        v_PDirectory.append(path)
    
    elif client=='Cr' :
        v_CrDirectory.append(path)

print('\n')
htmlBodyHead = """\
            <html>
            <head>
            <style>
            </style>
            </head>
            <body>

            <style>
            .PurpleText
            {
                color:#363CEF;
                font-family:courier;font-weight: bold;font-size: 85%;
            }
            .BlackText
            {
                color:#000000;
                font-family:Arial;font-weight: bold;font-size: 111%;
            }
            .BlueText
            {
                color:#0040ff;
                font-family:monospace;font-weight: normal;font-size:111%;
            }
            .RedText
            {
                color:#FF2828;
                font-family:monospace;font-weight: normal;font-size:111%;
            }
            </style>

            <p class=PurpleText>Hi All ,</br>Please fix the below mentioned checkins issues ASAP. </br></br>

            """

htmlBodytailer ="""\
                </body>
                </html>
                """

# ######################################################################################################################################################### #
LOGGER.info ('**************************************** Checking For Cr Directory *****************************************')
F2= open(v_CurrentDir+'\\OutFiles\\Cr_OUT.html','w+')
F2.write(htmlBodyHead)

for vr_PackageID in v_CrDirectory :
    try:
        TablePath=[]
        UspPath=[]
        UpdatePath=[]
        IndexPATH=[]
        ReportingPrimary=[]
        v_ErrorListtocheck =[]

        ts = time.time()
        CURRENT_TIMESTAMP = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        vr_ExStatus =1
        varIsmailsent = 0
        #--------------------------------------------------------
        fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , 0 ,0)
        #--------------------------------------------------------

        pkgIDqry = """Select Shared_Path From [SVN_BranchOrPackages] with(nolock) Where Package_ID ="""+vr_PackageID+""
        LOGGER.info(pkgIDqry)
        vr_crsr.execute('Select Shared_Path From [SVN_BranchOrPackages] with(nolock) Where Package_ID =?',(vr_PackageID))
        Ppath = vr_crsr.fetchone()[0]
        
        vr_crsr.execute("""Select errorname From ValidatorErrorLookup where Cr =1""")
        Fetchdata=vr_crsr.fetchall()
        
        for row in Fetchdata :
            v_ErrorListtocheck.append(row[0])
        
        v_ErrorListtocheck = [x.strip(' ') for x in v_ErrorListtocheck]
        print(v_ErrorListtocheck)
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        TablePath.append(Ppath+'\\Core\\DataBaseServer\\1.Tables\\')
        UspPath.append(Ppath+'\\Core\\DataBaseServer\\2.USPs\\')
        UpdatePath.append(Ppath+'\\Core\\DataBaseServer\\3.Updates\\')
        IndexPATH.append(Ppath+'\\Core\\DataBaseServer\\4.Indexes\\')

        ReportingPrimary.append(Ppath+'\\Reporting\\DataBaseServer\\1.Primary\\')
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #------------------------------------------------------------------- TABLE INVALID CHECKINS ---------------------------------------------------------------------#
        LOGGER.info('\n --------------------------- Inside TABLE Folder ---------------------------')
        for Tp in TablePath:
            try:
                LOGGER.info('\nTable path :--'+Tp)
                
                listOfTableFolders=os.listdir(Tp)
                listofpaths1=[]
                for i in listOfTableFolders:
                    pathscript=Tp+i
                    listofpaths1.append(pathscript)
                    #------------------------------
                    if 'OrphanFileCheck' in v_ErrorListtocheck :
                        Alist=fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                        if Alist is not None :
                            v_CrAuthor.append(Alist)
                    #------------------------------
                    if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                        Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                        if Alist is not None :
                            v_CrAuthor.append(Alist)
                    #------------------------------
                    if 'FileNotFound' in v_ErrorListtocheck :
                        Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                        if Alist is not None :
                            v_CrAuthor.append(Alist)
                    #------------------------------
                for a in listofpaths1:
                    accessloc1=os.listdir(a)

                    for Tscripts in accessloc1:
                        UprTscripts=Tscripts.upper()

                        try:
                            if  UprTscripts.endswith('.SQL') and UprTscripts=='SYNONYMS_LOCALONLY.SQL':
                                if 'Package' in a:
                                    LOGGER.info('Synonyms_found')

                                    if 'SynonymLocalCheck' in v_ErrorListtocheck :
                                        Alist = fn_SynFound (vr_PackageID,a+'\\'+Tscripts,'Err07')
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)

                            if  UprTscripts.endswith('.SQL') and UprTscripts!='SYNONYMS_LOCALONLY.SQL' :
                                
                                try:
                                    FI = open(a+'\\'+Tscripts, 'r',encoding='utf-16')
                                    files=FI.read().upper()
                                    FI.close()
                                except:
                                    FI = open(a+'\\'+Tscripts, 'r')
                                    files=FI.read().upper()
                                    FI.close()
                                
                                exp10=re.findall(r'\sEXEC\s*SP_RENAME',files)
                                if(exp10):
                                    continue

                                if 'AlterColumnCheck' in v_ErrorListtocheck :
                                    Alist=fn_AlterColumnCheck (vr_PackageID,a+'\\'+Tscripts,'Err08',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'DropColumnCheck' in v_ErrorListtocheck :
                                    Alist=fn_DropColumnCheck (vr_PackageID,a+'\\'+Tscripts,'Err19',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'QuotedIdentifierCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkQUOTED_IDENTIFIER (vr_PackageID,a+'\\'+Tscripts,'Err06',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)  

                                if 'ALTERTableCheck' in v_ErrorListtocheck :
                                    Alist=fn_CheckTabelAlter (vr_PackageID,a+'\\'+Tscripts,'Err01',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'TriggerCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkTrigger (vr_PackageID,a+'\\'+Tscripts,'Err02',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'ViewCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkViewPresent (vr_PackageID,a+'\\'+Tscripts,'Err03',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'IndexCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkIndex (vr_PackageID,a+'\\'+Tscripts,'Err04',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'UID_check' in v_ErrorListtocheck :
                                    Alist=fn_UIDCheck (vr_PackageID,a+'\\'+Tscripts,'Err09',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)
                         
                        except Exception as e:
                            LOGGER.info('Fatal >> :'+ str(e))
                            pass      

            
            except Exception as e :
                LOGGER.info('Exception Occurs [Tables] : '+str(e))                            
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
        #------------------------------------------------------------------- USP INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside USPs Folder --------------------------')
        for Up in UspPath:
            try:
                LOGGER.info('\nUSPs path :--'+Up)
                
                listOfUSPsFolders=os.listdir(Up)
                
                listofpaths2=[]
                for i in listOfUSPsFolders:
                    pathscript=Up+i
                    listofpaths2.append(pathscript)
                    #------------------------------
                    if 'OrphanFileCheck' in v_ErrorListtocheck :
                        Alist=fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                        if Alist is not None :
                            v_CrAuthor .append(Alist)
                    #------------------------------
                    if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                        Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                        if Alist is not None :
                            v_CrAuthor.append(Alist)
                    #------------------------------
                    if 'FileNotFound' in v_ErrorListtocheck :
                        Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                        if Alist is not None :
                            v_CrAuthor.append(Alist)
                    #------------------------------

                for a in listofpaths2:
                    try:
                        accessloc2=os.listdir(a)
                    except:
                        pass

                    for Uscripts in accessloc2:
                        UprUscripts=Uscripts.upper()
                        if  UprUscripts.endswith('.SQL'):
                            
                            try:
                                FI = open(a+'\\'+Uscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+Uscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            
                            exp_ProcCheck=re.findall(r'\sPROCEDURE\s.*',files)
                            exp_PcheckDrp =re.findall(r'\sDROP\s*PROCEDURE\s.*',files)
                            exp_PcheckCrt =re.findall(r'\sCREATE\s*PROCEDURE\s.*',files)
                            
                            try:
                                #---------------------------
                                if 'NoCountCheck' in v_ErrorListtocheck :
                                    if (exp_ProcCheck):
                                        if (exp_PcheckDrp and not exp_PcheckCrt):
                                            Alist=None
                                        else:
                                            fn_CheckNocountON (vr_PackageID,a+'\\'+Uscripts,'Err05',files )
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)


                                if 'AsteriskCheck' in v_ErrorListtocheck :
                                    if not (UprUscripts.startswith('DBB') or UprUscripts =='PR_ACHUPDATEPIIDATA.SQL'):
                                        Alist=fn_AsteriskCheck (vr_PackageID,a+'\\'+Uscripts,'Err11',files )
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)


                                if 'ProcDBOCheck' in v_ErrorListtocheck :
                                    Alist=fn_ProcDBOCheck (vr_PackageID,a+'\\'+Uscripts,'Err12',files )
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'CheckDropProc' in v_ErrorListtocheck :
                                    Alist=fn_CheckDropProc (vr_PackageID,a+'\\'+Uscripts,'Err13',files )
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                if 'DBBIndexCheck' in v_ErrorListtocheck :
                                    if  (UprUscripts.startswith('DBB')):
                                        Alist=fn_DBBIndexCheck (vr_PackageID,a+'\\'+Uscripts,'Err14',files )
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)
                                
                                if 'UID_check' in v_ErrorListtocheck :
                                    Alist=fn_UIDCheck (vr_PackageID,a+'\\'+Uscripts,'Err09',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)

                                #--------------------------
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass

            except Exception as e :
                LOGGER.info('Exception Occurs [USP] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
        #------------------------------------------------------------------- UPDATE INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside UPDATE PRIMARY Folder --------------------------')
        for Upd in UpdatePath:   
            try:
                LOGGER.info('\nUpdate path :--'+Upd)     

                listOUPDFolders=os.listdir(Upd)
                
                listofpaths3=[]
                listOfUpdateFolders2 = []

                for i in listOUPDFolders:
                    if 'RunManually_' not in i:
                        pathscript=Upd+i
                        listofpaths3.append(pathscript)
                        #------------------------------
                        if 'OrphanFileCheck' in v_ErrorListtocheck :
                            Alist=fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                            if Alist is not None :
                                v_CrAuthor .append(Alist)
                        #------------------------------
                        if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                            Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                            if Alist is not None :
                                v_CrAuthor.append(Alist)
                        #------------------------------
                        if 'FileNotFound' in v_ErrorListtocheck :
                            Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                            if Alist is not None :
                                v_CrAuthor.append(Alist)
                    #------------------------------
                    else :
                        listOfUpdateFolders2.append(i)

                for a in listofpaths3:
                    a=a.replace("/","\\")
                    accessloc1=os.listdir(a)

                    for UpdScripts in accessloc1:
                        Up_UpdScripts=UpdScripts.upper()
                        if Up_UpdScripts.endswith('.SQL'):
                            try:
                                FI = open(a+'\\'+UpdScripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+UpdScripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            
                            try:
                                #------------------------------------------------------------------------------
                                if 'IndexCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkIndex (vr_PackageID,a+'\\'+UpdScripts,'Err04',files)
                                    if Alist is not None :
                                        v_CrAuthor .append(Alist)
                                #------------------------------------------------------------------------------
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass
                            
                LOGGER.info('\n-------------------------- Inside UPDATE Runmanually Folder --------------------------')
                listofpaths3=[]
                for i in listOfUpdateFolders2:
                    pathscript=Upd+i
                    listofpaths3.append(pathscript)
                

                for a1 in listofpaths3:
                    access=os.listdir(a1)
                    for a2 in access:
                        LOGGER.info('Ranmanually path : '+(a1+'\\'+a2))

                        accessloc3=os.listdir(a1+'\\'+a2)
                    
                        for UpdScripts in accessloc3:
                            UprUpdScripts=UpdScripts.upper()
                            
                            if UprUpdScripts.endswith('.SQL'):
                                
                                try:
                                    FI = open(a1+'\\'+a2+'\\'+UpdScripts, 'r',encoding='utf-16')
                                    files=FI.read().upper()
                                    FI.close()
                                except:
                                    FI = open(a1+'\\'+a2+'\\'+UpdScripts, 'r')
                                    files=FI.read().upper()
                                    FI.close()

                                try:
                                    if 'QuotedIdentifierCheck' in v_ErrorListtocheck :
                                        Alist=fn_checkQUOTED_IDENTIFIER (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err06',files)
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)
                                    
                                    if 'SynonymsDBOCheck' in v_ErrorListtocheck :
                                        Alist=fn_SynonymsDBOCheck (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err15',files)
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)
                                    
                                    if 'IndexCheck' in v_ErrorListtocheck :
                                        Alist=fn_checkIndex (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err04',files)
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)

                                except Exception as e:
                                    LOGGER.info('Fatal >> :'+str(e))
                                    pass

            except Exception as e :
                LOGGER.info('Exception Occurs [UPDATE] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass

        #------------------------------------------------------------------- INDEX INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n--------------------------  Inside INDEX Folder -------------------------- ')
        for Idx in IndexPATH:

            try :
                LOGGER.info('\Index path :--'+Idx)
        
                listOfINDEXFolders=os.listdir(Idx)
                listofpaths1=[]

                for i in listOfINDEXFolders:

                    pathscript=Idx+i
                    listofpaths1.append(pathscript)


                for a in listofpaths1:
                    accessloc1=os.listdir(a)
            
                    for Idxscripts in accessloc1:
                        UprIdxscripts=Idxscripts.upper()
                        if  UprIdxscripts.endswith('.SQL') :
                            try:
                                FI = open(a+'\\'+Idxscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+Idxscripts, 'r')
                                files=FI.read().upper()
                                FI.close()

                            try:
                                if 'IndexMaxDOPCheck' in v_ErrorListtocheck :
                                        Alist=fn_IndexMaxDOPCheck (vr_PackageID,a+'\\'+Idxscripts,'Err17',files)
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)
                                
                                if 'IndexONLINECheck' in v_ErrorListtocheck :
                                        Alist=fn_IndexONLINECheck (vr_PackageID,a+'\\'+Idxscripts,'Err18',files)
                                        if Alist is not None :
                                            v_CrAuthor .append(Alist)
                            
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass

            except Exception as e :
                LOGGER.info('Exception Occurs [INDEX] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
        #------------------------------------------------------------------- Reporting Main INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside Reporting PRIMARY Folder --------------------------')

        for Rp in ReportingPrimary:
            LOGGER.info('\Reporting path :--'+Rp)  

            listOfUpdateFolders1=os.listdir(Rp)
            listOfUpdateFolders2=[]

            for lf in listOfUpdateFolders1:
                if 'RunManually_' in lf:
                    listOfUpdateFolders2.append(lf)

            listofpaths3=[]
            for i in listOfUpdateFolders2:
                pathscript=Rp+i
                listofpaths3.append(pathscript)
            
        
            for a1 in listofpaths3:
                access=os.listdir(a1)
                for a2 in access:
                    accessloc3=os.listdir(a1+'\\'+a2)
                
                    for Rpscripts in accessloc3:
                        UprRpScrpt=Rpscripts.upper()
                        if  UprRpScrpt.endswith('.SQL'):
                            
                            try:
                                FI = open(a1+'\\'+a2+'\\'+Rpscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a1+'\\'+a2+'\\'+Rpscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                        
                        if 'ReportingIndexCheck' in v_ErrorListtocheck :
                            Alist=fn_ReportingIndexCheck (vr_PackageID,a1+'\\'+a2+'\\'+Rpscripts,'Err16',files)
                            if Alist is not None :
                                v_CrAuthor .append(Alist)
        
        #--------------------------------------------------------
        fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , vr_ExStatus , varIsmailsent)
        #--------------------------------------------------------
    except Exception as e :
        LOGGER.info('Exception Occurs : '+str(e))  
        try:
            Status ='FAILED'
            vr_ExStatus = 3
            EFwrite.write('>>>'+str(e)+'\n')
            #--------------------------------------------------------
            fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , vr_ExStatus ,3)
            #--------------------------------------------------------
        except Exception as e :
            LOGGER.info('Error writing into exceptionfile >>:'+str(e))
            pass

F2.write(htmlBodytailer)
F2.close()

# ######################################################################################################################################################### #

LOGGER.info ('\n\r**************************************** Checking For P Directory *****************************************')
F2= open(v_CurrentDir+'\\OutFiles\\P_OUT.html','w+')
F2.write(htmlBodyHead)

for vr_PackageID in v_PDirectory :
    try:
        TablePath=[]
        UspPath=[]
        UpdatePath=[]
        ReportingPrimary=[]
        IndexPATH =[]
        v_ErrorListtocheck =[]

        ts = time.time()
        CURRENT_TIMESTAMP = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        vr_ExStatus =1
        varIsmailsent = 0
        #--------------------------------------------------------
        fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , 0,0)
        #--------------------------------------------------------

        pkgIDqry = """Select Shared_Path From [SVN_BranchOrPackages] with(nolock) Where Package_ID ="""+vr_PackageID+""
        LOGGER.info(pkgIDqry)
        vr_crsr.execute('Select Shared_Path From [SVN_BranchOrPackages] with(nolock) Where Package_ID =?',(vr_PackageID))
        Ppath = vr_crsr.fetchone()[0]
        
        vr_crsr.execute("""Select errorname From ValidatorErrorLookup where P =1""")
        Fetchdata=vr_crsr.fetchall()
        
        for row in Fetchdata :
            v_ErrorListtocheck.append(row[0])
        
        v_ErrorListtocheck = [x.strip(' ') for x in v_ErrorListtocheck]
        print(v_ErrorListtocheck)

        TablePath.append(Ppath+'\\Core\\DataBaseServer\\1.Tables\\')
        UspPath.append(Ppath+'\\Core\\DataBaseServer\\2.USPs\\')
        UpdatePath.append(Ppath+'\\Core\\DataBaseServer\\3.Updates\\')
        IndexPATH.append(Ppath+'\\Core\\DataBaseServer\\4.Indexes\\')

        ReportingPrimary.append(Ppath+'\\Reporting\\DataBaseServer\\1.Primary\\')
        

        #------------------------------------------------------------------- TABLE INVALID CHECKINS ---------------------------------------------------------------------#
        LOGGER.info('\n --------------------------- Inside TABLE Folder ---------------------------')
        for Tp in TablePath:
            try:
                LOGGER.info('\nTable path :--'+Tp)
                
                listOfTableFolders=os.listdir(Tp)
                listofpaths1=[]
                for i in listOfTableFolders:
                    pathscript=Tp+i
                    listofpaths1.append(pathscript)
                        #------------------------------
                    if 'OrphanFileCheck' in v_ErrorListtocheck :
                        Alist = fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                        if Alist is not None :
                            v_PAuthor.append(Alist)
                        #------------------------------
                    if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                        Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                        if Alist is not None :
                            v_PAuthor.append(Alist)
                        #------------------------------
                    if 'FileNotFound' in v_ErrorListtocheck :
                        Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                        if Alist is not None :
                            v_PAuthor.append(Alist)
                        #------------------------------
                for a in listofpaths1:
                    accessloc1=os.listdir(a)

                    for Tscripts in accessloc1:
                        UprTscripts=Tscripts.upper()

                        if  UprTscripts.endswith('.SQL') and UprTscripts=='SYNONYMS_LOCALONLY.SQL':
                            if 'Package' in a:
                                LOGGER.info('Synonyms_found')

                                if 'SynonymLocalCheck' in v_ErrorListtocheck :
                                    Alist = fn_SynFound (vr_PackageID,a+'\\'+Tscripts,'Err07')
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                        if  UprTscripts.endswith('.SQL') and UprTscripts!='SYNONYMS_LOCALONLY.SQL' :
                            
                            try:
                                FI = open(a+'\\'+Tscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+Tscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            
                            exp10=re.findall(r'\sEXEC\s*SP_RENAME',files)
                            if(exp10):
                                continue
                            
                            try:
                                if 'AlterColumnCheck' in v_ErrorListtocheck :
                                    Alist=fn_AlterColumnCheck (vr_PackageID,a+'\\'+Tscripts,'Err08',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)


                                if 'DropColumnCheck' in v_ErrorListtocheck :
                                    Alist=fn_DropColumnCheck (vr_PackageID,a+'\\'+Tscripts,'Err19',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)


                                if 'QuotedIdentifierCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkQUOTED_IDENTIFIER (vr_PackageID,a+'\\'+Tscripts,'Err06',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                                
                                if 'ALTERTableCheck' in v_ErrorListtocheck :
                                    Alist=fn_CheckTabelAlter (vr_PackageID,a+'\\'+Tscripts,'Err01',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                                
                                if 'TriggerCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkTrigger (vr_PackageID,a+'\\'+Tscripts,'Err02',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)


                                if 'ViewCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkViewPresent (vr_PackageID,a+'\\'+Tscripts,'Err03',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                                
                                if 'IndexCheck' in v_ErrorListtocheck :
                                    Alist=fn_checkIndex (vr_PackageID,a+'\\'+Tscripts,'Err04',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                                
                                if 'UID_check' in v_ErrorListtocheck :
                                    Alist=fn_UIDCheck (vr_PackageID,a+'\\'+Tscripts,'Err09',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass
            
            except Exception as e :
                LOGGER.info('Exception Occurs [Tables] : '+str(e)) 
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
                pass                           

        #------------------------------------------------------------------- USP INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside USPs Folder --------------------------')
        for Up in UspPath:
            try:
                LOGGER.info('\nUSPs path :--'+Up)
                
                listOfUSPsFolders=os.listdir(Up)
                
                listofpaths2=[]
                for i in listOfUSPsFolders:
                    pathscript=Up+i
                    listofpaths2.append(pathscript)
                        #------------------------------
                    if 'OrphanFileCheck' in v_ErrorListtocheck :
                        Alist = fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                        if Alist is not None :
                            v_PAuthor.append(Alist)
                        #------------------------------
                    if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                        Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                        if Alist is not None :
                            v_PAuthor.append(Alist)
                        #------------------------------
                    if 'FileNotFound' in v_ErrorListtocheck :
                        Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                        if Alist is not None :
                            v_PAuthor.append(Alist)

                for a in listofpaths2:
                    try:
                        accessloc2=os.listdir(a)
                    except:
                        pass

                    for Uscripts in accessloc2:
                        UprUscripts=Uscripts.upper()
                        if  UprUscripts.endswith('.SQL'):
                            
                            try:
                                FI = open(a+'\\'+Uscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+Uscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            
                            exp_ProcCheck=re.findall(r'\sPROCEDURE\s.*',files)
                            exp_PcheckDrp =re.findall(r'\sDROP\s*PROCEDURE\s.*',files)
                            exp_PcheckCrt =re.findall(r'\sCREATE\s*PROCEDURE\s.*',files)

                            try:
                                #---------------------------
                                if 'NoCountCheck' in v_ErrorListtocheck :
                                    if (exp_ProcCheck):
                                        if (exp_PcheckDrp and not exp_PcheckCrt):
                                            Alist=None
                                        else:
                                            fn_CheckNocountON (vr_PackageID,a+'\\'+Uscripts,'Err05',files )
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)
                                
                                if 'AsteriskCheck' in v_ErrorListtocheck :
                                    if not (UprUscripts.startswith('DBB') or UprUscripts =='PR_ACHUPDATEPIIDATA.SQL'):
                                        Alist=fn_AsteriskCheck (vr_PackageID,a+'\\'+Uscripts,'Err11',files )
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)

                                if 'ProcDBOCheck' in v_ErrorListtocheck :
                                    Alist=fn_ProcDBOCheck (vr_PackageID,a+'\\'+Uscripts,'Err12',files )
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)
                                
                                if 'CheckDropProc' in v_ErrorListtocheck :
                                    Alist=fn_CheckDropProc (vr_PackageID,a+'\\'+Uscripts,'Err13',files )
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)

                                if 'DBBIndexCheck' in v_ErrorListtocheck :
                                    if  (UprUscripts.startswith('DBB')):
                                        Alist=fn_DBBIndexCheck (vr_PackageID,a+'\\'+Uscripts,'Err14',files )
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)
                                
                                if 'UID_check' in v_ErrorListtocheck :
                                    Alist=fn_UIDCheck (vr_PackageID,a+'\\'+Uscripts,'Err09',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)
                                #--------------------------
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass

            except Exception as e :
                LOGGER.info('Exception Occurs [USP] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
                pass                           

        #------------------------------------------------------------------- UPDATE INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside UPDATE PRIMARY Folder --------------------------')
        for Upd in UpdatePath:   
            try:
                LOGGER.info('\nUpdate path :--'+Upd)     

                listOUPDFolders=os.listdir(Upd)
                
                listofpaths3=[]
                listOfUpdateFolders2 = []

                for i in listOUPDFolders:
                    if 'RunManually_' not in i:
                        pathscript=Upd+i
                        listofpaths3.append(pathscript)
                        #------------------------------
                        if 'OrphanFileCheck' in v_ErrorListtocheck :
                            Alist=fn_OrphanCheck (vr_PackageID,i ,pathscript ,'Err10') # orphan File check
                            if Alist is not None :
                                v_PAuthor.append(Alist)
                        #------------------------------
                        if 'DuplicateEntryCheck' in v_ErrorListtocheck :
                            Alist=fn_DuplicateEntryCheck (vr_PackageID,i ,pathscript ,'Err21') # Duplicate File check
                            if Alist is not None :
                                v_PAuthor.append(Alist)
                        #------------------------------
                        if 'FileNotFound' in v_ErrorListtocheck :
                            Alist=fn_FileNotFound (vr_PackageID,i ,pathscript ,'Err22') # File Not Found check
                            if Alist is not None :
                                v_PAuthor.append(Alist)

                    else :
                        listOfUpdateFolders2.append(i)

                for a in listofpaths3:
                    a=a.replace("/","\\")
                    accessloc1=os.listdir(a)

                    for UpdScripts in accessloc1:
                        Up_UpdScripts=UpdScripts.upper()
                        if Up_UpdScripts.endswith('.SQL'):
                            try:
                                FI = open(a+'\\'+UpdScripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+UpdScripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            
                            try:
                                # ----------------------------------------------------------------------
                                if 'IndexCheck' in v_ErrorListtocheck :
                                    Alist = fn_checkIndex (vr_PackageID,a+'\\'+UpdScripts,'Err04',files)
                                    if Alist is not None :
                                        v_PAuthor.append(Alist)
                                # ----------------------------------------------------------------------
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass

            except Exception as e :
                LOGGER.info('Exception Occurs [UPDATE] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass

            try:        
                LOGGER.info('\n-------------------------- Inside UPDATE Runmanually Folder --------------------------')
                listofpaths3=[]

                for i in listOfUpdateFolders2:
                    pathscript=Upd+i
                    listofpaths3.append(pathscript)
                

                for a1 in listofpaths3:
                    access=os.listdir(a1)
                    for a2 in access:
                        LOGGER.info('Ranmanually path : '+(a1+'\\'+a2))

                        accessloc3=os.listdir(a1+'\\'+a2)
                    
                        for UpdScripts in accessloc3:
                            UprUpdScripts=UpdScripts.upper()
                            
                            if UprUpdScripts.endswith('.SQL'):
                                
                                try:
                                    FI = open(a1+'\\'+a2+'\\'+UpdScripts, 'r',encoding='utf-16')
                                    files=FI.read().upper()
                                    FI.close()
                                except:
                                    FI = open(a1+'\\'+a2+'\\'+UpdScripts, 'r')
                                    files=FI.read().upper()
                                    FI.close()

                                try:
                                    if 'QuotedIdentifierCheck' in v_ErrorListtocheck :
                                        Alist = fn_checkQUOTED_IDENTIFIER (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err06',files)
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)
                                    
                                    if 'SynonymsDBOCheck' in v_ErrorListtocheck :
                                        Alist = fn_SynonymsDBOCheck (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err15',files)
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)
                                    
                                    if 'IndexCheck' in v_ErrorListtocheck :
                                        Alist = fn_checkIndex (vr_PackageID,a1+'\\'+a2+'\\'+UpdScripts,'Err04',files)
                                        if Alist is not None :
                                            v_PAuthor.append(Alist)
                                
                                except Exception as e:
                                    LOGGER.info('Fatal >> :'+str(e))
                                    pass

            except Exception as e :
                LOGGER.info('Exception Occurs [Runmanually] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
                pass                           

        
        #------------------------------------------------------------------- INDEX INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n--------------------------  Inside INDEX Folder -------------------------- ')
        for Idx in IndexPATH:

            try :
                LOGGER.info('\Index path :--'+Idx)
        
                listOfINDEXFolders=os.listdir(Idx)
                listofpaths1=[]

                for i in listOfINDEXFolders:

                    pathscript=Idx+i
                    listofpaths1.append(pathscript)


                for a in listofpaths1:
                    accessloc1=os.listdir(a)
            
                    for Idxscripts in accessloc1:
                        UprIdxscripts=Idxscripts.upper()
                        if  UprIdxscripts.endswith('.SQL') :
                            try:
                                FI = open(a+'\\'+Idxscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a+'\\'+Idxscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                            try:
                                if 'IndexMaxDOPCheck' in v_ErrorListtocheck :
                                        Alist=fn_IndexMaxDOPCheck (vr_PackageID,a+'\\'+Idxscripts,'Err17',files)
                                        if Alist is not None :
                                            v_PAuthor .append(Alist)
                                
                                if 'IndexONLINECheck' in v_ErrorListtocheck :
                                        Alist=fn_IndexONLINECheck (vr_PackageID,a+'\\'+Idxscripts,'Err18',files)
                                        if Alist is not None :
                                            v_PAuthor .append(Alist)
                            
                            except Exception as e:
                                LOGGER.info('Fatal >> :'+str(e))
                                pass
                            
            except Exception as e :
                LOGGER.info('Exception Occurs [INDEX] : '+str(e))
                try:
                    Status ='FAILED'
                    vr_ExStatus =3
                    EFwrite.write('>>>'+str(e)+'\n')
                except Exception as e :
                    LOGGER.info('Error writing into exceptionfile >>:'+str(e))
                    pass
                pass                           

        #------------------------------------------------------------------- Reporting Main INVALID CHECKINS -------------------------------------------------------------------                     
        LOGGER.info('\n-------------------------- Inside Reporting PRIMARY Folder --------------------------')

        for Rp in ReportingPrimary:
            LOGGER.info('\Reporting path :--'+Rp) 

            listOfUpdateFolders1=os.listdir(Rp)
            listOfUpdateFolders2=[]

            for lf in listOfUpdateFolders1:
                if 'RunManually_' in lf:
                    listOfUpdateFolders2.append(lf)

            listofpaths3=[]
            for i in listOfUpdateFolders2:
                pathscript=Rp+i
                listofpaths3.append(pathscript)
            
        
            for a1 in listofpaths3:
                access=os.listdir(a1)
                for a2 in access:
                    accessloc3=os.listdir(a1+'\\'+a2)
                
                    for Rpscripts in accessloc3:
                        UprRpScrpt=Rpscripts.upper()
                        if  UprRpScrpt.endswith('.SQL'):
                            
                            try:
                                FI = open(a1+'\\'+a2+'\\'+Rpscripts, 'r',encoding='utf-16')
                                files=FI.read().upper()
                                FI.close()
                            except:
                                FI = open(a1+'\\'+a2+'\\'+Rpscripts, 'r')
                                files=FI.read().upper()
                                FI.close()
                        
                        if 'QuotedIdentifierCheck' in v_ErrorListtocheck :
                            Alist = fn_checkQUOTED_IDENTIFIER (vr_PackageID,a1+'\\'+a2+'\\'+Rpscripts,'Err06',files)
                            if Alist is not None :
                                v_PAuthor.append(Alist)

                        if 'ReportingIndexCheck' in v_ErrorListtocheck :
                            Alist = fn_ReportingIndexCheck (vr_PackageID,a1+'\\'+a2+'\\'+Rpscripts,'Err16',files)
                            if Alist is not None :
                                v_PAuthor.append(Alist)

        #--------------------------------------------------------
        fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , vr_ExStatus,varIsmailsent)
        #--------------------------------------------------------         
              
    except Exception as e :
        LOGGER.info('Exception Occurs : '+str(e))  
        try:
            Status ='FAILED'
            vr_ExStatus =3
            EFwrite.write('>>>'+str(e)+'\n')
            #--------------------------------------------------------
            fn_ExecSpCall(vr_PackageID , CURRENT_TIMESTAMP , 'Invalid Checkins' , vr_ExStatus,3)
            #-------------------------------------------------------- 
        except Exception as e :
            LOGGER.info('Error writing into exceptionfile >>:'+str(e))
            pass
        pass                           

F2.write(htmlBodytailer)
F2.close()
        

# ###################################################################################################################################### #
v_CrAuthorlist =[]
v_PAuthorList = []

for lemnt in v_CrAuthor:
    ilst = lemnt.split(',')

    print(ilst)

    for e in ilst :
        v_CrAuthorlist.append(e)


for lemnt in v_PAuthor:
    ilst = lemnt.split(',')

    print(ilst)

    for e in ilst :
        v_PAuthorList.append(e)

# ----------------------------------------------------------------
for outs in os.listdir(v_CurrentDir+'\\OutFiles'):

    try :
        if outs == 'Cr_OUT.html' :
            vr_SUBJECT='Cr - Invalid Checkins'
            
            vr_crsr.execute ("""Select Ltrim(Rtrim(Mail_copy_recipients)) FROM CPS_Emails WITH(NOLOCK) WHERE EnvironmentName='Cr' and ProcessName ='InvalidCheckin'""")
            Vr_cc = list(vr_crsr.fetchone())

            vr_crsr.execute ("""Select Ltrim(Rtrim(Mail_recipients)) FROM CPS_Emails WITH(NOLOCK) WHERE EnvironmentName='Cr' and ProcessName ='InvalidCheckin'""")
            Vr_To = list(vr_crsr.fetchone())[0].split(';')

            results = list(dict.fromkeys(v_CrAuthorlist))
            results.extend(Vr_To)  # --- Adding the default receipient addressese .
            print('\nCr Authors are :')
            print(results)

            results.append('ankit.kumar@mai.cm')

            ErrHtmlBody=open(v_CurrentDir+'\\OutFiles\\'+outs,'r').read()
            
            if len(ErrHtmlBody) > 0:
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                fn_Mailsend (vr_SUBJECT , results , Vr_cc , ErrHtmlBody,client ='Cr')
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            else:
                LOGGER.info('.... No Mail Sent ...')
                
        elif outs == 'P_OUT.html':
            vr_SUBJECT='P - Invalid Checkins'
            
            vr_crsr.execute ("""Select Ltrim(Rtrim(Mail_copy_recipients)) FROM CPS_Emails WITH(NOLOCK) WHERE EnvironmentName='P' and ProcessName ='InvalidCheckin'""")
            Vr_cc = list(vr_crsr.fetchone())
        
            results = list(dict.fromkeys(v_PAuthorList))
            results.extend(['rbhargava@mai.cm','satyam.agrawal@mai.cm'])

            print('P Authors are :')
            print(results)
            
            ErrHtmlBody=open(v_CurrentDir+'\\OutFiles\\'+outs,'r').read()

            if len(ErrHtmlBody) > 0:
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                fn_Mailsend (vr_SUBJECT , results , Vr_cc , ErrHtmlBody,client = 'P')
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            else:
                LOGGER.info('.... No Mail Sent ...')

    except Exception as e :
        LOGGER.info ('Exception Occured >>> '+str(e))
        pass

# ################################################### Alert Message Call ####################################################################### #

EFwrite.close()
# added explicit commit and connection close ..
vr_conn.commit()
vr_conn.close()
# # --------------------------------
AlrtObj.fn_Alertmailgenerator(logfilename ,vrHostName,Status)
# # --------------------------------
