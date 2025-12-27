### 🚀 Project Showcase: Azure Server Health Monitoring using Ansible + Django + NGINX

I built a Server Health Check Monitoring system to centrally monitor Azure-based servers using an agentless and scalable approach.

🔧 Tech Stack

Ansible – Agentless health data collection

Django – Backend logic & dashboard rendering

NGINX – Reverse proxy & web server

Azure VMs – Infrastructure layer

### 📊 What it does

Collects CPU, Memory, and Disk utilization from multiple Azure servers

Displays real-time health status in a clean web dashboard

Uses threshold-based checks to mark disk health as OK / Warning / Critical

Eliminates the need to log in to individual servers

### 📌 Why this project
As a Linux administrator, I wanted a lightweight, customizable monitoring solution without relying on third-party tools. This project helped me strengthen my skills in automation, backend development, and infrastructure monitoring.

### Key Benefits

* **Agentless monitoring** using Ansible
* **Centralized visibility** of Azure server health
* **Web-based dashboard** built with Django
* **Scalable** – easily add more Azure servers
* **Customizable** health checks based on requirements

---

### Use Case

This system is useful for **Linux administrators and DevOps engineers** who want a lightweight, customizable monitoring solution for Azure-hosted servers without relying on third-party monitoring tools.

---------------------------------------------------------------------------------------------------
### Prerequites:
Copy the repo in user "ansible" home directory
All M's should have python3.x, ansible, django, nginx , sysstat installed
Run "python3 manage.py collectstatic"
Create below mentioned custom services
Edit NGINX coniguration with below
Disable selinux
Give "o+rx" permission to /home, /home/ansible and all insie /home/ansible/HealthCheck for NGINX to work
----------------------------------------------------------------------------------------------------

Using Ansible Colletng data -
Play book :-

        [root@monitorsrv ~]# cat /home/ansible/HealthCheck/dataGather.yml 
        ---
        - name : Monitor
          hosts : all
          become : true
          vars :
            OutFile : /home/ansible/HealthCheck/Monitor_data.txt
          tasks :
            - name : Cler Output file
              delegate_to : localhost
              copy :
                content : ""
                dest : "{{OutFile}}"
        
        - name : Cpu Data
          shell : sar 1 3 | tail -1 | awk '{print 100-$NF}'
          register : cpu_usage
        
        - name : Memory Data
          shell : free -m | awk 'NR == 2 {print $3/$2*100}'
          register : mem_usage
    
        - name : Read FS Mon File
          set_fact :
            fs_mon : "{{lookup('file','/home/ansible/HealthCheck/fs.mon').splitlines()}}"
    
        - name : Disk Data
          shell : for fs in {{fs_mon | join(' ')}} ; do df -h ${fs} 2>/dev/null | tr -d "%" | awk 'NR>1{print $(NF) "-" $(NF-1)}' ; done | tr "\n" ";"
          register : disk_usage
    
        - name : Save Data
          delegate_to: localhost
          lineinfile :
            path : "{{OutFile}}"
            line : "{{inventory_hostname}},{{cpu_usage.stdout}},{{mem_usage.stdout}},{{disk_usage.stdout}}"
    ...

Custom Service that will run the playboot after each 2 minutes:-

        [root@monitorsrv ~]# cat /etc/systemd/system/datacollection.service 
        [Unit]
        Description=Data Collection
        After=network.target
        
        [Service]
        Type=simple
        WorkingDirectory=/home/ansible/HealthCheck/
        ExecStart=/bin/bash -c "while true;do ansible-playbook dataGather.yml;sleep 120;done"
        User=ansible
        Restart=always
        
        [Install]
        WantedBy=multi-user.target

Custom Servie for Django to run -

    [root@monitorsrv ~]# cat /etc/systemd/system/healthmonitor.service 
      [Unit]
      Description=healthmonitor
      After=network.target
      
      [Service]
      Type=simple
      WorkingDirectory=/home/ansible/HealthCheck/monitor/
      ExecStart=/usr/bin/python3 manage.py runserver
      Restart=always
      RestartSec=10
      User=ansible
      
      [Install]
      WantedBy=multi-user.target

Configuration DOne on NGINX -

    server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  _;

        include /etc/nginx/default.d/*.conf;

        location / {
            proxy_pass http://localhost:8000;
        }

        location /static/ {
            alias /home/ansible/HealthCheck/monitor/static/;
        }

        error_page 404 /404.html;
            location = /40x.html {
        }

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {
        }
    }

Finally the wHealhCeck is visible in web using NGINX http://<server IP>

<img width="1353" height="390" alt="image" src="https://github.com/user-attachments/assets/efa3adec-8d25-4b69-a89d-cdaae7a2c734" />


