# Create Events in Service Now from Zabbix Alarms
Send Zabbix Alarms to Service Now via Python 3 using the Service Now API

Created script because needed to send zabbix alarms to snow, but didn't ahve the event maangent tool to do it the easy way.

# Installation
Fist some prep work. You will need to have Python 3 installed. You will need to also have two Python 3 modules installed (installing the modules via PIP3 makes is a little easier). Modules that need to be installed: `requests` and `requests_oauthlib`.

You can test to make sure everything installed correctly by running Python 3 and then importing the modules. If there are any errors you should troubleshoot before proceeding.

Copy the `zabbix-create-event-snow-V1.py` script into the `AlertScriptsPath` 
directory which is by default `/usr/lib/zabbix/alertscripts` and make it executable:

    $ cd /usr/lib/zabbix/alertscripts
    $ wget https://raw.github.com/derpaherk/zabbix-alarms-to-servicenow.git 
    $ chmod 755 zabbix-create-event-snow-V1.py
   
Now that the script has been copied and permissions set. You will need to edit the script to meet your correct setup. 
 There are 4 to 5 lines that will need to be changed. The 5th is only if you are using a Proxy.
    
    $ instance  = 'SNOWinstance'   # Service Now Instance Name
    $ username  = 'Username'          # Service-Now login
    $ password  = 'Password'   # Service-Now password
    $ interface = 'interface'   # Use whatever interface your instace of Service-Now uses examples em_event, u_event
    The Proxy line is farther down in the script
    $ proxies = {
    $ 'https': 'PROXY_ADDRESS:PORT',
    $ }
