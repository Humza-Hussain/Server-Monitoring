import pymongo
import config
def insert_service(svip,svername,service,stat,oldt_now,newt_now):
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    service_col=db[config.collections[1]]
    usr_serv={"serip":svip,"servername":svername,"servicesname":service,"status":stat,"old_time":oldt_now,"new_time":newt_now}
    obj_service=service_col.insert_one(usr_serv)
    return obj_service
