from pymongo import MongoClient
import config
def makehist(ip,servername,name,status,t_new,uptime,typ):
    Client=MongoClient(config.connectstring)
    db=Client[config.database]
    history_col=db[config.collections[2]]
    history_col.insert_one({"serip":ip,"severname":servername,"type":typ,"name":name,"status":status,"downtime":t_new})
    #history_col.insert_one({"serip":ip,"severname":servername,"type":typ,"name":name,"status":status,"downtime":t_new,"uptime":uptime})