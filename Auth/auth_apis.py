from flask_blueprint import Blueprint
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required,JWTManager,create_access_token,get_jwt_identity
from itsdangerous import URLSafeTimedSerializer
from flask import request,jsonify
from datetime import datetime, timedelta
import base64
import smtplib
import uuid
import pyotp
import config
from dateutil import relativedelta
from signup import Register
from login import Login
import hashlib 
s=URLSafeTimedSerializer('thisisvalue')
auth_blueprint = Blueprint('auth_blueprint', __name__)
@auth_blueprint.route('/signup',methods=['POST'])
@cross_origin()
def signup():
    issuccess=False;fullname=""
    userregister_col=db[config.collections[8]]
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    fullname=fname+" "+lname
    if not fname and not lname and not email:
        return jsonify({"Value":"Fields with asteric are neccessary","status":"204"}) 
    else:
        usrid=uuid.uuid4()
        issuccess=Register(userregister_col,usrid,fullname,"",email,"prodowner",False,"","","","","",False,False,"",0,0,False)
        if issuccess:
            token=s.dumps({"userid":str(usrid)},salt='email-verify')
            #link=url_for('verifyemail',token=token,_external=True)
            url='https://1d23-154-192-17-28.ngrok-free.app /varification/{}'.format(token)
            subject = f'Email Verification'
            body = f'email verification {url}'
            smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
            smtp.starttls()
            smtp.login(config.smtp_username, config.smtp_password)

            message = f'Subject: {subject}\n\n{body}'

            smtp.sendmail(config.sender_email, [email], message)  # updated line

            smtp.quit()
            return jsonify({"messege":"Email sent successfully","emailverficationtoken":token,"success":issuccess,"status":"200"})             
        else:
            return jsonify({"messege":"User exist already","success":issuccess,"status":"203"})    

@auth_blueprint.route('/login',methods=['POST'])
@cross_origin()
def login():
    islogin=False;paktype="";pakvalue="";usrid=""
    userregister_col=db[config.collections[8]]
    email=request.form['email']
    password=request.form['password']
    passwordbyte=password.encode()
    hashedpassword=hashlib.sha256(passwordbyte)
    passwordhash=hashedpassword.hexdigest()
    if not email or not password:
        return jsonify({"messege":"Incorrect username or password","success":False,"status":"400"})
    else:
        islogin,paktype,pakvalue,usrid=Login(userregister_col,email,passwordhash)
        usrobj=userregister_col.find_one({"email":email})
        if usrobj!=None:
            usrobjpass=userregister_col.find_one({"password":passwordhash})
            if usrobjpass==None:
                return jsonify({"messege":"Please enter correct email and password","success":False,"status":"400"})
        if  usrid=="" and islogin==False:
            return jsonify({"messege":"User not exist please sign up","success":False,"status":"404"})
        if islogin: 
            usrobj=userregister_col.find_one({"_id":usrid})
            if usrobj!=None:
                if usrobj["suspended"]:
                    return jsonify({"messege":"this user is suspended by administrator","success":False,"status":"404"}) 
                else:
                    totp = pyotp.TOTP(config.key)
                    val=totp.now()
                    secret_key=pyotp.random_base32()
                    query={"$set":{"secret_key":secret_key,"code":val,"authenticated":False}}
                    userregister_col.update_one({"email":email,"password":passwordhash},query)
                    subject = f'OTP Verification'
                    body = f'OTP : {val}'
                    smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
                    smtp.starttls()
                    smtp.login(config.smtp_username, config.smtp_password)

                    message = f'Subject: {subject}\n\n{body}'

                    smtp.sendmail(config.sender_email, [email], message)  # updated line

                    smtp.quit()
                    usrverify=email+" "
                    val=base64.b64encode(usrverify.encode())
                    usremailotp=val.decode("ascii")
                    return jsonify({"verificationtoken":usremailotp,"sucess":True,"status":"200"})
        else:
            return jsonify({"messege":"Please enter correct email and password","success":False,"status":"400"}) 

