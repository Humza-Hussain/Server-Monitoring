import config
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()
class appconfiguration:
    SECRET_KEY=os.environ["SECRET_KEY"]
    # MONGO_URI=config.connectstring
    # SESSION_TYPE="mongodb"
    #SESSION_MONGODB=MongoClient(MONGO_URI)
    # SESSION_MONGODB_DB=config.database
    # SESSION_MONGODB_COLLECT=config.collections[9]
    