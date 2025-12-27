from django.shortcuts import render

def Dashboard(req):
    f=open("/home/ansible/HealthCheck/Monitor_data.txt","r")
    data = {}
    
    count = 1
    for i in f:
        d = i.strip().split(",")
        threshold = 50

        if float(d[1]) >threshold:
            cpu_color="red"
        else:
            cpu_color="green"

        if float(d[2]) > threshold:
            mem_color="red"
        else:
            mem_color="green"

        dsk = d[3].strip().split(";")
        flag = 1
        dsk_status = []
        for ds in dsk:
            fs=ds.split("-")
            print(f"FS = {fs} , Legth = {len(fs)}")
            if len(fs) >1 and float(fs[1]) > threshold:
                dsk_status.append(fs[0] + " : " + fs[1] + " %")
                flag = 0
            

        if flag == 0:
            dsk_color = "red"
            ds_status = ' ; '.join(dsk_status)
        else:
            dsk_color = "green"
            ds_status = "OK"

        data[count]={
        "Host" : d[0],
        "CPU" : {
            "color": cpu_color,
            "status" : d[1]
            },
        "Memory" : {
            "color": mem_color,
            "status" : d[2]
            },
        "Disk" : {
                "color" : dsk_color,
                "status" : ds_status,
            },
        }
        print(data)
        

        count += 1
    return render(req,"dashboard.html",{"DATA":data})
