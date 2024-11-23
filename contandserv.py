from services import insert_service
from container import insert_container
from datetime import datetime,timedelta
from history import makehist
from contandservstatusup import insert_upstatus
import config
import pymongo
def contandserv(ip,servername,service_col,container_col,status,service_lst,contstat,cont_lst):
    Client=pymongo.MongoClient(config.connectstring)
    db=Client[config.database]
    hist_coll=db[config.collections[2]]
    upduration_col=db[config.collections[7]]
    t_now=datetime.now()
    if service_lst!="":
        success_ser=Services(ip,servername,status,service_lst,service_col,hist_coll,upduration_col)
        success_ser=True
    else:
        success_ser=False
        upstatus="up"
        type_s="service"
        ptrser=service_col.find({"serip":ip})
        for obj in ptrser:
            insert_upstatus(ip,servername,obj["servicesname"],upstatus,t_now,type_s)
    if cont_lst!="":
        success_cont=True
        success_cont=Containers(ip,servername,contstat,cont_lst,container_col)
    else:
        upstatus="up"
        type_c="container"
        ptrcon=container_col.find({"serip":ip})
        for obj in ptrcon:
            insert_upstatus(ip,servername,obj["containername"],upstatus,t_now,type_c) 
        success_cont=False
    return success_ser,success_cont   
def Services(ip,servername,status,servicelst,service_col,hist_col,updur_col):
    cont=0;dservice_lst=[];lst_services="";chk=False;namelst=[]
    t_n=datetime.now()
    cpy_servicelst=servicelst
    for i in servicelst:
        if i==",":
            lst_services+="\n"
            cont=cont+1
        else:
            lst_services+=i
    svr=cpy_servicelst.split(",",cont)
    for i in range(len(svr)-1):
        dservice_lst.append(svr[i])
    ser_col_ptr=service_col.find()
    length_serv=len(list(ser_col_ptr))
    if length_serv==0:
        oldt_n=t_n
        newt_n=t_n
        for i in range(len(svr)-1):
            insert_service(ip,servername,svr[i],status,oldt_n,newt_n)
            makehist(ip,servername,svr[i],"down",t_n,"","service")
        chk=True
    else:
        ptr=service_col.find({"serip":ip})
        nalst=list(ptr)
        if len(nalst)==0:
            oldt_n=t_n
            newt_n=t_n
            for i in range(len(svr)-1):
                insert_service(ip,servername,svr[i],status,oldt_n,newt_n)
                makehist(ip,servername,svr[i],"down",t_n,"","service")
            chk=True
        else:
            for serobj in nalst:
                namelst.append(serobj["servicesname"])
            for nameser in dservice_lst:              
                if nameser not in namelst:
                    oldt_n=t_n
                    newt_n=t_n
                    insert_service(ip,servername,nameser,status,oldt_n,newt_n)
                    makehist(ip,servername,nameser,"down",t_n,"","service")
                else:
                    newt_n=t_n
                    query={"$set":{"new_time":newt_n}}
                    service_col.update_one({"serip":ip,"servicesname":nameser},query)
                    makehist(ip,servername,nameser,"down",t_n,"","service") 
                chk=True
    indval="servicesname"
    servlst=uplstdata(service_col,ip,dservice_lst,indval)
    up_lst=list(servlst[0])  
    if up_lst==nalst:
        print("all services are down")
    else:
        for servname in up_lst:
            insert_upstatus(ip,servername,servname,"service",t_n,"up")
            #makehist(ip,servername,servname,"up",t_n,"service")
    return chk      
        # if up_lst==nalst:
        #     print("all services are down")
        # else:
        #     for upser in up_lst:
        #         #makehist(ip,servername,upser,"up",t_n,"service")
        #         ptr=hist_col.find({"serip":ip,"type":"service","name":upser}).sort("downtime",1)
        #         lstsort=list(ptr)
        #         lind=len(lstsort)
        #         lastdown=lstsort[lind-1]
        #         #print(lastdown)
        #         #print(lastdown["type"])
        #         if lastdown["uptime"]=="":
        #             query={"$set":{"uptime":t_n}}
        #             hist_col.update_one({"serip":lastdown["serip"],"type":lastdown["type"],"name":upser,"downtime":lastdown["downtime"]},query)
        #         insert_upstatus(ip,servername,upser,"service",t_n)
    #downtimecalculation(hist_col,updur_col)
def uplstdata(coll,ip,dserv_lst,opt=None):
    reslst=[];namelst=[]
    ptr=coll.find({"serip":ip})
    datalst=list(ptr)
    for i in range(len(datalst)):
        namelst.append(datalst[i][opt])
    finaluplst=uncommon_data(namelst,dserv_lst,reslst)
    return list(finaluplst)               
def uncommon_data(a, b,reslst):
    a_set = set(a)
    b_set = set(b)
    reslst.append(a_set-b_set)
    return reslst                   
