import config
from server import  insert_server
from servicessandcontainers import insert_service_and_container
def add_server_and_service_and_cont(services,containers,svip,svername,usrid,svr_coll,sverviceandcont_coll):    
    serchk=False;conchk=False
    ptr=svr_coll.find()
    ptrserandcont=sverviceandcont_coll.find()
    sersandcontslst=list(ptrserandcont)
    svrlst=list(ptr)
    if len(svrlst)==0:
        if len(sersandcontslst)==0:
            insert_server(usrid,svip,svername)
            if len(services)==0:
                serchk=True
            else:                
                for serv in services:
                    insert_service_and_container(svip,serv,"service")
                    serchk=False
            if len(containers)==0:
                conchk=True
            else:
                for cont in containers:
                    insert_service_and_container(svip,cont,"container")
                    conchk=False
            return {"messege":"Server added","Container added": conchk,"Service added":serchk,"success":True,"status":"200"}
    else:
        svrobj=svr_coll.find_one({"owner_id":usrid,"ip":svip})
        if svrobj==None:
            insert_server(usrid,svip,svername)
            if len(services)!=0:
                for serv in services:
                    insert_service_and_container(svip,serv,"service")
                    serchk=True
            else:
                serchk=False
            if len(containers)!=0:
                for cont in containers:
                    insert_service_and_container(svip,cont,"container")
                    conchk=True
            else:
                conchk=False
            return {"messege":"Server added","Container added": conchk,"Service added":serchk,"success":True,"status":"200"}
        else:
            return {"messege":"Server already added","success":False,"status":"400"}