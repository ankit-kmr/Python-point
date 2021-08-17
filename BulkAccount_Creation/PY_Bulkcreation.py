import flask
from flask import request, jsonify
import json ,requests
from termcolor import colored, cprint

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False

resBody ={}

ApiUrl = 'http://WEB15/AnkitK_APIHandlers/ankitkjsonCoreIssueFinalAccountCreation.aspx'

def fn_AccountCreationReq(UsrID ,Pass ,ProductID ,storeName ,Fname ,Lname ,MailID ,SSN ,BTable ,Bcycle ,Source):
    global vrTotalAcctCreated

    hdr = {'Content-Type': 'application/json','Accept':'application/json'}
    parameters = {
        "Password":"",
        "UserID":"",
        "RecordNumber":"1",
        "ProductID":"",
        "MerchantID":"",
        "StoreName":"",
        "CreditLimit":"5000",
        "CurrencyCode":"840",
        "AccountType":"01",
        "Title":"",
        "FirstName":"",
        "MiddleName":"",
        "LastName":"",
        "SNSuffix":"",
        "AddressLine1":"12 Avenue New one",
        "AddressLine2":"",
        "State":"GA",
        "City":"Atlanta",
        "PostalCode":"30093",
        "Country":"US",
        "EmailID":"",
        "LanguageIndicator":"",
        "HomePhoneNumber":"456346346364",
        "WorkPhoneNumber":"",
        "MobilePhoneNumber":"",
        "DateOfBirth":"08311993",
        "EmployerName":"Joe",
        "EmployeeNumber":"",
        "MotherMaidenName":"",
        "SocialSecurityNumber":"",
        "GovernmentIDType":"",
        "GovernmentID":"",
        "IDIssueDate":"",
        "IDExpirationDate":"",
        "IDIssueCountry":"",
        "IDIssueState":"",
        "BillingTable":"",
        "CardsRequested":"",
        "MobileCarrier":"",
        "EmbossingLine4":"",
        "BillingCycle":"",
        "NameonCard":"",
        "TotalAnnualIncome":"100000",
        "CurrentEmploymentMonths":"31",
        "ResidenceType":"1",
        "MonthsAtResidence":"31",
        "EmploymentType":"1",
        "Position":"",
        "EmployerContactPhoneNumber":"",
        "ApplicationVersion":"",
        "APIVersion":"2.0",
        "CalledID":"",
        "CallerID":"",
        "IPAddress":"",
        "SessionID":"",
        "Source":"",
        "AddressFlag":"1",
        "ShippingAddressLine1":"24 MG Road",
        "ShippingAddressLine2":"Near Upper Lake",
        "ShippingCity":"City",
        "ShippingState":"",
        "ShippingCountry":"JP",
        "ShippingPostalCode":"22222222",
        "ArtID":"abc123",
        "CosignerFlag":"0"
        }


    parameters['ProductID'] = ProductID
    parameters['UserID'] = UsrID
    parameters['Password'] = Pass
    parameters['StoreName'] = storeName
    parameters['FirstName'] = Fname
    parameters['LastName'] = Lname
    parameters['EmailID'] = MailID
    parameters['SocialSecurityNumber'] = SSN
    parameters['BillingTable'] = BTable
    parameters['BillingCycle'] = Bcycle
    parameters['Source'] = Source

    response = requests.post(ApiUrl, headers=hdr, json=parameters)
    print(response.status_code)
    rspns=response.json()

    msg=rspns.get('ErrorMessage')
    AcctNmber =rspns.get('AccountNumber')
    print(msg)
    
    if response.status_code == 200 :
        if msg=='Card Details Returned Successfully':
            cprint('Account Craeted successfully -->+'+str(AcctNmber) ,'green')
            vrTotalAcctCreated =vrTotalAcctCreated +1
    else:
        cprint(msg ,'red')

@app.route('/Ankit_Api/BulkAccountCreation', methods=['POST'])
def Fn_ReqDetails():
    global resBody
    vrTotalAcctCreated = 0

    try:
        content = request.get_json() # -- Json request Parsing
        print (content)
        print ("content['ProductID'] -->"+content['ProductID'])

        VrprodID = content['ProductID'] 
        VrUsrID = content['UserID'] 
        VrPass = content['Password'] 
        VrStrname = content['StoreName'] 
        Vrfname = content['FirstName'] 
        VrLname = content['LastName'] 
        VrSSN = content['SocialSecurityNumber'] 
        VrBT = content['BillingTable'] 
        VrBcycle = content['BillingCycle'] 
        VrSrc = content['Source'] 

        vrTotalreq =int(content['TotalAccount'])

        for r in range(1,vrTotalreq+1):
            MailID = Vrfname+'24123'+str(r)+'@mail.com'
            TmpSSN = int(VrSSN) +r
            VrSSN =str(TmpSSN)
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            fn_AccountCreationReq (VrUsrID ,VrPass ,VrprodID ,VrStrname ,Vrfname ,VrLname ,MailID ,VrSSN ,VrBT ,VrBcycle ,VrSrc)
            #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        
        
        resBody['UserID'] = VrUsrID
        resBody['Password'] = VrPass
        resBody['ProductID'] = VrprodID
        resBody['StoreName'] = VrStrname
        resBody['FirstName'] = Vrfname
        resBody['LastName'] = VrLname
        resBody['BillingTable'] = VrBT
        resBody['BillingCycle'] = VrBcycle
        resBody['Source'] = VrSrc
        resBody['TotalacctCreated'] = vrTotalAcctCreated

        return jsonify(resBody)
    
    except Exception as e :
        cprint('Fatal >>>+ '+str(e) ,'red')

app.run(host='127.0.0.1', port= 8090)
