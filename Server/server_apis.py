from flask_blueprint import Blueprint
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required,JWTManager,get_jwt_identity,verify_jwt_in_request,get_jwt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
import config
from flask import request,jsonify,Response
import requests
import contandserv
from datetime import datetime,timedelta
from dateutil import relativedelta
import smtplib
from signup import Register
from websitedown import websitedownlog
from insertingserverdetailstobashscript import write_server_detail_to_bashscript
from insertserverperformancedatatofile import write_server_performance_to_bashscript
from addserverandsercont import add_server_and_service_and_cont
from subcription import insert_subscription
from operator import itemgetter
import pymongo
from pathlib import Path
from zipfile import ZipFile
import hashlib
import os
import uuid
import json
jwt=JWTManager()
s=URLSafeTimedSerializer('thisisvalue')
server_blueprint = Blueprint('server_blueprint', __name__)
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["role"]=="admin":
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403
        return decorator
    return wrapper

@server_blueprint.route('/contserv-down', methods=['POST'])
def contserv_down():
    ch_cont=False;ch_ser=False
    service_col=db[config.collections[1]]
    container_coll=db[config.collections[0]]
    history_col=db[config.collections[2]]
    data = request.get_json()
    try:
        if data==None:
            return 'error'
        else:
            ip = data.get('svip', '')
            servername = data.get('servername', '')
            owner_id = data.get('owner_id', '')
            servicelst = data.get('service', '')
            status = data.get('status', '')
            container_name=data.get('container', '')
            container_status=data.get('container_status', '')
            if ip!="" and servername!=""and status!=""and owner_id!=""and container_status!="":
                ch_ser,ch_cont=contandserv(ip,servername,service_col,container_coll,status,servicelst,container_status,container_name)                                    
                maxcounthist(history_col)
                if ch_ser or ch_cont:
                    # lstserv=lsttoken(servicelst)
                    # lstcont=lsttoken(container_name)            
                    # subject = f'Service is down on {servername} IP: {ip}'
                    # body = f'Server: {servername}\n with IP: {ip}\n Services are:\n {lstserv} \n Containers are :{lstcont} \n Status: {status} \n '
                    # smtp = smtplib.SMTP(smtp_server, smtp_port)
                    # smtp.starttls()
                    # smtp.login(smtp_username, smtp_password)

                    # message = f'Subject: {subject}\n\n{body}'

                    # smtp.sendmail(sender_email, [reciever_email], message)  # updated line
    
                    # smtp.quit()
                    x=0
                    return jsonify({"messege":"services or containers are down","success":True,})
                else:
                    return jsonify({"success":False,"status":"All services and containers are up"})     
            else:
                return jsonify({"success":False})                           
    except ValueError as e:
        return jsonify({"Error":e})
@server_blueprint.route('/serverperformance',methods=['POST'])
def serverperformance():
    perf_per=100.00
    try:
        sver_perf_coll=db[config.collections[5]]
        data=request.get_json()
        if data==None:
            return jsonify({"Error":False})
        else:
            ram_usage=data.get('mem_used_percent',' ')
            disk_usage=data.get('disk_used_percent',' ')
            #numb_of_processes=data.get('process_count',' ')
            cpu_usage=data.get('list_cores',' ')
            servername=data.get('servername',' ')
            svip=data.get("svip",' ')
            number_of_users=data.get("numb_user",' ')
            numb_usr=int(number_of_users)
            ram_u=float_value(ram_usage)
            disk_u=float_value(disk_usage)
            cpu_u=float_value(cpu_usage)
            left_ram=perf_per-ram_u
            left_disk=perf_per-disk_u
            time_n=datetime.now()
            if cpu_usage=="" or ram_usage=="" or disk_usage=="" or numb_usr==0:
                return  jsonify({"val":False}) 
            else:
                j=0
                ptr_lst= sver_perf_coll.find()
                svrperflst=list(ptr_lst)
                legtsvrper=len(svrperflst)
                if legtsvrper==0:
                    sver_perf_coll.insert_one({"ram_usage":str(ram_u),"disk_usage":str(disk_u),"list_cores":str(cpu_u),"svip":svip,"servername":servername,"numb_users":numb_usr,"time":time_n}) 
                else:
                    print(legtsvrper)
                    if  legtsvrper>30:
                        frstdocval=svrperflst[j]["_id"]
                        sver_perf_coll.delete_one({"_id":frstdocval})
                    sver_perf_coll.insert_one({"ram_usage":str(ram_u),"disk_usage":str(disk_u),"list_cores":str(cpu_u),"svip":svip,"servername":servername,"numb_users":numb_usr,"time":time_n})  
                subject = f'Server Performance of {servername}'
                body = f'Memory usage: {ram_usage} \n Disk usage: {disk_usage}\n Cpu usage:{cpu_u} \n Number of users: {numb_usr}\n'
                smtp = smtplib.SMTP(smtp_server, smtp_port)
                smtp.starttls()
                smtp.login(smtp_username, smtp_password)

                message = f'Subject: {subject}\n\n {body}'

                smtp.sendmail(sender_email, [reciever_email], message)  # updated line

                smtp.quit()
                return jsonify({"success":True}) 
    except ValueError:
        return jsonify({"error":True})

@server_blueprint.route('/website-down',methods=['POST'])
def website_down():
    websitehist_col=db[config.collections[4]]
    website_col=db[config.collections[3]]
    data = request.get_json()
    try:
        if data==None:
            return 'error'
        else:
            urlstatus=data.get('status', '')
            weburllst=data.get('website', '')
            usr_id=data.get('usrid', '')
            if weburllst!="" and urlstatus!="" and usr_id!="":
                alertval=websitedownlog(website_col,websitehist_col,weburllst,usr_id,urlstatus)
                if alertval:
                    lstweburl=lsttoken(weburllst)         
                    subject = f'Website down'
                    body = f'websites are:{lstweburl} \n Status: {urlstatus} \n '
                    smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
                    smtp.starttls()
                    smtp.login(config.smtp_username, config.smtp_password)

                    message = f'Subject: {subject}\n\n{body}'

                    smtp.sendmail(config.sender_email, [config.reciever_email], message)  # updated line
    
                    smtp.quit()
                else:
                    return jsonify({"success":False})
            else:
                t_now=datetime.now()
                websitehist_col.find({"usr_id":usr_id})
                query={"$set":{"status":200,"time":t_now}}
                websitehist_col.update_many({"usr_id":usr_id},query)
                return "all websites are up"
            maxcounthist(websitehist_col)
            return jsonify({"success":alertval})
            
    except ValueError as e:
        print(e)
        return jsonify({"success":False})

# @server_blueprint.route('/svrmetrictype',methods=['POST'])
def filtersverperfmetric(svip):
    distkusagevallst=[];cpuusagevallst=[];diskusagelst_time=[];cpuusagelst_time=[];finallst=[]
    col=db[config.collections[5]]
    svrperfdbindex="disk_usage"
    svrperfdbindex="list_cores"
    ptr=col.find({"svip":svip})
    for svrperf in ptr:
        distkusagevallst.append({"value":svrperf["disk_usage"]})
        distkusagevallst.append({"time":str(svrperf["time"])})
        cpuusagevallst.append({"value":svrperf["list_cores"]})
        cpuusagevallst.append({"time":str(svrperf["time"])}) 
    sorteddisklist=sorted(distkusagevallst, key=itemgetter('time'))
    sortedcpulist=sorted(cpuusagevallst, key=itemgetter('time'))
    finallst.append({"Disk_Usage":sorteddisklist})
    finallst.append({"Cpu_Usage":sortedcpulist})
    return finallst
    #return jsonify({"Server performance data":finallst}) 

@server_blueprint.route('/getserverusercount', methods=['POST'])
def getserverusercount():
    sver_perf_col=db[config.collections[5]]
    svip=request.form["svip"]
    svrptr=sver_perf_col.find({"svip":svip}).sort("time",1)
    lstsverperfdat=list(svrptr)
    if len(lstsverperfdat)==0:
        return jsonify({"messege":"No data is present is database","success":False,"status":"404"})
    else:
        return jsonify({"Number of users":lstsverperfdat[-1]["numb_users"],"success":True,"status":"200"})

