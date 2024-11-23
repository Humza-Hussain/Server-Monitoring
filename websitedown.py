from datetime import datetime
def websitedownlog(website_col,websitehist_col,weburllst,ip,urlstatus):
    con=0;weblst=[];allwebsitename=[];check=False
    con=counttoken(weburllst)
    lsturl=weburllst.split(",",con)
    time_n=datetime.now()
    for k in range(len(lsturl)-1):
        weblst.append(lsturl[k])
    ptr=website_col.find()
    if ptr==None:
        for w in range(len(lsturl)-1):
            website_col.insert_one({"usr_id":ip,"url":lsturl[w],"status":urlstatus,"old_time":time_n,"new_time":time_n})
            websitehist_col.insert_one({"usr_id":ip,"url":val,"status":urlstatus,"time":time_n})
        check=True
    else:
        ptrlst=website_col.find({"usr_id":ip})
        existlstusrl=list(ptrlst)
        if len(existlstusrl)==0:
            for i in range(len(lsturl)-1):
                website_col.insert_one({"usr_id":ip,"url":lsturl[i],"status":urlstatus,"old_time":time_n,"new_time":time_n})
                websitehist_col.insert_one({"usr_id":ip,"url":lsturl[i],"status":urlstatus,"time":time_n})
            check=True
        else:
            for webobj in existlstusrl:
                allwebsitename.append(webobj["url"])
            for val in weblst:
                if val in allwebsitename:
                    t_now=datetime.now()
                    query={"$set":{"new_time":t_now}}
                    website_col.update_one({"usr_id":ip,"url":val},query)
                    websitehist_col.insert_one({"usr_id":ip,"url":val,"status":urlstatus,"time":time_n})
                else:
                    website_col.insert_one({"usr_id":ip,"url":val,"status":urlstatus,"old_time":time_n,"new_time":time_n})
                    websitehist_col.insert_one({"usr_id":ip,"url":val,"status":urlstatus,"time":time_n})
                check=True
    urllst=uplstdata(website_col,ip,weblst)
    up_urllst=list(urllst[0])            
    if up_urllst==weblst:
        print("all services are down")
        check=True
    else:
        for upurl in up_urllst:
            websitehist_col.insert_one({"usr_id":ip,"url":upurl,"status":200,"time":time_n})
    return check 
def uplstdata(coll,ip,dserv_lst):
    reslst=[];namelst=[]
    ptr=coll.find({"usr_id":ip})
    datalst=list(ptr)
    for i in range(len(datalst)):
        namelst.append(datalst[i]["url"])
    finaluplst=uncommon_data(namelst,dserv_lst,reslst)
    return list(finaluplst)            
def uncommon_data(a, b,reslst):
    a_set = set(a)
    b_set = set(b)
    reslst.append(a_set-b_set)
    return reslst   
def counttoken(lst):
    lst_services="";cont1=0
    for i in lst:
        if i==",":
            cont1=cont1+1
        else:
            x=0
    return cont1
