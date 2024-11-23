def matching(mycol,str_email,str_password):
    sucess=False;usrid=""
    pipeline=[{"$match":{"$and":[{"email":str_email},{"password":str_password}]}}]
    mat_usr=mycol.aggregate(pipeline)
    lst_usr=list(mat_usr)
    if len(lst_usr)==0:
        print("Email or Password does not exist !")
        sucess=False
        return "","",sucess,"" 
    else:
        pak_value=lst_usr[0]["package"]
        pak_type=lst_usr[0]["ptype"]
        usrid=lst_usr[0]["_id"]
        sucess=True
        return pak_value,pak_type,sucess,usrid 
    
def Login(usr_col,usr_email,usr_password):
    pktype="";pkvalue="";usr_id="";chkulog=False
    pkvalue,pktype,chkulog,usr_id=matching(usr_col,usr_email,usr_password)
    return chkulog,pktype,pkvalue,usr_id