@auth_blueprint.route('/varification/<token>',methods=['POST'])
@cross_origin()
def verifyemail(token):
    print(token)
    verify_usr=s.loads(token, salt='email-verify',max_age=8600)
    userregister_col=db[config.collections[8]]
    print(verify_usr)
    usrobj=userregister_col.find_one({"_id": verify_usr["userid"]})
    if usrobj!=None:
        if usrobj["_id"]==verify_usr["userid"]:
            usrobj["confirmed"]=True
            return jsonify({"messege":"email confirmed","status":"200"})
        else:
            return jsonify({"messege":"Invalid link or confirmation link has expired", "success":False,"status":"404"}) 
    else:
        return jsonify({"messege":"No user found", "success":False,"status":"404"})

@auth_blueprint.route('/validated/<token>',methods=['POST'])
@cross_origin()
def validateuser(token):
    user=s.loads(token, salt='email-verify',max_age=86000)
    userregister_col=db[config.collections[8]]
    confirmedpassword=request.form['cPassword']
    password=request.form['password']
    print(password)
    if confirmedpassword!="" or password!="":
        if password==confirmedpassword:
            t_n=datetime.now()
            passwordbyte=password.encode()
            hashedpassword=hashlib.sha256(passwordbyte)
            passwordhash=hashedpassword.hexdigest()
            usr_obj=userregister_col.find_one({"_id": user["userid"]})
            if usr_obj!=None:
                query={"$set":{"confirmed":True,"createdon":t_n,"password":passwordhash}}
                userregister_col.update_one({"_id":user["userid"]},query)
                return jsonify({"Messege":"Password updated successfully","success":True,"status":"200"})
                #else:
                    #return jsonify({"messege":"Password entered already","success":False,"status":"203"})    
            else:
                return jsonify({"messege":"User not found","success":False,"status":"404"})
        else:
            return jsonify({"messege":"Password not matched","success":False,"status":"403"})
    else:
        return jsonify({"Messege":"Either one of field is empty","success":False,"status":"204"})

@auth_blueprint.route('/verifyotp',methods=['POST'])
@cross_origin()
def verifyotp():
    usremaillst=[];chk=False;usremailotp=""
    val=request.form["otp"]
    usremailotp=request.form["token"]
    usremailotp=base64.b64decode(usremailotp)
    usrotpemailval=usremailotp.decode("ascii")
    usremaillst=usrotpemailval.split(" ",1)
    userregister_col=db[config.collections[8]]
    server_col=db[config.collections[11]]
    package_col=db[config.collections[10]]
    usrobj=userregister_col.find_one({"email":usremaillst[0]})
    if not val:
        return jsonify({"messege":"please enter otp","success":False,"status":"400"})
    if usrobj!=None:
        if usrobj["email"]==usremaillst[0]:
            if usrobj["code"]==val:
                payload={"email":usrobj["email"],"role":usrobj["role"]}
                access_token=create_access_token(identity=usrobj["_id"],expires_delta=timedelta(minutes=720),additional_claims=payload,fresh=True)
                query={"$set":{"authenticated":True,"code":"","secret_key":""}}
                userregister_col.update_one({"email":usremaillst[0]},query)
                return jsonify({"access_token":access_token,"messege":"User is verified and authenticated","success":True,"status":"200"})
            elif usrobj["code"]!="":
                return jsonify({"messege":"invalid otp","success":False,"status":"403"})
            else:
                return jsonify({"messege":"otp has expired","success":False,"status":"400"})
        else:
            return jsonify({"messege":"email not found","success":False,"status":"400"})
    else:
        return jsonify({"messege":"user not found","success":False,"status":"400"})

