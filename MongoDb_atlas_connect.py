from pymongo import MongoClient

try:
    conn = MongoClient('mongodb+srv://ankit-mongo:ak-mongo@cluster0.swkyd.mongodb.net/MysecondDB?retryWrites=true&w=majority')
    print("Connected successfully!!!")
except Exception as e:  
    print(str(e))
    
myFirstDatabase = conn['MysecondDB']
SampleCollection = myFirstDatabase['sampleCollectionNew']

SampleCollection.insert_one({"Name":'ronaldo443',"Age":45})