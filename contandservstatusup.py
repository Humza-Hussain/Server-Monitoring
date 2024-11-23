import pymongo
import config
def insert_upstatus(svip,svername,contsername,ty,uptime,upstat):
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    sercontup_col=db[config.collections[6]]
    conserv={"serip":svip,"servername":svername,"name":contsername,"type":ty,"status":upstat,"uptime":uptime}
    obj_conserv=sercontup_col.insert_one(conserv)
    return obj_conserv
