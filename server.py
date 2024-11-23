import pymongo 
import uuid
def insert_server(owner_id,svip,servername):
    id=str(uuid.uuid4())
    con_str="mongodb://localhost:27017"
    Client=pymongo.MongoClient(con_str)
    db=Client["ServerData"]
    server_coll=db["Servers"]
    svr_data={"_id":id,"owner_id":owner_id,"ip":svip,"serv_name":servername}
    server_coll.insert_one(svr_data)
            