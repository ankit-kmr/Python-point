import os,sys
import pandas as pd
import sqlalchemy as sa
import pyodbc
import urllib

def fn_CsvFilemaking (filenam , Sheetname):
    ServerName ='Xeon'
    dbName ='Ankit_Temp'
    vr_csvR = pd.read_excel("C:\\Users\\ankit.kumar\\Desktop\\Python_Progrm\\Xlsx File Genearator\\Xls_To_Table\\Input\\"+filenam ,sheet_name = Sheetname)

    vr_csvR.columns =[column.replace(" ", "_") for column in vr_csvR.columns] 

    #print (vr_csvR)
    conn = urllib.parse.quote_plus('Driver={SQLServer};'
                'Server=' + ServerName + ';'
                'Database=' + dbName + ';'
                'Trusted_Connection=yes;')

    engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(conn),fast_executemany=True)
    #engine = engine.execution_options(autocommit=True)

    vr_csvR.to_sql('DeserveCC_Status' ,schema='dbo',con =engine)
    
    print(engine.execute("SELECT * FROM DeserveCC_Status").fetchall())
    
try :
    
    vr_Outfolder = "C:\\Users\\ankit.kumar\\Desktop\\Python_Progrm\\Xlsx File Genearator\\Xls_To_Table\\"
    
    # -------------------------------------------
    fn_CsvFilemaking ('DeserveCC_Status.xlsx' , 'Status Sample Data')
    # -------------------------------------------  

except Exception as e :
    print('FATAL >> '+ str(e))
    
        
        