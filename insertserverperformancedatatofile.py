def write_server_performance_to_bashscript(svip,servername,url):
    ismod=False
    fpr =open('./serverperformancebashscript.sh','r')
    lst_bach_script_data=fpr.readlines()
    writedata=""
    for j in range(len(lst_bach_script_data)-1):
        if lst_bach_script_data[j]=="svip="+f'""'+"\n":
            lst_bach_script_data[j]="svip="+f'"{svip}"'+"\n"
            ismod=True
        if lst_bach_script_data[j]=="endpoint="+f'""'+"\n":
            lst_bach_script_data[j]="endpoint="+f'"{url}"'+"\n"
            ismodified=True
        if lst_bach_script_data[j]=="servername="+f'""'+"\n":
            lst_bach_script_data[j]="servername="+f'"{servername}"'+"\n"
            ismod=True
    fpr.close()
    fpw=open('./serverperformancecreatedscript.sh','w')
    if ismod:  
        for m in lst_bach_script_data:
            writedata+=m 
            ismod=True 
        fpw.write(writedata)
        fpw.close()
    return ismod