def Containers(ip,servername,contstat,cont_lst,container_col):
    h=0;cpy_containerslst=[];chk_c=False;lst_containers="";contnamlst=[]
    t_n=datetime.now()
    for i in cont_lst:
        if i==",":
            lst_containers+="\n"
            h=h+1
        else:
            lst_containers+=i
    conts_lst=cont_lst.split(",",h)
    for i in range(len(conts_lst)-1):
        cpy_containerslst.append(conts_lst[i])
    container_col_ptr=container_col.find()
    len_container=len(list(container_col_ptr))
    if len_container==0:
        oldt_n=t_n
        newt_n=t_n
        for i in range(len(conts_lst)-1):
            insert_container(ip,servername,conts_lst[i],contstat,oldt_n,newt_n)
            makehist(ip,servername,conts_lst[i],"down",t_n,"","container")
        chk_c=True
    else:
        ptr=container_col.find({"serip":ip})
        nalst=list(ptr)
        if len(nalst)==0:
            oldt_n=t_n
            newt_n=t_n
            for i in range(len(conts_lst)-1):
                insert_container(ip,servername,conts_lst[i],contstat,oldt_n,newt_n)
                makehist(ip,servername,conts_lst[i],"down",t_n,"","container")
            chk_c=True
        else:
            for contobj in nalst:
                contnamlst.append(contobj["containername"])
            for namecont in cpy_containerslst:              
                if namecont not in contnamlst:
                    oldt_n=t_n
                    newt_n=t_n
                    insert_container(ip,servername,namecont,contstat,oldt_n,newt_n)
                    makehist(ip,servername,namecont,"down",t_n,"","container")
                else:
                    newt_n=t_n
                    query={"$set":{"new_time":newt_n}}
                    container_col.update_one({"serip":ip,"containername":namecont},query)
                    makehist(ip,servername,namecont,"down",t_n,"","container")
                chk_c=True
    indval="containername"
    histlst=uplstdata(container_col,ip,cpy_containerslst,indval)
    up_lst=list(histlst[0])
    if up_lst==contnamlst:
        print("all containers are down")
    else:
        for contname in up_lst:
            #makehist(ip,servername,contname,"up",t_n,"container")
            insert_upstatus(ip,servername,contname,"container",t_n,"up")
    return chk_c
def downtimecalculation(col,updur_col):
    name="redit"
    opt="service"
    td=timedelta(seconds=1800)
    n=datetime.now()
    fixthreshold=n-td
    totdowntime=[];totdtime=0;downtimelst=[];hours=0;minutes=0
    ptr=col.find({"name":name,"type":opt})
    lsthist=list(ptr)
    if len(lsthist)==1:
         downtime=""
    else:
        for k in range(len(lsthist)-1):
            dur=lsthist[k+1]["downtime"]-lsthist[k]["downtime"]
            if dur>td:
                hours, minutes = dur.seconds // 3600, dur.seconds // 60 % 60
                upval=datetime(lsthist[k]["downtime"].year,lsthist[k]["downtime"].month,lsthist[k]["downtime"].day,hours,minutes,0)
                updur_col.insert_one({"name":lsthist[k]["name"],"type":lsthist[k]["type"],"uptime":upval})
            else:
                dval=datetime(lsthist[k]["downtime"].year,lsthist[k]["downtime"].month,lsthist[k]["downtime"].day,hours,minutes,0)
                query={"$set":{"downtime":dval}}
                col.update_one({"serip":lsthist[k+1]["serip"],"type":lsthist[k+1]["type"],"name":lsthist[k+1]["name"],"downtime":lsthist[k+1]["downtime"]},query)
                #downtimelst.append(dur)
                
    
      
# def downtimecalcution(col):
#     name="redit"
#     opt="service"
#     td=timedelta(days=1)
#     n=datetime.now()
#     fixthreshold=n-td
#     totdowntime=[];totdtime=0;downtimelst=[]
#     ptr=col.find({"name":name,"type":opt})
#     lsthist=list(ptr)
#     for k in range(len(lsthist)-1):
#         if lsthist[k]["downtime"]:
#             if lsthist[k]["uptime"]=="":
#                 downtimelst.append(lsthist[k]["downtime"])
#             else:
#                 downtimecal=lsthist[k]["uptime"]-lsthist[k]["downtime"]
#                 #hours, minutes = downtimecal.seconds // 3600, downtimecal.seconds // 60 % 60
#                 #downdate=datetime(histobj["uptime"].year,histobj["uptime"].month,histobj["uptime"].day,hours,minutes,0)
#                 totdowntime.append(downtimecal)
#     for l in range(len(downtimelst)-1):
#        dowtime=downtimelst[l+1]-downtimelst[l]
#        totdowntime.append(dowtime)
#        print(dowtime)
    # for obj in totdowntime:
    #     hours, minutes = obj.seconds // 3600, obj.seconds // 60 % 60
        #print(hours)
        #print(minutes) 
    #print(downtimelst)
    #print(totdowntime)
    # totdtime=sum(totdowntime,timedelta(0,0))
    # print(totdtime)