import requests
import json
from requests.auth import HTTPBasicAuth,HTTPDigestAuth

try:
    URL = "https://cloud.mongodb.com/api/atlas/v1.0/groups/6118d6fe9b36265361173dae/databaseUsers/admin/ankit-mongo"
    
    UserName = 'newTestUser'
    Password = 'Test123'
    role = 'read'
    DBName = 'myTestDB'

    #PARAMS = { "databaseName": DBName,"password":Password, "roles" :[{'databaseName':DBName,'roleName':role,}] , "username":UserName }
    
    # hdr = {}
    # hdr = {'Content-Type': 'application/json','Accept':'application/json'}
    # hdr["Authorization"] = 'kypihees:59b6442b-35aa-43cd-bd8e-8b1499bbfa47'
 
    # print(hdr)
    
    #res = requests.get(url = URL , headers= hdr)
    res = requests.get(url = URL , auth =HTTPDigestAuth('kypihees','59b6442b-35aa-43cd-bd8e-8b1499bbfa47') )
    
    print(res)
    response_data = res.json()

    print(response_data)

except Exception as e:
    print("Exception occured :: ",str(e))