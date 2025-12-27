# HealthCheck
This will gather health data from servers using ansible and shown in web using django

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