@auth_blueprint.route('/userauthenticated',methods=['POST'])
@cross_origin()
@jwt_required()
def enabledauth():
    current_user_id=get_jwt_identity()
    userregister_col=db[config.collections[8]]
    subs_col=db[config.collections[13]]
    usrobj=userregister_col.find_one({"_id":current_user_id})
    st_time=datetime.now()
    subscribedat=datetime.now()
    end_time = st_time+ relativedelta(months=1)
    if usrobj["authenticated"]:
        if usrobj["role"]=="devop":
            if usrobj["alloweddeveopusrtoselpak"]:
                server_col=db[config.collections[11]]
                package_col=db[config.collections[10]]
                pak_obj=package_col.find_one({"package":usrobj["package"]})
                subsobj=subs_col.find_one({"usrid":current_user_id})
                svrobj=server_col.find({"owner_id":usrobj["_id"]})
                svrlst=list(svrobj)
                if usrobj["package"]=="" and usrobj["ptype"]=="":
                    url="https://4979-154-192-17-13.ngrok-free.app/packages"
                    #insert_subscription(current_user_id,"trial","",st_time,end_time,subscribedat,"monthly",True,"","","")
                    return jsonify({"URL":url, "messege":"No package is selected yet","success":True,"status":"200"})
                if pak_obj!=None:        
                    if usrobj["package"]=="trial" and usrobj["ptype"]=="unpaid":
                        subsobj=subs_col.find_one({"usrid":current_user_id,"package": usrobj["package"]})
                        sttime=subsobj["start_time"]
                        t_now=datetime.now()
                        timeduration=sttime-t_now
                        if timeduration.days>pak_obj["duration"]:
                            url="https://4979-154-192-17-13.ngrok-free.app/packages"
                            return jsonify({"URL":url,"messege":"Your trial package is expired","success":False,"status":"200"})
                        if len(svrlst)>int(pak_obj["no of server"]):
                            url="https://4979-154-192-17-13.ngrok-free.app/packages"
                            return jsonify({"URL":url,"messege":"you can not add more servers and update your package","success":True,"status":"200"})
                        else:
                            url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                            return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                    if usrobj["package"]=="basic" and usrobj["ptype"]=="paid":
                        pak_obj_basic=package_col.find_one({"package":usrobj["package"]})
                        if len(svrlst)>int(pak_obj_basic["no of server"]):
                            url="https://4979-154-192-17-13.ngrok-free.app/packages"
                            return jsonify({"URL":url,"messege":"you cannot add more servers","success":True,"status":"200"})
                        else:
                            url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                            return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                    if usrobj["package"]=="premium" and usrobj["ptype"]=="paid":
                        pak_obj_premium=package_col.find_one({"package":usrobj["package"]})
                        if len(svrlst)>int(pak_obj_premium["no of server"]):
                            url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                            return jsonify({"URL":url,"messege":"you have already availed premium package","success":True,"status":"200"})
                        else:
                            url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                            return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"200"}) 
            else:
                if usrobj["package"]=="trial" and usrobj["ptype"]=="unpaid":
                    subsobj=subs_col.find_one({"usrid":current_user_id,"package": usrobj["package"]})
                    sttime=subsobj["start_time"]
                    t_now=datetime.now()
                    timeduration=sttime-t_now
                    if timeduration.days>pak_obj["duration"]:
                        return jsonify({"messege":"Your trial package is expired ask product owner to update package","success":False,"status":"200"})
                    if len(svrlst)>int(pak_obj["no of server"]):
                        return jsonify({"messege":"you can not add more servers and ask product owner to update your package","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                if usrobj["package"]=="basic" and usrobj["ptype"]=="paid":
                    pak_obj_basic=package_col.find_one({"package":usrobj["package"]})
                    if len(svrlst)>int(pak_obj_basic["no of server"]):
                        return jsonify({"messege":"you cannot add more servers ask product owner to update package","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                if usrobj["package"]=="premium" and usrobj["ptype"]=="paid":
                    pak_obj_premium=package_col.find_one({"package":usrobj["package"]})
                    if len(svrlst)>int(pak_obj_premium["no of server"]):
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"you have already availed premium package","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"200"})
        if  usrobj["role"]=="devop" or usrobj["role"]=="prodowner" or usrobj["role"]=="admin":
            server_col=db[config.collections[11]]
            package_col=db[config.collections[10]]
            pak_obj=package_col.find_one({"package":usrobj["package"]})
            subsobj=subs_col.find_one({"usrid":current_user_id})
            svrobj=server_col.find({"owner_id":usrobj["_id"]})
            svrlst=list(svrobj)
            if usrobj["package"]=="" and usrobj["ptype"]=="":
                url="https://4979-154-192-17-13.ngrok-free.app/packages"
                #insert_subscription(current_user_id,"trial","",st_time,end_time,subscribedat,"monthly",True,"","","")
                return jsonify({"URL":url, "messege":"No package is selected yet","success":True,"status":"200"})
            if pak_obj!=None:        
                if usrobj["package"]=="trial" and usrobj["ptype"]=="unpaid":
                    subsobj=subs_col.find_one({"usrid":current_user_id,"package": usrobj["package"]})
                    sttime=subsobj["start_time"]
                    t_now=datetime.now()
                    timeduration=sttime-t_now
                    if timeduration.days>pak_obj["duration"]:
                        url="https://4979-154-192-17-13.ngrok-free.app/packages"
                        return jsonify({"URL":url,"messege":"Your trial package is expired","success":False,"status":"200"})
                    if len(svrlst)>int(pak_obj["no of server"]):
                        url="https://4979-154-192-17-13.ngrok-free.app/packages"
                        return jsonify({"URL":url,"messege":"you can not add more servers and update your package","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                if usrobj["package"]=="basic" and usrobj["ptype"]=="paid":
                    pak_obj_basic=package_col.find_one({"package":usrobj["package"]})
                    if len(svrlst)>int(pak_obj_basic["no of server"]):
                        url="https://4979-154-192-17-13.ngrok-free.app/packages"
                        return jsonify({"URL":url,"messege":"you cannot add more servers","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"201"})
                if usrobj["package"]=="premium" and usrobj["ptype"]=="paid":
                    pak_obj_premium=package_col.find_one({"package":usrobj["package"]})
                    if len(svrlst)>int(pak_obj_premium["no of server"]):
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"you have already availed premium package","success":True,"status":"200"})
                    else:
                        url="https://4979-154-192-17-13.ngrok-free.app/dashboard"
                        return jsonify({"URL":url,"messege":"servers limit not exceed","success":True,"status":"200"})
        if usrobj["role"]=="monitorusr":
            url="https://c6de-182-191-95-80.ngrok-free.app/graph"
            return jsonify({"URL":url,"messege":"redirect user to graph dashboard","success":True,"status":"200"})
        else:
            return jsonify({"messege":"User created without a role","success":False,"status":"400"})
    else:
        return jsonify({"messege":"unauthenticated user","success":False,"status":"401"})
    
@auth_blueprint.route('/resendotp',methods=['POST'])
@cross_origin()
def resendotp():
    usrotpemail=request.form["token"]
    usremaillst=[];usremailstr=""
    usremailotp=base64.b64decode(usrotpemail)
    usrotpemailval=usremailotp.decode("ascii")
    usremaillst=usrotpemailval.split(" ",1)
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find_one({"email":usremaillst[0]})
    if usrobj!=None:
        secret_key=pyotp.random_base32()
        totp=pyotp.TOTP(secret_key)
        otp=totp.now()
        subject = f'OTP Verification'
        body = f'OTP : {otp}'
        smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
        smtp.starttls()
        smtp.login(config.smtp_username, config.smtp_password)

        message = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(config.sender_email, [usremaillst[0]], message)  # updated line

        smtp.quit()
        print(usremaillst)
        for val in usremaillst:
            usremailstr+=val+" "
        encodedusremailstr=base64.b64encode(usremailstr.encode())
        usremail=encodedusremailstr.decode("ascii")
        query={"$set":{"code":otp,"secret_key":secret_key}}
        userregister_col.update_one({"email":usremaillst[0]},query)
        return jsonify({"optemail":usremail,"messege":"otp is sent successfully","success":True,"status":"200"})
    else:
        return jsonify({"messege":"Email is not found","success":False,"status":"400"})

