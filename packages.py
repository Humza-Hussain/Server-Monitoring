import pymongo 
import uuid
def insert_package(pakname,duration,price,accounttype,description,noofserver,createdat,typeofpackage,planid,isactivate,updatedat,noofdevopusrs,noofmonitorusrs):
    con_str="mongodb://localhost:27017"
    Client=pymongo.MongoClient(con_str)
    db=Client["ServerData"]
    pak_coll=db["Packages"]
    pak_data={"planid":planid,"package":pakname,"duration":duration,"price":price,"accounttype":accounttype,"description":description,"no of server":noofserver,"type of package":typeofpackage,"isactivate":isactivate,"createdat":createdat,"updatedat":updatedat,"no of deveopusrs":noofdevopusrs,"no of monitorusrs":noofmonitorusrs}
    pak_coll.insert_one(pak_data)