@server_blueprint.route('/totalserviceuptime',methods=['POST'])
def totalserviceuptime():
    downtimelst=[];uptimelst=[];totaltimemonitor=[];totuptime=timedelta(0);lstdservicecontainerdown=[];lstdservicecontainerup=[]
    ip=request.form["svip"]
    servicename=request.form["name"]
    serconttype=request.form["serconttype"]
    svr_down_hist_col=db[config.collections[2]]
    svr_up_hist_col=db[config.collections[6]]
    dservicecontainerptr=svr_down_hist_col.find({"serip":ip,"name":servicename,"type":serconttype})
    upservicecontainerptr=svr_up_hist_col.find({"serip":ip,"name":servicename,"type":serconttype})
    lstdservicecontainerdown=list(dservicecontainerptr)
    lstdservicecontainerup=list(upservicecontainerptr)
    if len(lstdservicecontainerdown)==0 and len(lstdservicecontainerup):
        return jsonify({"messege":"No service and container monitored yet","success":False,"status":"201"})
    else:
        for dservcont in lstdservicecontainerdown:
            downdatdict={"time":dservcont["downtime"],"status":dservcont["status"]}
            downtimelst.append(downdatdict)
            totaltimemonitor.append(downdatdict)
        for upservcont in lstdservicecontainerup:
            updatdict={"time":upservcont["uptime"],"status":upservcont["status"]}
            uptimelst.append(updatdict)
            totaltimemonitor.append(updatdict)
        totaltimemonitorlst = sorted(totaltimemonitor, key=itemgetter('time'))
        for i in range(len(totaltimemonitorlst)-2):
            if totaltimemonitorlst[i]["status"]=="up" and totaltimemonitorlst[i+1]["status"]=="up":
                totuptime+=totaltimemonitorlst[i+1]["time"]-totaltimemonitorlst[i]["time"]
            if totaltimemonitorlst[i]["status"]=="up" and totaltimemonitorlst[i+1]["status"]=="down":
                totuptime+=totaltimemonitorlst[i+1]["time"]-totaltimemonitorlst[i]["time"]
        downtime=timedelta(days=1)-totuptime  
        return jsonify({"Down Time":downtimelst,"Up Time":uptimelst,"total time":totaltimemonitorlst,"uptime":str(totuptime),"downtime":str(downtime)})

@server_blueprint.route('/getsercontdataonbasistime',methods=['POST'])
def getsercontdataonbasismonitorhist():
    downtimelst=[];uptimelst=[];totaltimemonitor=[];lstdaydata=[];lstweekdata=[];lstmonthdata=[]
    t_now=datetime.now()
    ip=request.form["svip"]
    servicename=request.form["name"]
    serconttype=request.form["serconttype"]
    timeperiod=request.form["timeperiod"]
    svr_down_hist_col=db[config.collections[2]]
    svr_up_hist_col=db[config.collections[6]]
    dservicecontainerptr=svr_down_hist_col.find({"serip":ip,"name":servicename,"type":serconttype})
    upservicecontainerptr=svr_up_hist_col.find({"serip":ip,"name":servicename,"type":serconttype})
    lstdservicecontainerdown=list(dservicecontainerptr)
    lstdservicecontainerup=list(upservicecontainerptr)
    if len(lstdservicecontainerdown)==0 and len(lstdservicecontainerup):
        return jsonify({"messege":"No service and container monitored yet","success":False,"status":"201"})
    else:
        for dservcont in lstdservicecontainerdown:
            downdatdict={"time":dservcont["downtime"],"status":dservcont["status"]}
            downtimelst.append(downdatdict)
            totaltimemonitor.append(downdatdict)
        for upservcont in lstdservicecontainerup:
            updatdict={"time":upservcont["uptime"],"status":upservcont["status"]}
            uptimelst.append(updatdict)
            totaltimemonitor.append(updatdict)
        totaltimemonitorlst = sorted(totaltimemonitor, key=itemgetter('time'))
        if timeperiod=="day":
            for k in range(len(totaltimemonitorlst)-1):
                d=timedelta(days=1)
                duration=t_now-totaltimemonitorlst[k]["time"]
                if duration<=d:
                    data={"time":totaltimemonitorlst[k]["time"],"status":totaltimemonitorlst[k]["status"]}
                    lstdaydata.append(data)
            return jsonify({"Graph data by day":lstdaydata,"success":True,"status":"200"})
        if timeperiod=="weekly":
            for k in range(len(totaltimemonitorlst)-1):
                d=timedelta(days=7)
                duration=t_now-totaltimemonitorlst[k]["time"]
                if duration<=d:
                    data={"time":totaltimemonitorlst[k]["time"],"status":totaltimemonitorlst[k]["status"]}
                    lstweekdata.append(data)
            return jsonify({"Graph data by weekly":lstweekdata,"success":True,"status":"200"})
        if timeperiod=="monthly":
            for k in range(len(totaltimemonitorlst)-1):
                d=timedelta(days=30)
                duration=t_now-totaltimemonitorlst[k]["time"]
                if duration<=d:
                    data={"time":totaltimemonitorlst[k]["time"],"status":totaltimemonitorlst[k]["status"]}
                    lstmonthdata.append(data)
            return jsonify({"Graph data by monthly":lstmonthdata,"success":True,"status":"200"})
@server_blueprint.route('/contservhist',methods=['POST'])
def filterserconthist():
    lst_status=[];lst_time=[];lst_finallst=[];lst_name=[]
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    col=db[config.collections[2]]
    data=request.get_json()
    ip=data.get('serip', '')
    typ=data.get('typ', '')
    name=data.get('name','')
    filtptr=col.find({"serip":ip,"type":typ,"name":name})
    for res in filtptr:
        lst_status.append(res["status"])
        lst_time.append(str(res["time"]))
    val={ip:{name:lst_status, "time":lst_time}}
    lst_finallst.append(val)
    return jsonify({"filteredres":lst_finallst})            

@server_blueprint.route('/servercontainerdataforgraph',methods=['POST'])
def svrandcontdataforgraph():
    downlst=[];uplst=[];dsercontlst=[];upsercontlst=[];monitordata=[]
    svip=request.form["ip"]
    servcontname=request.form["name"]
    svrcontype=request.form["type"]
    ser_cont_hist_down=db[config.collections[2]]
    ser_cont_hist_up=db[config.collections[6]]
    servcontptrdown=ser_cont_hist_down.find({"serip":svip,"name":servcontname,"type":svrcontype})
    servcontptrup=ser_cont_hist_up.find({"serip":svip,"name":servcontname,"type":svrcontype})
    downlst=list(servcontptrdown)
    uplst=list(servcontptrup)
    if len(downlst)==0 and len(uplst)==0:
        return jsonify({"messege":"No service and container is monitored yet","success":False,"status":"200"})
    else:
        if len(downlst)==0:
            chkdown=False
        else:
            for dserv in downlst:
                downdatdict={"time":dserv["downtime"],"status":dserv["status"]}
                monitordata.append(downdatdict)
            chkdown=True
        if len(uplst)==0:
            chkup=False
        else:    
            for upserv in uplst:
                updatdict={"time":upserv["uptime"],"status":upserv["status"]}
                monitordata.append(updatdict)
            chkup=True
        timemonitor = sorted(monitordata, key=itemgetter('time'))
        return jsonify({"Graph data":timemonitor,"Up":chkup,"Down":chkdown,"success":True,"status":"200"})

