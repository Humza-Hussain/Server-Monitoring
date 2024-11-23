from flask import Flask, request,jsonify,send_file,render_template,Response
from flask_cors import cross_origin, CORS
#from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from operator import itemgetter
import base64
import pymongo 
from flask_jwt_extended import JWTManager
from functools import wraps
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from appconfig import appconfiguration
import config
from pathlib import Path 
app = Flask(__name__)
app.config.from_object(appconfiguration)
app.config['JWT_SECRET_KEY']=b'uufiofreuy'
jwt=JWTManager(app)
Client=pymongo.MongoClient(config.connectstring)
smtp_server = config.stmpserv
smtp_port =config.stmpport
smtp_username = config.usremail 
smtp_password = config.usrpassword
sender_email = config.senderemail
reciever_email = config.receiveremail
def create_app():
    api_vi_cors_config = {
        "origins": "https://c6de-182-191-95-80.ngrok-free.app",
        "methods": ["OPTIONS", "GET", "POST"]
    }
    CORS(app, resources={
        r"/*": api_vi_cors_config
    })
    app.config['CORS_HEADERS'] =['Content-Type','Authorization']
    encoded_credentials = base64.b64encode(f"{config.client_id}:{config.client_secret}".encode()).decode('ascii')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }
    db=Client[config.database]
    blocklist=set()


if __name__ == '__main__':
    app.run(debug=True)
         
