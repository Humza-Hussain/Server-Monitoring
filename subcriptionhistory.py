import pymongo 
def insert_subscritionhistory(usrid,pkname,trasactionid,price,updatedpak,previouspak):
    con_str="mongodb://localhost:27017"
    Client=pymongo.MongoClient(con_str)
    db=Client["ServerData"]
    pak_coll=db["Subscription History"]
    subscribed_data={"usrid":usrid,"package":pkname,"price":price,"transactionid":trasactionid,"updatedpak":updatedpak,"previouspak":previouspak}
    pak_coll.insert_one(subscribed_data)