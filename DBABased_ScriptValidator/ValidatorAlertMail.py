import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import sqlite3


class ValidatorAlertSetup:

    # conn = sqlite3.connect('D:\SVN_Checkout\Applications\CoreBankCard\CreditProcessing\Trunk\ControlParameters\Sscripts_VALIDATORS\SQLlite_DB'+'\\ValidatorAlertDB.db')
    # conn.isolation_level = None
    # var_cur=conn.cursor()
    v_CurrentDir = os.getcwd()

    def fn_Alertmailgenerator(self,Filename,HostName,Status):
        
        SERVER="hst name"

        me = 'ankit.kumar@m.cm'
        address_book = ['ankit.kumar@m.cm'] #controlteam@m.cm 'rbhargava@m.cm','rahul.kumar@m.cm'

        if Status=='SUCCESS':
            header='<h4 style="color:green;">[SCRIPT_VALIDATOR_Running_Alert]_[SUCCESS]</h4>'
        else:
            header='<h4 style="color:red;">[SCRIPT_VALIDATOR_Running_Alert]_[FAILURE]</h4>'
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg['Subject'] = "[Control_Script_VALIDATOR_Running_Alert]"
        msg['From'] = me
        msg['To'] = ','.join(address_book)
        

        # Create the body of the message (a plain-text and an HTML version).
        html = """\
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
            <th>LogFileLoc</th>
            <th>Status</th>
        </tr>
        <tr style="color:blue;">
            <td><first_data></td>
            <td><second_data></td>
            <td><third_data></td>
            <td><fouth_data></td>
        </tr>
        </table>

        </body>
        </html>
        """
        html=html.replace('<first_data>',HostName)
        html=html.replace('<second_data>',Filename)
        html=html.replace('<third_data>',HostName+'\log')
        html=html.replace('<fouth_data>',Status)
        html=html.replace('{Header}',header)

        # Record the MIME types of both parts - text/plain and text/html.
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        # Send the message via local SMTP server.
        if Status=='SUCCESS':
            try:
                s = smtplib.SMTP(SERVER)
                s.sendmail(me, address_book, msg.as_string())
                s.quit()   
                print('\n\r** Alert Mail sent successfully **')
            except:
                print('\n\r **There was an exception**')  
        
        else:
            f = open(self.v_CurrentDir+'\\OutFiles\\ValidatorExceptions.xml')

            attachment = MIMEText(f.read())
            attachment.add_header('Content-Disposition', 'attachment', filename='ExceptionsList.txt')           
            msg.attach(attachment)

            part1 = MIMEText(html, 'html')

            msg.attach(part1)

            
            try:
                s = smtplib.SMTP(SERVER)
                s.sendmail(me, address_book, msg.as_string())
                s.quit()   
                print('\n\r** Alert Mail sent successfully **')
            except:
                print('\n\r **There was an exception**')  
