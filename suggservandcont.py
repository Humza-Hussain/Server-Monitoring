import pymongo
import config
def insert_servandcont():
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    suggservcont_col=db[config.collections[9]]
    # usr_serv={"serip":svip,"servername":svername,"name":name,"type":typ}
    obj_suggservandcont=suggservcont_col.insert_many([
    {"name":"mysql","type":"service"},
    {"name":"postresql","type":"service"},
    {"name":"phpadmin","type":"service"},
    {"name":"mongo","type":"service"},
    {"name":"appache","type":"service"},
    {"name":"ngnix","type":"service"},
    {"name":"mysql","type":"container"},
    {"name":"appache","type":"container"},
    {"name":"mongo","type":"container"},
    {"name":"redis","type":"container"}
    ]
    )                                            