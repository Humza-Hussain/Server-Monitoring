def write_server_detail_to_bashscript(svip,userid,servername,services,containers,url):
    serstr="";contstr="";ismodified=False
    for k in services:
        serstr+=f'"{k}"'+" "
    for k in containers:
        contstr+=f'"{k}"'+" "
    fpr =open('./servermonitorbashscript.sh','r')
    lst_bach_script_data=fpr.readlines()
    writedata=""
    for j in range(len(lst_bach_script_data)-1):
        if lst_bach_script_data[j]=="svip="+f'""'+"\n":
            lst_bach_script_data[j]="svip="+f'"{svip}"'+"\n"
            ismodified=True
        if lst_bach_script_data[j]=="endpoint="+f'""'+"\n":
            lst_bach_script_data[j]="endpoint="+f'"{url}"'+"\n"
            ismodified=True
        if lst_bach_script_data[j]=="owner_id="+f'""'+"\n":
            lst_bach_script_data[j]="owner_id="+f'"{userid}"'+"\n"
            ismodified=True
        if lst_bach_script_data[j]=="servername="+f'""'+"\n":
            lst_bach_script_data[j]="servername="+f'"{servername}"'+"\n"
            ismodified=True
        if lst_bach_script_data[j]=="services=()\n":
            lst_bach_script_data[j]="services=("+serstr+")\n"
            ismodified=True
        if lst_bach_script_data[j]=="containers=()\n":
            lst_bach_script_data[j]="containers=("+contstr+")\n"
            ismodified=True
    fpr.close()
    fpw=open('./servermonitorcreatedscript.sh','w')
    if ismodified:  
        for m in lst_bach_script_data:
            writedata+=m 
            ismodified=True 
        fpw.write(writedata)
        fpw.close()
    return ismodified
