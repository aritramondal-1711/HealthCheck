### Project Overview: Server Health Monitoring Using Ansible and Django

This project is designed to **collect health and status information from servers hosted in Microsoft Azure** and **display the collected data through a web application built with Django**.

The solution uses **Ansible** for automation and data collection, and **Django** as the backend framework to present the information in a user-friendly web interface.

---

### How the System Works

1. **Azure Servers**

   * Multiple virtual machines are running in **Microsoft Azure**.
   * These servers are configured to allow secure access (SSH/WinRM) from the Ansible control node.

2. **Ansible (Data Collection Layer)**

   * Ansible is used to connect to Azure servers without installing any agents.
   * Playbooks are executed to gather health-related metrics such as:

     * CPU usage
     * Memory usage
     * Disk utilization
     * Uptime
     * Running services
     * OS and kernel information
   * The collected data is formatted (JSON/structured output) for easy processing.

3. **Django (Web Application Layer)**

   * The Django application receives the health data collected by Ansible.
   * Data is stored in a database for historical tracking and reporting.
   * Django views and templates are used to:

     * Display real-time server health
     * Show server-wise dashboards
     * Highlight warning or critical thresholds

4. **Automation & Integration**

   * Ansible playbooks can be triggered:

     * Manually
     * On a schedule (cron / Azure automation)
     * Via Django (using background tasks like Celery or subprocess calls)
   * This ensures regular and automated health checks.

---

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