@server_blueprint.route('/servicecontainerandperformancerelserverdataforgraph',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required()
def servandcontdatarelsvrforgraph():
    downlst=[];uplst=[];dsercontlst=[];svrperflst=[];containerupdown=[];fmonitordataservices=[];serviceupdown=[];totcontainerupdown=[];totupdownservice=[];svrdetailslst=[];usrserverdetailsdataforgraph=[] 
    #svip=request.form["ip"]
    current_usr_id=get_jwt_identity()
    # id=request.form["id"]
    # servcontname=request.form["name"]
    # svrcontype=request.form["type"]
    ser_cont_hist_down=db[config.collections[2]]
    ser_cont_hist_up=db[config.collections[6]]
    svervice_and_cont_coll=db[config.collections[12]]
    svr_coll=db[config.collections[11]]
    # svrobj=svr_coll.find_one({"_id":id})
    # svip=svrobj["ip"]
    svrptr=svr_coll.find({"owner_id":current_usr_id})
    for svr in svrptr:
        servivceptr=svervice_and_cont_coll.find({"serip":svr["ip"],"type":"service"})
        containerptr=svervice_and_cont_coll.find({"serip":svr["ip"],"type":"container"})
        servicenamelst=list(servivceptr)
        containernamelst=list(containerptr)
        for ser in servicenamelst:
            servptrdown=ser_cont_hist_down.find({"serip":svr["ip"],"name":ser["name"],"type":"service"})
            servptrup=ser_cont_hist_up.find({"serip":svr["ip"],"name":ser["name"],"type":"service"})
            upserviceslst=list(servptrup)
            downserviceslst=list(servptrdown)
            if len(downserviceslst)>0:
                for serdown in downserviceslst:
                    if ser["name"]==serdown["name"]:
                        downdatdict={"time":serdown["downtime"],"status":serdown["status"]}
                        serviceupdown.append(downdatdict)
            if len(upserviceslst)>0:
                for serup in upserviceslst:
                    if ser["name"]==serup["name"]:
                        updatdict={"time":serup["uptime"],"status":serup["status"],"type":serup["type"],"serip":serup["serip"],"name":serup["name"]}
                        serviceupdown.append(updatdict)
            sortedserviceupdownlist=sorted(serviceupdown, key=itemgetter('time'))
            totupdownservice.append({"Name":ser["name"],"Value":sortedserviceupdownlist})
            serviceupdown=[]
            sortedserviceupdownlist=[]
        for cont in containernamelst:
            contptrdown=ser_cont_hist_down.find({"serip":svr["ip"],"name":cont["name"],"type":"container"})
            contptrup=ser_cont_hist_up.find({"serip":svr["ip"],"name":cont["name"],"type":"container"})
            downcontainerslst=list(contptrdown)
            upcontainerlst=list(contptrup)
            if len(downcontainerslst)>0:
                for contdown in downcontainerslst:
                    if cont["name"]==contdown["name"]:
                        downdatdict={"time":contdown["downtime"],"status":contdown["status"]}
                        containerupdown.append(downdatdict)
            if len(upcontainerlst)>0:
                for contup in upcontainerlst:
                    if cont["name"]==contup["name"]:
                        updatdict={"time":contup["uptime"],"status":contup["status"],"type":contup["type"],"serip":contup["serip"],"name":contup["name"]}
                        containerupdown.append(updatdict)
            sortedcontainerupdownlist=sorted(containerupdown, key=itemgetter('time'))
            totcontainerupdown.append({"Name":cont["name"],"Value":sortedcontainerupdownlist})
            containerupdown=[]
            sortedcontainerupdownlist=[]
        svrperflst=filtersverperfmetric(svr["ip"])
        # svrdetailslst.append({"Services":totupdownservice})
        # svrdetailslst.append({"Containers":totcontainerupdown})
        # svrdetailslst.append({"Server Performance":svrperflst})
        usrserverdetailsdataforgraph.append({"IP":svr["ip"],"Server_Id":svr["_id"],"Services":totupdownservice,"Containers":totcontainerupdown,"Server_Performance":svrperflst})
        totcontainerupdown=[]
        totupdownservice=[]
    return jsonify({"graphdataforuserservers": usrserverdetailsdataforgraph})
    # return jsonify({"Graph data":timemonitor,"Up":chkup,"Down":chkdown,"success":True,"status":"200"})

@server_blueprint.route('/serverdetailfile',methods=['GET'])
def sendbashscriptfile():
    # fp=open(config.usrserverbashscript,'w')
    svrperfmonit=Path(config.serverperformancemonitorfp).name
    svrmonitor=Path(config.servermonitorfp).name
    with ZipFile(config.usrserverbashscript, 'w') as zip_object:
    # Adding files that need to be zipped
        zip_object.write(config.serverperformancemonitorfp,arcname=svrperfmonit)
        zip_object.write(config.servermonitorfp,arcname= svrmonitor)
    if os.path.exists(config.usrserverbashscript):
        fpb=open(config.usrserverbashscript,'rb')
        isobytes=fpb.read()
        os.remove(config.usrserverbashscript)
        return Response(isobytes,
                        mimetype='application/zip',
                        headers={'Content-Disposition': 'attachment;filename=serverbashscript.zip'})
    else:
        return jsonify({"messege:": "File not created yet", "success":False,"status":"404" })

@server_blueprint.route('/adduser',methods=['POST'])
@jwt_required()
def adduser():
    noofmonitorusr=0;nootdeveopusr=0;totnoofmonitorusr=0;totnoofdeveopusr=0;usrcreated=False;allowdevopuser=False
    fname=request.form['fname']
    lname=request.form['lname']
    email=request.form['email']
    typeusr=request.form['typeofusr']
    allowdevopusertoselectpak=request.form['allowdeveoptoselectpak']
    username=fname+" "+lname
    current_usrid=get_jwt_identity()
    userregister_col=db[config.collections[8]]
    pakage_col=db[config.collections[10]]
    usrobj=userregister_col.find_one({"_id":current_usrid})
    if usrobj!=None:
        if usrobj["role"]=="admin" or usrobj["role"]=="prodowner": 
            if not fname and not lname and not email and not typeusr:
                return jsonify({"Value":"Fields with asteric are neccessary","status":"204"}) 
            else:
                if not allowdevopusertoselectpak:
                    allowdevopuser=False
                    package=usrobj["package"]
                    ptype=usrobj["ptype"]
                else:
                    allowdevopuser=allowdevopusertoselectpak
                    if allowdevopuser:
                        package=""
                        ptype=""
                    else:
                        package=usrobj["package"]
                        ptype=usrobj["ptype"]
                pakobj=pakage_col.find_one({"package":usrobj["package"]})
                usrid=uuid.uuid4()
                if usrobj["package"]=="trial":
                    if int(usrobj["no of monitorusrs"])<=int(pakobj["no of monitorusrs"]):
                        if typeusr=="monitorusr":
                            noofmonitorusr=1
                            query={"$set":{"no of monitor":noofmonitorusr}}
                        usrcreated,token=emailsent(userregister_col,usrid,username,email,typeusr,current_usrid,allowdevopuser,package,ptype)
                        if usrcreated:
                            userregister_col.update_one({"_id":usrobj["_id"]},query)
                            return jsonify({"messege":"Email sent successfully","emailverficationtoken":token,"success":usrcreated,"status":"200"})
                        else:
                            return jsonify({"messege":"User already exist","success":False,"status":"400"}) 
                    if int(usrobj["no of deveopurs"])<=int(pakobj["no of deveopusrs"]):  
                        if typeusr=="deveopusr":
                            nootdeveopusr=1
                            query={"$set":{"no of deveop":nootdeveopusr}}
                        usrcreated,token=emailsent(userregister_col,usrid,username,email,typeusr,current_usrid,allowdevopuser,package,ptype)
                        if usrcreated:
                            userregister_col.update_one({"_id":usrobj["_id"]},query)
                            return jsonify({"messege":"Email sent successfully","emailverficationtoken":token,"success":usrcreated,"status":"200"})
                        else:
                            return jsonify({"messege":"User already exist","success":False,"status":"400"}) 
                    else:
                        return jsonify({"messege":"you cannot add more devop user or monitor user","success":False,"status":"400"})
                else:
                    usrcreated,token=emailsent(userregister_col,usrid,username,email,typeusr,current_usrid,allowdevopuser,package,ptype)
                    if usrcreated:
                        if typeusr=="monitorusr":
                            totnoofmonitorusr=int(usrobj["no of monitorusrs"])+noofmonitorusr
                            query={"$set":{"no of monitorusrs":totnoofmonitorusr}}
                        if typeusr=="deveopusr":
                            totnoofdeveopusr=int(usrobj["no of devopusrs"])+nootdeveopusr
                            query={"$set":{"no of devopusrs":totnoofdeveopusr}}
                        userregister_col.update_one({"_id":usrobj["_id"]},query)
                        return jsonify({"messege":"Email sent successfully","emailverficationtoken":token,"success":usrcreated,"status":"200"})
                    else:
                        return jsonify({"messege":"User already exist","success":False,"status":"400"})           
        else:
            return jsonify({"messege":"User have no access rights","succes":False,"status":"404"})  
    else:
        return jsonify({"messege":"user not found","succes":False,"status":"404"}) 

def emailsent(userregister_col,usrid,username,email,typeusr,current_usrid,allowdevopusr,packname,ptype):
    issuccess=Register(userregister_col,usrid,username,"",email,typeusr,False,"",packname,ptype,"","",False,False,current_usrid,0,0,allowdevopusr)
    if issuccess:
        token=s.dumps({"userid":str(usrid)},salt='email-verify')
        url='https://4979-154-192-17-13.ngrok-free.app/varification/{}'.format(token)
        subject = f'Email Verification'
        body = f'email verification {url}'
        smtp = smtplib.SMTP(config.smtp_server, config.smtp_port)
        smtp.starttls()
        smtp.login(config.smtp_username, config.smtp_password)

        message = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(config.sender_email, [email], message)  # updated line

        smtp.quit()
        return issuccess,token
@server_blueprint.route('/getallprodowner',methods=['GET'])
def getallprodowners():
    try:
        usrlst=[]
        userregister_col=db[config.collections[8]]
        usrptr=userregister_col.find({"role":"prodowner"})
        usrlst=list(usrptr)
        if len(usrlst)==0:
            return jsonify({"messege":"No user is created yet","status":"200"})
        else:
            return jsonify({"Users":usrlst,"status":"200","success":True})  
    except Exception as e:
        return jsonify({"message":"error","status":"500"})  

@server_blueprint.route('/getallservices',methods=['GET'])
def getallservices():
    lstservices=[]
    suggservcont_col=db[config.collections[9]]
    ptr=suggservcont_col.find({"type":"service"})
    for obj in ptr:
        lstservices.append(obj["name"])
    return jsonify({"Services":lstservices})
@server_blueprint.route('/getallcontainers',methods=['GET'])
def getallcontainers():
    lstcontainers=[]
    suggservcont_col=db[config.collections[9]]
    ptr=suggservcont_col.find({"type":"container"})
    for obj in ptr:
        lstcontainers.append(obj["name"])
    return jsonify({"Services":lstcontainers})
@server_blueprint.route('/insertserver',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization','Access-Control-Allow-Origin'])
@jwt_required()
def insertserver():
    serchk=False;conchk=False;ismodified_file=False;errdata={};ismodf=False
    try:
        current_user_id=get_jwt_identity()
        print(current_user_id)
        current_user_email=get_jwt()
        data=request.get_json()
        svip=data["ip"]
        svername=data["name"]
        services=data["service"]
        containers=data["container"]
        # svip=request.form['ip']
        # svername=request.form['name']
        # services=request.form['service']
        # containers=request.form['container']
        print(services)
        package_col=db[config.collections[10]]
        svr_coll=db[config.collections[11]]
        svervice_and_cont_coll=db[config.collections[12]]
        userregister_col=db[config.collections[8]]
        usr_obj= userregister_col.find_one({"_id":current_user_id,"email":current_user_email["email"]})
        print(usr_obj)
        pak_obj=package_col.find_one({"package":str(usr_obj["package"]),"accounttype":str(usr_obj["ptype"])})
        if svip!="" and svername!="":
            if usr_obj["role"]=="admin":
                svrptr=svr_coll.find({"owner_id":current_user_id})
                svrlst=list(svrptr)  
                if len(services)==0 and len(containers)==0:
                    return jsonify({"messege":"services and containers are empty","success":False,"status":"204"})
                else:
                    # if len(svrlst)>=int(pak_obj["no of server"]):
                    #     return jsonify({"messege":"you cannot add more server limit exceeded","success":False,"status":"400"})
                    # else:
                    ismodified_file=write_server_detail_to_bashscript(svip,prodownerid,svername,services,containers,config.svrdownurl)
                    if ismodified_file:
                        errdata=add_server_and_service_and_cont(services,containers,svip,svername,prodownerid,svr_coll,svervice_and_cont_coll)
                        ismodf=write_server_performance_to_bashscript(svip,svername,config.svrperformurl)
                        if ismodf:
                            return jsonify({"messege":errdata,"msg":"files created successfully"})
                        else:
                            return jsonify({"messege":errdata,"msg":"files not created"})
            if usr_obj["role"]=="devop":
                prodownerid=usr_obj["poid"]
                svrptr=svr_coll.find({"owner_id":prodownerid})
                svrlst=list(svrptr)  
                if len(services)==0 and len(containers)==0:
                    return jsonify({"messege":"services and containers are empty","success":False,"status":"204"})
                else:
                    # if len(svrlst)>=int(pak_obj["no of server"]):
                    #     return jsonify({"messege":"you cannot add more server limit exceeded","success":False,"status":"400"})
                    # else:
                    ismodified_file=write_server_detail_to_bashscript(svip,prodownerid,svername,services,containers,config.svrdownurl)
                    if ismodified_file:
                        errdata=add_server_and_service_and_cont(services,containers,svip,svername,prodownerid,svr_coll,svervice_and_cont_coll)
                        ismodf=write_server_performance_to_bashscript(svip,svername,config.svrperformurl)
                        if ismodf:
                            return jsonify({"messege":errdata,"msg":"files created successfully"})
                        else:
                            return jsonify({"messege":errdata,"msg":"files not created"})
                if usr_obj["role"]=="prodowner":
                    svrptr=svr_coll.find({"owner_id":current_user_id})
                    svrlst=list(svrptr)
                    if len(services)==0 and len(containers)==0:
                        return jsonify({"messege":"services and containers are empty","success":False,"status":"204"})
                    else:
                        # if len(svrlst)>=int(pak_obj["no of server"]):
                        #     return jsonify({"messege":"you cannot add more server limit exceeded","success":False,"status":"400"})
                        # else:
                        ismodified_file=write_server_detail_to_bashscript(svip,current_user_id,svername,services,containers,config.svrdownurl)
                        if ismodified_file:
                            errdata=add_server_and_service_and_cont(services,containers,svip,svername,current_user_id,svr_coll,svervice_and_cont_coll)
                            ismodf=write_server_performance_to_bashscript(svip,svername,config.svrperformurl)
                            if ismodf:
                                return jsonify({"messege":errdata,"msg":"files created successfully"})
                            else:
                                return jsonify({"messege":errdata,"msg":" file not created"})
            else:
                jsonify({"messege":"User have no access rights","success":False,"status":"400"}) 
        else:
            return jsonify({"messege":"either one of field is empty","success":False,"status":"203"})
    except Exception as e:
        return jsonify({"messege":"Exception occured","success":False,"status":"404"})
@server_blueprint.route('/selectpackage',methods=['POST'])
@jwt_required()
def subcribepackageusr():
    current_user_id=get_jwt_identity()
    data=request.get_json()
    userregister_col=db[config.collections[8]]
    package_col=db[config.collections[10]]
    pak=data["package"]
    if not pak :
        return jsonify({"messege":"either one of field is empty","success":False,"status":"203"})
    else:
        usrptr=userregister_col.find_one({"_id":current_user_id})
        pakobj=package_col.find_one({"package":pak})
        if usrptr!=None:
            if pakobj!=None:
                if pakobj["package"]=="trial":
                    if usrptr["role"]=="devop" or usrptr["role"]=="admin":
                        if usrptr["alloweddeveopusrtoselpak"]:
                            query={"$set":{"package":pakobj["package"],"ptype":pakobj["accounttype"]}}
                            userregister_col.update_one({"_id":current_user_id,"role":usrptr["role"]},query)
                            prodownerobj=userregister_col.find_one({"_id":usrptr["poid"],"role":"prodowner"})
                            if prodownerobj!=None:
                                userregister_col.update_one({"_id":prodownerobj["_id"]},query)
                                return jsonify({"planid":"","package name":pakobj["package"],"success":True,"status":"200"})
                            else:
                                return jsonify({"messege":"User not found","success":False,"status":"404"})
                        if usrptr["role"]=="prodowner" or usrptr["role"]=="admin": 
                            query={"$set":{"package":pakobj["package"],"ptype":pakobj["accounttype"]}}
                            userregister_col.update_one({"_id":current_user_id,"role":usrptr["role"]},query)
                            devopusrobj=userregister_col.find_one({"poid":usrptr["_id"],"role":"devop"})
                            if devopusrobj!=None:
                                userregister_col.update_one({"_id":devopusrobj["_id"]},query)
                                return jsonify({"planid":"","package name":pakobj["package"],"success":True,"status":"200"})
                            else:
                                return jsonify({"messege":"Devop User not found or not added","success":False,"status":"404"})
                else:
                    return jsonify({"planid":pakobj["planid"],"package name":pakobj["package"],"success":True,"status":"200"})
            else:
                return jsonify({"messege":"Package not found","success":False,"status":"404"})
        else:
            return jsonify({"messege":"User not found","success":False,"status":"404"})

@server_blueprint.route('/confirmedpackagesubcription',methods=['POST'])
@jwt_required()
def confirmedsubscription():
    ptype=""
    currentid=get_jwt_identity()
    subsid=request.form["subsid"]
    pakname=request.form["pakname"]  
    userregister_col=db[config.collections[8]]
    package_col=db[config.collections[10]]
    subs_coll=db[config.collections[13]]
    usrptr=userregister_col.find_one({"_id":currentid})
    pakobj=package_col.find_one({"package":pakname})
    subsobj=subs_coll.find_one({"usrid":currentid})
    st_time=datetime.now()
    subscribedat=datetime.now()
    if usrptr!=None:
        if pakobj!=None:
            if subsobj==None:
                if pakobj["type of package"]=="monthly":
                    end_time = st_time+ relativedelta(months=1)
                if pakobj["type of package"]=="yearly":
                    end_time= st_time+relativedelta(months=12)
                query={"$set":{"package":pakname,"ptype":pakobj["accounttype"]}}
                userregister_col.update_one({"_id":currentid},query)
                insert_subscription(currentid,pakobj["package"],pakobj["price"],st_time,end_time,subscribedat,pakobj["type of package"],True,"",datetime.now(),subsid)
                return jsonify({"messege":"user availed package successfully and subcription is activated","success":True,"status":"200"})
            else:
                upgradeuserpackage(pakname,subsid,currentid)
                return jsonify({"messege":"package updated successfully","success":True,"status":"200"})
        else:
            return jsonify({"messege":"package not found and subscription id is empty","success":False,"status":"404"})     
    else:
        return jsonify({"messege":"user not found ","success":False,"status":"404"})

# @server_blueprint.route('/createsubcription',methods=['GET'])
# def createsubscription():
#     return render_template('login.html')

@server_blueprint.route('/getsubscriptiondetail',methods=['GET'])
@jwt_required()
def getsubcriptiondetail():
    subs_coll=db[config.collections[13]]
    userregister_col=db[config.collections[8]]
    package_col=db[config.collections[10]]
    current_usr_id=get_jwt_identity()
    response=request.form["response"]
    subid=response["id"]
    email=response["email"]
    username=response["subscriber"]["name"]["full_name"]
    planid=response["planid"]
    pakobj=package_col.find_one({"planid",planid})
    usrobj=userregister_col.find_one({"_id":current_usr_id})
    if usrobj!=None:
        # subsobj=subs_coll.find_one({"usrid":usrobj["_id"]})
        # query={"$set":{"subscriptionid":subid}}
        # subs_coll.update_one({"usrid":usrobj["_id"]},query)
        query={"$set":{"subscritionid":subid}}
        userregister_col.update_one({"_id":usrobj["_id"]},query)
        #insert_subscription("",pakobj["package"],pakobj["price"],st_time,end_time,subscribedat,typeofsub,True,"",datetime.now())
@server_blueprint.route('/getuserpackage',methods=['GET'])
@jwt_required()
def getusrpackage():
    currentusrid=get_jwt_identity()
    userregister_col=db[config.collections[8]]
    pakage_col=db[config.collections[10]]
    subs_coll=db[config.collections[13]]
    usrobj=userregister_col.find_one({"_id":currentusrid})
    if usrobj!=None:
        pakobj=pakage_col.find_one({"package":usrobj["package"]})
        usrsubobj=subs_coll.find_one({"usrid":usrobj["_id"]})
        if pakobj!=None and usrsubobj!=None:
            usrpakdetail={"username":usrobj["username"],"package":usrsubobj["package"],"price":usrsubobj["price"],"type of subscription":usrsubobj["typeofsub"],"starttime":usrsubobj["start_time"],"endtime":usrsubobj["end_time"], "subscribeat":usrsubobj["subscribedat"]}
            return jsonify({"User package detail":usrpakdetail,"success":True,"status":"200"})
        else:
            return jsonify({"messege":"package not found or user has not subscribed yet","success":False,"status":"400"})

def upgradeuserpackage(pak,subsid,current_user_id):
    chkm=False
    userregister_col=db[config.collections[8]]
    package_col=db[config.collections[10]]
    subs_coll=db[config.collections[13]]
    st_time=datetime.now()
    subscribedat=datetime.now()
    end_time=datetime.now()
    if not pak:
        return jsonify({"messege":"either one of field is empty","success":False,"status":"203"})
    else:
        usrptr=userregister_col.find_one({"_id":current_user_id})
        pakobj=package_col.find_one({"package":pak})
        subsobj=subs_coll.find_one({"usrid":current_user_id})
        if usrptr!=None and subsobj!=None:
            if usrptr["package"]==pak:
                if subsobj["isactive"]:
                    if subsobj["typeofsub"]=="monthly":
                        end_time = st_time+ relativedelta(months=1)
                    if subsobj["typeofsub"]=="yearly":
                        end_time = st_time+ relativedelta(months=12)
                    query={"$set":{"package":pak,"price":pakobj["price"],"start_time":st_time,"end_time":end_time,"upgradededat":datetime.now(),"isactive":True,"subcriptionid":subsid}}
                    if usrptr["package"]=="premium":
                        if pak=="trial":
                            chkm=False
                            return jsonify({"messege":"you cannot downgrade to trial package", "success":False,"status":"200"})
                        if pak=="basic":
                            return jsonify({"messege":"you cannot downgrade to basic package", "success":False,"status":"200"})
                        else:
                            chkm=True
                    if usrptr["package"]=="basic":
                        if pak=="trial":
                            chkm=False
                            return jsonify({"messege":"you cannot downgrade to trial package", "success":False,"status":"200"})
                        else:
                            chkm=True
                    if chkm:
                        if pakobj["type of package"]=="monthly":
                            end_time = st_time+ relativedelta(months=1)
                        if pakobj["type of package"]=="yearly":
                            end_time= st_time+relativedelta(months=12)
                        subattime=subsobj["subscribedat"]
                        sttime=subsobj["start_time"]
                        edtime=subsobj["end_time"]
                        #timeforpackageused=datetime.now()-subattime
                        #print(timeforpackageused)
                        #noofday=edtime-sttime
                        #print(noofday.days)
                        #cost=float(str(pakobj["price"]))
                        #costperday=cost/noofday.days
                        #cost_of_package_used=timeforpackageused.days*costperday
                        #print(cost_of_package_used)
                        #print(timeforpackageused)
                        usrpakobj=package_col.find_one({"package":usrptr["package"]})
                        data = '{ "reason": "Subcription upgraded" }'

                        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions/'+subsobj["subcriptionid"]+'/cancel', headers=headers, data=data)
                        if response.status_code==204:
                            data = {
                                "plan_id":usrpakobj["planid"]
                            }
                            response = requests.patch('https://api-m.sandbox.paypal.com/v1/billing/subscriptions/'+subsid+'/revise', headers=headers, data=data)
                            if response.status_code==200:
                                subs_coll.update_one({"usrid":current_user_id,"package":subsobj["package"]},query)
                                query={"$set":{"package":pak,"ptype":pakobj["accounttype"]}}
                                userregister_col.update_one({"_id":current_user_id},query)
                                return jsonify({"messege":"package upgraded successfully", "success":True,"status":"200"})
                            else:
                                return jsonify({"messege":"package upgrade failed", "success":False,"status":"400"})
                        else:
                            return jsonify({"messege":"package upgrade failed", "success":False,"status":"400"})
                else:
                    return jsonify({"messege":"updation failed", "success":False,"status":"400"})
            else:
                return jsonify({"messege":"This package is not associated with this user", "success":False,"status":"400"})
        else:
            return jsonify({"messege":"User not found or user has no subcription yet", "success":False,"status":"400"})       
@server_blueprint.route('/updatepackage/<string:pakname>',methods=['POST'])
@admin_required()
def updatepackage(pakname):
    chkm=False;chky=False
    current_user_id=get_jwt_identity()
    data=request.get_json()
    userregister_col=db[config.collections[8]]
    package_col=db[config.collections[10]]
    subs_coll=db[config.collections[13]]
    price=data["price"]
    duration=data["duration"]
    noofserver=data["noofserver"]
    newpakname=data["package"]
    accounttype=data["accounttype"]
    subtype=data["typeofsub"]
    descript=data["description"]
    auto_billing=data["auto_billing"]
    tax_percentage=data["tax_percentage"]
    payment_failure_threshold=data["pay_fail_count"]
    setup_fee=data["setup_fee"]
    isactive=data["isactivate"]
    #setup_fee_failure=data["setup_fee_failure"]
    st_time=datetime.now()
    subscribedat=datetime.now()
    end_time=datetime.now()
    if not newpakname or not price or not descript or not subtype or not duration or not auto_billing or not tax_percentage or not setup_fee or not noofserver or not payment_failure_threshold:
        return jsonify({"messege":"either one of field is empty","success":False,"status":"203"})
    else:
        usrptr=userregister_col.find_one({"_id":current_user_id})
        pakobj=package_col.find_one({"package":pakname,"type of package":subtype})
        print(pakobj)
        if usrptr!=None:
            if pakobj!=None:
                #responseplandata = requests.get('https://api-m.sandbox.paypal.com/v1/billing/plans/'+pakobj["planid"], headers=headers)
                #plandata=json.loads(responseplandata)
                #if pakobj["price"]==price and pakobj["duration"]==duration and pakobj["accounttype"]==accounttype and pakobj["description"]==descript and pakobj["type of package"]==subtype and plandata["status"]==isactive and plandata["taxes"]["percentage"]==tax_percentage
                data = [{ "op": "replace", "path": "/description", "value": descript},
                                        { "op": "replace", "path": "/payment_preferences.auto_bill_outstanding", "value": auto_billing}
                                        ,{ "op": "replace", "path": "/name", "value": newpakname},
                                        { "op": "replace", "path": "/taxes.percentage", "value": tax_percentage},
                                        { "op": "replace", "path": "/payment_preferences.payment_failure_threshold", "value": payment_failure_threshold},
                                        { "op": "replace", "path": "/payment_preferences.setup_fee", "value": setup_fee}
                                        #{ "op": "replace", "path": "/payment_preferences.setup_fee_failure_action", "value": setup_fee_failure}
                                        ]
                updatedat=json.dumps(data)
                print(pakobj["planid"])
                response = requests.patch(config.plansurl+'/'+pakobj["planid"], headers=headers, data=updatedat)
                print(response.status_code)
                print(response.content)
                query={"$set":{"package":newpakname,"price":price,"description":descript,"accounttype":accounttype,"duration":duration,"no of server":noofserver,"type of package":subtype,"isactivate":isactive,"createdat":datetime.now()}}
                package_col.update_one({"_id":pakobj["_id"],"package":pakobj["package"]},query)
                return jsonify({"messege":"package updated successfully", "success":True,"status":"200"})
            else:
                return jsonify({"messege":"This package not found", "success":False,"status":"400"})
        else:
            return jsonify({"messege":"Admin user access only", "success":False,"status":"400"})       
@server_blueprint.route('/createpackage',methods=['POST'])
@admin_required()
def createpackage():
    #adminid="1"
    duration=0;accounttype=""; billingcyclelst=[]
    userregister_col=db[config.collections[8]]
    pakage_col=db[config.collections[10]]
    adminuserobj=userregister_col.find_one({"role":"admin"})
    if adminuserobj!=None:
        istrial=request.form["istrial"]
        activepackage=request.form["activepackage"]
        pkname=request.form["packagename"]
        price=request.form["price"]
        #accounttype=request.form["accounttype"]
        noofdevopusrs=request.form["no of devopusrs"]
        noofmonitorusrs=request.form["no of monitorusrs"]
        duration=request.form["duration"]
        des=request.form["description"]
        noofserver=request.form["no of server"]
        typeofpack=request.form["typeofpack"]
        isactive=request.form["activepackage"]
        stepupfee=request.form["stepupfee"]
        tax=request.form["taxpercentage"]
        payment_failure_threshold=request.form["pay_failure_threshold"]
        auto_billing_subscription=request.form["autobillsub"]
        if pkname!="" and des!="" and noofserver!="":
            creatat=datetime.now()
            if istrial: 
                price=""
                accounttype="unpaid"
                if typeofpack=="monthly":
                    duration=30
                if typeofpack=="weekly":
                   duration=7 
                pkobj=pakage_col.find_one({"package":pkname, "type of package": typeofpack})
                if pkobj==None:
                     insert_package(pkname,duration,price, accounttype,des,noofserver,creatat,typeofpack,"",isactive,"",noofdevopusrs,noofmonitorusrs)
                     return jsonify({"messege":"Package Created successfully","success":True,"status":"200"})
                else:
                    return jsonify({"messege":"Package already exist","success":False,"status":"400"})
            else:
                if price!="":
                    accounttype="paid"
                    if typeofpack=="monthly":
                        duration=30
                        typeofplan="MONTH"
                    if typeofpack=="yearly":
                        duration=365
                        typeofplan="YEARLY"
                    pkobj=pakage_col.find_one({"package":pkname, "type of package":typeofpack})
                    if pkobj==None:
                        billingcyclelst=[{ "frequency": { "interval_unit": typeofplan, "interval_count": 1 }, "tenure_type": "REGULAR", "sequence": 1, "pricing_scheme": { "fixed_price": { "value": price, "currency_code": "USD" } } } ] 
                        if activepackage=="active" or activepackage=="Active":
                            isact="ACTIVE"
                        else:
                            isact="INACTIVE"
                        subdata={
                        "product_id": config.prodid,
                        "name": pkname, 
                        "description": des,
                        "status": isact, 
                        "billing_cycles":billingcyclelst 
                        ,"payment_preferences": { "auto_bill_outstanding":  auto_billing_subscription, "setup_fee": { "value": stepupfee, "currency_code": "USD" }, "setup_fee_failure_action": "CONTINUE", "payment_failure_threshold": payment_failure_threshold}, "taxes": { "percentage": tax, "inclusive": False }
                        }
                        dat=json.dumps(subdata)
                        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/plans', headers=headers, data=dat)
                        if response.status_code==201:
                            paypalplandata=json.loads(response.content)
                            planid=paypalplandata["id"]
                            insert_package(pkname,duration,price, accounttype,des,noofserver,creatat,typeofpack,planid,isactive,"",noofdevopusrs,noofmonitorusrs)
                            return jsonify({"messege":"Package Created successfully","success":True,"status":"200"})
                        else:
                            print(response.content)
                            return jsonify({"messege":"Package not created","success":False,"status":response.status_code})
                    else:
                        return jsonify({"messege":"Package already exist","success":False,"status":"400"})
                else:
                    return jsonify({"messege":"Price is empty","success":False,"status":"204"})
        else:
            return jsonify({"messege":"All fields are required","success":False,"status":"204"})
    else:
        return jsonify({"messege":"You dont have rights to access this","success":False,"status":"204"})
@server_blueprint.route('/getpackagebyname/<value>',methods=['GET'])
def getpackagename(value):
    pakage_col=db[config.collections[10]]
    pak_obj=pakage_col.find_one({"package":value})
    if pak_obj!=None:
        pak=json.dumps(pak_obj)
        return jsonify({"Package":pak,"success":True,"status":"200"})
    else:
        return jsonify({"messege":"Package not found","success":False,"status":"404"})
@server_blueprint.route('/getallpackages',methods=['GET'])
def getallpackages():
    paklst=[];lstpakdict=[]
    pakage_col=db[config.collections[10]]
    pakptr=pakage_col.find()
    paklst=list(pakptr)
    if len(paklst)==0:
         return jsonify({"messege":"No package is created yet","success":False,"status":"200"})
    else:
        for pak in paklst:
            pakdat={"Package":pak["package"],"Price":pak["price"],"Description":pak["description"],"Number Of Server":pak["no of server"],"Duration":pak["duration"],"Type Of Package": pak["type of package"],"Plan Type":pak["accounttype"],"Created At": pak["createdat"]}
            lstpakdict.append(pakdat)
        return jsonify({"All Packages":lstpakdict,"success":True,"status":"200"})    

# @server_blueprint.route('/getplandata',methods=['GET'])
# def getplandata():
#     response = requests.get('https://api-m.sandbox.paypal.com/v1/billing/plans/P-5ML4271244454362WXNWU5NQ', headers=headers)

@server_blueprint.route('/deletepackage/<string:value>',methods=['DELETE'])
@jwt_required()
def deletepackage(value):
    userregister_col=db[config.collections[8]]
    pakage_col=db[config.collections[10]]
    currentusr=get_jwt_identity()
    adminuserobj=userregister_col.find_one({"_id":currentusr})
    if adminuserobj!=None:
        if adminuserobj["role"]=="admin":
            pak_obj=pakage_col.find_one({"package":value})
            if pak_obj!="":         
                pakage_col.delete_one({"_id":pak_obj["_id"]})
                return jsonify({"messege":"Package deleted successfully","status":"200"})
            else:
                return jsonify({"messege":"Package not found","status":"401"})
        else:
            return jsonify({"messege":"You dont have rights to access this","success":False,"status":"204"})  
    else:
        return jsonify({"messege":"User not found","success":False,"status":"400"})      

@server_blueprint.route('/cancelsubcription',methods=['GET'])
@jwt_required()
def cancelsubscription():
    userregister_col=db[config.collections[8]]
    pakage_col=db[config.collections[10]]
    subs_coll=db[config.collections[13]]
    current_usr_id=get_jwt_identity()
    userobj=userregister_col.find_one({"_id":current_usr_id})
    subsobj=subs_coll.find_one({"usrid":current_usr_id})
    pakobj=pakage_col.find_one({"package":userobj["package"]})
    if userobj!=None and pakobj!=None and subsobj!=None:
        data = '{ "reason": "Not satisfied with the service" }'
        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions//cancel', headers=headers, data=data)
        if response.status_code==204:
            query={"$set":{"isactive":False,"cancelat":datetime.now()}}
            subs_coll.update_one({"usrid":current_usr_id, "package":userobj["package"]},query)
            return jsonify({"messege":"You canceled your subscription","suucess":True,"status":"200"})
    else:
        return jsonify({"messege":"user not found or this package is not associated with this user","suucess":False,"status":"400"})        

@server_blueprint.route('/usrserverdata',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required() 
def usersvrdata():
    servsstr="";contstr="";chkser=False;chkcont=False
    current_usr_id=get_jwt_identity()
    lstservices=[];lstcontainers=[];lstservers=[];lstsernames=[];lstcontnames=[];lstserip=[];lstsername=[];lstconser=[]
    svr_coll=db[config.collections[11]]
    svervice_and_cont_coll=db[config.collections[12]]
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find({"_id":current_usr_id})
    if usrobj!=None:
        serversptr=svr_coll.find({"owner_id": current_usr_id})
        svrlst=list(serversptr)
        if len(svrlst)==0:
             return jsonify({"messege":"No server associated with this user","success":False,"status":"400"})
        else:
            for serv in svrlst:
                servptr=svervice_and_cont_coll.find({"serip": serv["ip"],"type":"service"})
                contptr=svervice_and_cont_coll.find({"serip": serv["ip"],"type":"container"})
                for service in servptr:
                    #servicedata={"Service":service["name"]}
                    lstservices.append(service["name"])
                for container in contptr:
                    #containerdata={"Container":container["name"]}
                    lstcontainers.append(container["name"])
                # lstservices=list(servptr)
                # lstcontainers=list(contptr)
                #serdict={"Server_id":str(serv["_id"]),"Server_Name":serv["serv_name"],"Services":lstservices,"Containers":lstcontainers}
                serdict={"Server_id":str(serv["_id"]),"Server_IP":serv["ip"],"Server_Name":serv["serv_name"]}
                lstconser.append(serdict)
                lstservices=[]
                lstcontainers=[]
            return jsonify({"User_Servers_Data":lstconser,"success":True,"status":"200"})
    else:
        return jsonify({"messege":"Authentication  error","success":False,"status":"400"})

@server_blueprint.route('/serverdetaildata',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required() 
def serverdetaildata():
    servsstr="";contstr="";chkser=False;chkcont=False
    current_usr_id=get_jwt_identity()
    lstservices=[];lstcontainers=[];lstservers=[];lstsernames=[];lstcontnames=[];lstserip=[];lstsername=[];lstconser=[]
    ip=request.form["ip"]
    svr_coll=db[config.collections[11]]
    svervice_and_cont_coll=db[config.collections[12]]
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find({"_id":current_usr_id})
    if usrobj!=None:
        serversptr=svr_coll.find({"owner_id": current_usr_id,"ip":ip})
        svrlst=list(serversptr)
        if len(svrlst)==0:
             return jsonify({"messege":"No server is present is database","success":False,"status":"400"})
        else:
            for serv in svrlst:
                servptr=svervice_and_cont_coll.find({"serip": serv["ip"],"type":"service"})
                contptr=svervice_and_cont_coll.find({"serip": serv["ip"],"type":"container"})
                for service in servptr:
                    #servicedata={"Service":service["name"]}
                    lstservices.append(service["name"])
                for container in contptr:
                    #containerdata={"Container":container["name"]}
                    lstcontainers.append(container["name"])
                # lstservices=list(servptr)
                # lstcontainers=list(contptr)
                serdict={"Server IP":serv["ip"],"Server Name":serv["serv_name"],"Server Name":serv["serv_name"],"Services":lstservices,"Containers":lstcontainers}
                lstconser.append(serdict)
            return jsonify({"User Servers Data":lstconser,"success":True,"status":"200"})
    else:
        return jsonify({"messege":"Authentication  error","success":False,"status":"400"})
    
    
@server_blueprint.route('/deleteserver',methods=['POST'])
@jwt_required()
def deleteserver():
    current_usrid=get_jwt_identity()
    ip=request.form["ip"]
    svr_coll=db[config.collections[11]]
    svervice_and_cont_coll=db[config.collections[12]]
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find_one({"_id":current_usrid})
    if usrobj["role"]=="devop" or usrobj["role"]=="prodowner" or usrobj["admin"]=="admin":
        if not ip:
            return jsonify({"messege":"invalid ip","success":False,"status":"400"})
        else:
            svrptr=svr_coll.find_one({"ip":ip})
            usrobj=userregister_col.find_one({"_id":current_usrid})
            if usrobj!=None:
                if svrptr!=None:
                    svr_coll.delete_one({"ip":ip})
                    svervice_and_cont_coll.delete_many({"serip":ip})
                    return jsonify({"messege":"server is deleted successfully","success":True,"status":"200"})
                else:
                    return jsonify({"messege":"server not found or this server is not associated with this user","success":False,"status":"400"}) 
            else:
                return jsonify({"messege":"user is not authenicated","success":False,"status":"400"})

@server_blueprint.route('/deleteservice/<string:servicename>',methods=['GET'])
@jwt_required()
def deleteservice(servicename):
    svervice_and_cont_coll=db[config.collections[12]]
    if not servicename:
        return jsonify({"messege":"invalid service name","success":False,"status":"400"})
    else:
        serviceobj=svervice_and_cont_coll.find_one({"name":servicename,"type":"service"})
        if serviceobj!=None:
            svervice_and_cont_coll.delete_one({"name":servicename,"type":"service"})
            return jsonify({"messege":"service is deleted successfully","success":True,"status":"200"})
        else:
            return jsonify({"messege":"service not found","success":False,"status":"400"}) 
@server_blueprint.route('/deletecontainer/<string:containername>',methods=['GET'])
@jwt_required()
def deletecontainer(containername):
    svervice_and_cont_coll=db[config.collections[12]]
    if not containername:
        return jsonify({"messege":"invalid container name","success":False,"status":"400"})
    else:
        serviceobj=svervice_and_cont_coll.find_one({"name":containername,"type":"container"})
        if serviceobj!=None:
            svervice_and_cont_coll.delete_one({"name":containername,"type":"container"})
            return jsonify({"messege":"container is deleted successfully","success":True,"status":"200"})
        else:
            return jsonify({"messege":"container not found","success":False,"status":"400"}) 

@server_blueprint.route('/updateserviceandcontainer/<string:ip>',methods=['PUT'])
@jwt_required()
def updateserviceorcontainer(ip):
    lstservice=[];existservice=[];existcontainer=[];chkser=False;chkcont=False;ismodified_file=False
    current_usrid=get_jwt_identity()
    data=request.get_json()
    services=data['service']
    containers=data['container']
    svervice_and_cont_coll=db[config.collections[12]]
    svr_coll=db[config.collections[11]]
    svrobj=svr_coll.find_one({"ip":ip})
    userregister_col=db[config.collections[8]]
    print(services)
    print(containers)
    usrobj=userregister_col.find_one({"_id":current_usrid})
    if usrobj!=None:
        if usrobj["role"]=="admin":
            if len(services)==0 and len(containers)==0:
                return jsonify({"messege":"services and containers is empty","success":False,"status":"400"})
            else:
                serviceptr=svervice_and_cont_coll.find({"serip":ip,"type":"service"})
                contptr=svervice_and_cont_coll.find({"serip":ip,"type":"container"})
                lstservice=list(serviceptr)
                lstcontainer=list(contptr)
                if len(lstservice)==0:
                    chkser=False
                else:
                    for service in services:
                        if service not in lstservice:
                            insert_service_and_container(ip,service,"service")
                            chkser=True
                        else:    
                            existservice.append(service) 
                if len(lstcontainer)==0:
                    chkcont=False
                else:    
                    for cont in containers:
                        if cont not in lstcontainer:
                            insert_service_and_container(ip,cont,"container")
                            chkcont=True
                        else:
                            existcontainer.append(cont)
                if chkser==True or chkcont==True:
                    if svrobj!=None:
                        ismodified_file=write_server_detail_to_bashscript(ip,current_usrid,svrobj["serv_name"],services,containers,config.svrdownurl)
                        if ismodified_file:
                            return jsonify({"messege":"Server Data updated successfully","service updated":chkser,"container updated":chkcont,"success":True,"status":"200"})
                else:
                    return jsonify({"messege":"services or conatiners are empty","service updated":chkser,"container updated":chkcont,"success":False,"status":"400"})
        if usrobj["role"]=="devop":   
            if len(services)==0 and len(containers)==0:
                return jsonify({"messege":"services and containers is empty","success":False,"status":"400"})
            else:
                serviceptr=svervice_and_cont_coll.find({"serip":ip,"type":"service"})
                contptr=svervice_and_cont_coll.find({"serip":ip,"type":"container"})
                lstservice=list(serviceptr)
                lstcontainer=list(contptr)
                if len(lstservice)==0:
                    chkser=False
                else:
                    for service in services:
                        if service not in lstservice:
                            insert_service_and_container(ip,service,"service")
                            chkser=True
                        else:    
                            existservice.append(service) 
                if len(lstcontainer)==0:
                    chkcont=False
                else:    
                    for cont in containers:
                        if cont not in lstcontainer:
                            insert_service_and_container(ip,cont,"container")
                            chkcont=True
                        else:
                            existcontainer.append(cont)
                if chkser==True or chkcont==True:
                    if svrobj!=None:
                        ismodified_file=write_server_detail_to_bashscript(ip,current_usrid,svrobj["serv_name"],services,containers,config.svrdownurl)
                        if ismodified_file:
                            return jsonify({"messege":"Server Data updated successfully","service updated":chkser,"container updated":chkcont,"success":True,"status":"200"})
                else:
                    return jsonify({"messege":"services or conatiners are empty","service updated":chkser,"container updated":chkcont,"success":False,"status":"400"})
        if usrobj["role"]=="prodowner":
            if len(services)==0 and len(containers)==0:
                return jsonify({"messege":"services and containers is empty","success":False,"status":"400"})
            else:
                serviceptr=svervice_and_cont_coll.find({"serip":ip,"type":"service"})
                contptr=svervice_and_cont_coll.find({"serip":ip,"type":"container"})
                lstservice=list(serviceptr)
                lstcontainer=list(contptr)
                if len(lstservice)==0:
                    chkser=False
                else:
                    for service in services:
                        if service not in lstservice:
                            insert_service_and_container(ip,service,"service")
                            chkser=True
                        else:    
                            existservice.append(service) 
                if len(lstcontainer)==0:
                    chkcont=False
                else:    
                    for cont in containers:
                        if cont not in lstcontainer:
                            insert_service_and_container(ip,cont,"container")
                            chkcont=True
                        else:
                            existcontainer.append(cont)
                if chkser==True or chkcont==True:
                    if svrobj!=None:
                        ismodified_file=write_server_detail_to_bashscript(ip,current_usrid,svrobj["serv_name"],services,containers,config.svrdownurl)
                        if ismodified_file:
                            return jsonify({"messege":"Server Data updated successfully","service updated":chkser,"container updated":chkcont,"success":True,"status":"200"})
                else:
                    return jsonify({"messege":"services or conatiners are empty","service updated":chkser,"container updated":chkcont,"success":False,"status":"400"})
        
        else:
            return jsonify({"messege":"User have no access rights","success":False,"status":"400"})
    else:
        return jsonify({"messege":"User not found","success":False,"status":"404"})
@server_blueprint.route('/suspenduser/<string:email>',methods=['GET','POST'])
@admin_required()
def suspenduser(email):
    data=request.get_json()
    suspendedval=data['issuspended']
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find_one({"email":email})
    if usrobj==None:
        return jsonify({"messege":"User not found","success":False,"status":"400"})
    else:
        if not suspendedval:
            return jsonify({"messege":"suspended field value is not selected","success":False,"status":"400"})
        else:
            query={"$set":{"suspended":suspendedval,"authenticated":False}}
            userregister_col.update_one({"email":email},query)
            return jsonify({"messege":"This user is suspended contact administrator","success":True,"status":"200"})

@server_blueprint.route('/resetpasswordlink', methods=['POST'])
def resetpasswordlink():
    data=request.get_json()
    email=data['email']
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find_one({"email":email})
    if usrobj!=None:
        token=s.dumps({"userid":usrobj["_id"]},salt='reset-password')
        url='http://127.0.0.1:5000/resetpassword/{}'.format(token)
        subject = f'Email Verification'
        body = f'email verification {url}'
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)

        message = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(sender_email, [email], message)  # updated line

        smtp.quit()
        return jsonify({"messege":"Password reset eamil link is sent successfully","success":True,"status":"200"})
    else:
        return jsonify({"messege":"User not found","success":False,"status":"400"})

@server_blueprint.route('/resetpassword/<token>',methods=['GET','POST'])
def resetpassword(token):
    userregister_col=db[config.collections[8]]
    try:
        usrid=s.loads(token,salt='reset-password',max_age=3600)
        usrobj=userregister_col.find_one({"_id":str(usrid["userid"])})
        print(usrobj)
        if usrobj==None:
            return jsonify({"messege":"User not found","success":False,"status":"400"})
        else:
            data=request.get_json()
            password=data['password']
            confirmpassword=data['confirmpassword']
            if not password or not confirmpassword:
                return jsonify({"messege":"Either one of field is empty","success":False,"status":"400"})
            else:
                if confirmpassword==password:
                    passwordbyte=password.encode()
                    hashedpassword=hashlib.sha256(passwordbyte)
                    passwordhash=hashedpassword.hexdigest()
                    print(password)
                    if usrobj["password"]==passwordhash:
                        return jsonify({"messege":"your password is same as before add different password","success":False,"status":"400"})
                    else:
                        query={"$set":{"password":passwordhash}}
                        userregister_col.update_one({"_id":usrid["userid"]},query)
                        return jsonify({"messege":"your password is changed successfully","success":True,"status":"200"})
                else:
                    return jsonify({"messege":"Password not matched","success":False,"status":"403"})
    except SignatureExpired as e:
        return jsonify({"messege":e,"success":False,"status":"400"})
    except BadSignature as e:
        return jsonify({"messege":e,"success":False,"status":"400"})

@server_blueprint.route('/activateplan', methods=['POST'])
@admin_required()
def planactivison():
    activateval=request.form['activate']
    pakname=request.form['pakagename']
    typeofsub=request.form['typeofpackage']
    pakage_col=db[config.collections[10]]
    pakobj=pakage_col.find_one({"package":pakname,"type of package":typeofsub})
    if pakobj!=None:
        if activateval:
            response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/plans/'+pakobj["planid"]+'/activate', headers=headers)
            if response.status_code==204:
                return jsonify({"messege":"plan activated","success":True,"status":"200"})    
        else:
            response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/plans/'+pakobj["planid"]+'/deactivate', headers=headers)
            if response.status_code==204:
                return jsonify({"messege":"plan deactivated","success":True,"status":"200"})
        
@server_blueprint.route('/getallservers',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getallserversdata():
    try:
        svrlst=[]
        svr_coll=db[config.collections[11]]
        svrptr=svr_coll.find()
        svrlst=list(svrptr)
        if len(svrlst)==0:
            return jsonify({"messege":"No server is added yet","status":"200"})
        else:
            return jsonify({"List all servers associated with this user are":svrlst,"status":"200","success":True})  
    except Exception as e:
        return jsonify({"message":e,"status":"500"})
@server_blueprint.route('/getallusers',methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getallusers():
    try:
        usrlst=[]
        userregister_col=db[config.collections[8]]
        usrptr=userregister_col.find()
        usrlst=list(usrptr)
        if len(usrlst)==0:
            return jsonify({"messege":"No user is created yet","status":"200"})
        else:
            return jsonify({"Users":usrlst,"status":"200","success":True})  
    except Exception as e:
        return jsonify({"message":"error","status":"500"})  


@server_blueprint.route('/updateuserdata',methods=['PUT'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@jwt_required()
def updateuserdata():
    current_id=get_jwt_identity()
    userregister_col=db[config.collections[8]]
    usrobj=userregister_col.find_one({"_id":current_id})
    if usrobj!=None:
        username=request.form["username"]
        email=request.form["email"]
        query={"username":username,"email":email}
        userregister_col.update_one({"_id":current_id},query)
        return jsonify({"messege":"user data updated successfully","success":True,"status":"200"})
    else:
        return jsonify({"messege":"user not found","success":False,"status":"404"})

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header,jwt_payload: dict):
    jti = jwt_payload["jti"]
    return jti in blocklist

@server_blueprint.route('/logoutusr',methods=['DELETE'])
@jwt_required()
def logout():
    jwtrevokedtoken_coll=db[config.collections[15]]
    jti=get_jwt()["jti"]
    blocklist.add(jti)
    #jwtrevokedtoken_coll.insert_one({"jwtrevoked":jti})
    return jsonify({"messege":"User logout successfully","success":True,"status":"200"})
def float_value(cpu_value):
    ram_val=""
    for i in cpu_value:
        if i=="%":
            h=0
        else:
            ram_val+=i
    return float(ram_val)   
def lastdownsercont(col):
    l_ptr=col.find()
    l_lst=list(l_ptr)
    last_doc=l_lst[-1]
    return last_doc
def lsttoken(lst):
    cpylst="";cont=0
    for i in lst:
        if i==",":
            cpylst+="\n"
            cont=cont+1
        else:
            cpylst+=i
    return cpylst
def counttoken(lst):
    cont1=0
    for i in lst:
        if i==",":
            cont1=cont1+1
        else:
            x=0
    return cont1       
def maxcounthist(col):    
    time_n=datetime.now()
    fixthreshold=time_n-timedelta(days=1)
    col.delete_many({"time":{"$lt":fixthreshold}})
def linetoken(line):
    con=0
    for k in line:
        if k==" ":
            con=con+1
    return con
def lastarguetoken(linetxt):
    containlst=""
    lindex=len(linetxt)-1
    vallast=linetxt[lindex]
    for h in vallast:
        if h=='\n':
            containlst+=","
        else:
            containlst+=h
    return containlst            
