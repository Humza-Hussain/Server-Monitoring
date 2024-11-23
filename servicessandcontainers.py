import pymongo
import config
def insert_service_and_container(svip,name,sercontyp):
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    service_col=db[config.collections[12]]
    usr_service_cont={"serip":svip,"name":name,"type":sercontyp}
    obj_service=service_col.insert_one(usr_service_cont)
    return obj_service