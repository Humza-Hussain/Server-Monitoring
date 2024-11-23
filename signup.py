def Register(coll,uid,usrname,password,email,isadmin,isconfirmed,time_n,package,typ,secret_key,code,isauthenticated,issuspended,poid,noofdevop,noofmonitorusr,alloweddevopusrtoselpak):
    chk=False;iscreated=False
    if usrname=="":
        return chk
    else:
        if email=="":
            return chk
        else:
            chk=True
    if chk==True:
        usr_dat={"_id":str(uid),"username":usrname,"email":email,"password":password,"role":isadmin,"confirmed":isconfirmed,"authenticated":isauthenticated,"suspended":issuspended,"createdon":time_n,"secret_key":secret_key,"code":code,"package":package,"ptype":typ,"poid":poid,"no of deveopusrs":noofdevop,"no of monitorusrs":noofmonitorusr,"alloweddeveopusrtoselpak":alloweddevopusrtoselpak}    
        val=email
        key_em="email"
        email_obj=coll.find_one({key_em:val})
        if email_obj==None:
            coll.insert_one(usr_dat)
            iscreated=True
            print("Account is created")
        else:
            iscreated=False
            print("Account is already created!")
    return iscreated