import os
import pyodbc
import pandas as pd

def py_Connect_MSSQL():
    conct = pyodbc.connect(Driver='{SQL Server}',
                      Server='servername',
                      Database='Ankit_DB',
                      Trusted_Connection='yes',
                      autocommit=True)
    return  conct


vr_conn=py_Connect_MSSQL()
vr_crsr=vr_conn.cursor()

vr_CurrentDir = os.getcwd()

fread = open(vr_CurrentDir+'\\IN\\InputQry.txt','r').read()
fread =fread.replace('\n',' ')
print(fread)

writer = pd.ExcelWriter(vr_CurrentDir+'\\OUT\\SampleOUT.xlsx', engine='xlsxwriter')

if os.path.exists(vr_CurrentDir+'\\OUT\\SampleOUT.xlsx'):
    print('\n** ..OUT file already Exists.. **\n\r')

else:
    # ======================================================================
    vr_crsr.execute(fread)
    # ======================================================================
    df_list =[]

    column_names = [col[0] for col in vr_crsr.description] # Get column names from MySQL

    for row in vr_crsr.fetchall():
        df_list.append({name: row[i] for i, name in enumerate(column_names)})

    df1 = pd.DataFrame(df_list)
    print(df1)
    print('\n')

    df1.to_excel(writer, sheet_name='Sheet1')


    i = 1

    while i < 40:
        if (vr_crsr.nextset() is True):
            dfnext_data = []
            sheetname ='Sheet'+str((str(i+1)))

            column_names = [col[0] for col in vr_crsr.description] # Get column names from MySQL

            for row in vr_crsr.fetchall():
                dfnext_data.append({name: row[i] for i, name in enumerate(column_names)})

            dfNxt = pd.DataFrame(dfnext_data)
            print(dfNxt)
            print('\n')

            dfNxt.to_excel(writer, sheet_name=sheetname)
            
        i= i+1

    writer.save()

    print('\n\r$$$... Xls Made Successfully ...$$$')


