import traceback
import pymongo

client = pymongo.MongoClient(
        "mongodb+srv://bhaskar69:Bhaskarsaikia2007@cluster0.yo1tfgw.mongodb.net/?retryWrites=true&w=majority"
)
result = str(client)

if "connect=True" in result:
    try:
        print("MONGODB CONNECTED SUCCESSFULLY ✅")
    except:
        pass
else:
    try:
        print("MONGODB CONNECTION FAILED ❌")
    except:
        pass

folder = client["MASTER_DATABASE"] 
usersdb = folder.USERSDB 
chats_auth = folder.CHATS_AUTH 
gcdb = folder.GCDB 
sksdb = client["SKS_DATABASE"].SKS 
confdb = client["SKS_DATABASE"].CONF_DATABASE
