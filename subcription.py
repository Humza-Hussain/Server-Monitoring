import pymongo 
def insert_subscription(usrid,pkname,price,starttime,endtime,subcribedat,typeofsub,subactive,cancelat,updatedat,subid):
    con_str="mongodb://localhost:27017"
    Client=pymongo.MongoClient(con_str)
    db=Client["ServerData"]
    subcription_coll=db["Subscription"]
    subscribed_data={"subcriptionid":subid,"usrid":usrid,"package":pkname,"price":price,"isactive":subactive,"start_time":starttime,"end_time":endtime,"subscribedat":subcribedat,"typeofsub":typeofsub,"cancelat":cancelat,"updatedat":updatedat}
    subcription_coll.insert_one(subscribed_data)