#!/usr/bin/python3

## Create Service-Now event from Zabbix, Old script was creating Incidents from Zabbix.
## We have really changed this since the old script so the copyright doesn't really
## matter, but props to the old scripter still
## Old Copyright (C) 2001-2015 Jan Garaj - www.jangaraj.com for creating Incidents
## https://github.com/monitoringartist/zabbix-script-servicenow
## Doc: http://wiki.servicenow.com/index.php?title=Python_Web_Services_Client_Examples
## WSDL doc: https://<your_instance>.service-now.com/incident.do?WSDL
##

##ToDo:
##Encrypt password or OAuth2
##Use Webhook URL instead of standard u_event API URL
##Update recommended settings

debug     = 0
instance  = 'INSTANCE'   # Service-Now instance
username  = 'USERNAME'   # Service-Now login
password  = 'PASSWORD'   # Service-Now password
interface = 'em_event'   # Use whatever interface your instace of Service-Now uses examples em_event, u_event
category  = 'Category'        # Category of incident
scategory = 'Subcategory'     # Subcategory of incident


import re, sys

# command line arguments
# subject - {TRIGGER.STATUS} - PROBLEM or OK

subject = sys.argv[2]

# message - whatever message the Zabbix action sends, preferably something like "Zabbix server is unreachable for 5 minutes"

# recommended setting: add recommended settings for documentation here.
# This is currently what we have set in Zabbix.
'''
Trigger: {TRIGGER.NAME}
Trigger description: {TRIGGER.DESCRIPTION}
Trigger severity: {TRIGGER.SEVERITY}
Trigger nseverity: {TRIGGER.NSEVERITY}
Trigger status: {TRIGGER.STATUS}
Trigger URL: {TRIGGER.URL}
Host: {HOST.HOST}
Host IP:{HOST.IP}
Host description: {HOST.DESCRIPTION}
Event age: {EVENT.AGE}
Current Zabbix time: {DATE} {TIME}

Item values:

1. {ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}

Event Graph: ZabbixServer.com/zabbix/history.php?action=showvalues&itemids[]={ITEM.ID1}
Event Details: ZabbixServer.com/zabbix/tr_events.php?triggerid={TRIGGER.ID}&eventid={EVEN T.ID}

metic_name: {ITEM.NAME}


Zabbix event ID: {EVENT.ID}
'''
message = sys.argv[3]

# value mapping
zabbix2servicenow = {
    # parse from Zabbix message, remap value if map exists
    'dynamic': {
        'severity': '^Trigger nseverity: .*',
        'configuration_item': '^Host: .*',
        'short_description': '^Trigger: .*',
        'zabbix_event_id': '^Zabbix event ID: .*',
        'metric_name': '^metic_name: .*',
        'graph_url': '^Event Graph: .*',
        'event_url': '^Event Details: .*',
        'host_ip': '^Host IP: .*',
    },
    # maps Zabbix value -> Service Now value
    'maps': {
        'severity': {
            # ServiceNow: 1 - Critical, 2 - Error, 3 - Moderate, 4 - Low, 5 - Project
            # Zabbix:     0 - Not classified, 1 - Information, 2 - Warning, 3 - Average, 4 - High, 5  - Disaster
            '0': '3',
            '1': '3',
            '2': '3',
            '3': '2',
            '4': '1',
            '5': '1',
        }
    },
    # static
    'static': {
        'category': category,
        'subcategory': scategory,
        'additional_info': message,
    }
}
incident = zabbix2servicenow['static']
for key in zabbix2servicenow['dynamic']:
    items=re.findall(zabbix2servicenow['dynamic'][key], message, re.MULTILINE)
    if len(items) != 1:
        if debug:
            print('Problem with "%s" matching, found %i times' % (zabbix2servicenow['dynamic'][key], len(items)))
        incident[key] = 'Problem with "%s" matching, found %i times' % (zabbix2servicenow['dynamic'][key], len(items))
        continue
    else:
        items[0] = items[0].split(':')[1].strip()
        if key in zabbix2servicenow['maps']:
            if items[0] not in zabbix2servicenow['maps'][key]:
                if debug:
                    print("Problem with mapping of value %s" % str(items[0]))
                incident[key] = "Problem with mapping of value %s" % str(items[0])
            else:
                incident[key] = zabbix2servicenow['maps'][key][items[0]]
        else:
            incident[key] = items[0]

# add host name to short description
incident['short_description'] = incident['configuration_item'] + ": " + incident['short_description']+ "\n Event URL: http://" + incident['event_url'] + "\n Graph URL: http://" + incident['graph_url']


import requests, json
#starting to add OAuth possible, Testing with OAuth1, but looking into OAuth2.
from requests_oauthlib import OAuth1

# Set the Proxy if needed, if not comment it out and remove it below in the response
proxies = {
    'https': 'PROXY_ADDRESS:PORT',
}

# Set the request parameters, Looking into using the Webhook URL.
url = 'https://%s.service-now.com/api/now/table/%s' % (instance, interface)
#starting to add OAuth possible
#auth = OAuth1('YOUR_APP_KEY', 'YOUR_APP_SECRET', 'USER_OAUTH_TOKEN', 'USER_OAUTH_TOKEN_SECRET')


# Set proper headers
headers = {"Content-Type":"application/json","Accept":"application/json"}

# Do the HTTP request
# Payload is what zabbix sends to service-now fields
payload={
        "u_event_source":'ZabbixPCC',
        "u_event_severity":incident['severity'],
        "subcategory":incident['subcategory'],
        "category":incident['category'],
        "u_node":incident['configuration_item'],
        "description":incident['short_description'],
        "u_additional_info":incident['additional_info'],
        "message_key":incident['zabbix_event_id'],
		"correlation_id":incident['zabbix_event_id'],
        "metric_name":incident['metric_name'],
        "u_node_ipv4_address":incident['host_ip']
}
payload2 = json.dumps(payload)
response = requests.post(url, proxies=proxies, auth=(username, password), headers=headers ,data=payload2)
# starting to add OAuth possible
#response = requests.post(url, proxies=proxies, auth=auth, headers=headers ,data=payload2)

# Check for HTTP codes other than 200
if response.status_code != 200:
    print(('Status:', response.status_code, 'Headers:', response.headers, 'Error Response:',response.json()))
    exit()

# Decode the JSON response into a dictionary and use the data
data = response.json()
print(data)
