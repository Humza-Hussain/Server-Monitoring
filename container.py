import pymongo
import config
def insert_container(svip,svername,container,stat,oldt_now,newt_now):
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    container_col=db[config.collections[0]]
    usr_container={"serip":svip,"servername":svername,"containername":container,"status":stat,"old_time":oldt_now,"new_time":newt_now}
    obj_container=container_col.insert_one(usr_container)
    return obj_container