from __future__ import print_function
import json
import os
import httplib2
import urllib
import sys
import requests
import jwt
import googleapiclient.errors
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket
from httplib2 import Http
from json import dumps
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


#Google Auth#####################################################
headers = {}

scopes = ['https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/admin.directory.group']

credentials = ServiceAccountCredentials.from_json_keyfile_name('python-2-email-3e7929af352e.json', scopes=scopes)

account_sub = 'nicholas.petillo@translationllc.com'

delegated_credentials=credentials.create_delegated(account_sub)

httplib2.debuglevel=5

http = delegated_credentials.authorize(Http())

service = discovery.build('admin', 'directory_v1', http=http)
#Google Auth#####################################################

###ZenDesk Creds#################################################
zd_creds = {
'subdomain' : 'translationllc',
'email' : 'nicholas.petillo@translationllc.com',
'password' : 'AMQwvVJRC2GmvWHB'
}


zenpy_client = Zenpy(**zd_creds)
###ZenDesk Creds#################################################




r = requests.get('https://sheetdb.io/api/v1/xjzx9xzer55t4')

packages_json = r.json()

emails = []
firstnames = []
lastnames = []
user = []
group_add_email = []
slack_add_email = []
company = []
location = []
payload_zoom = []
start_date = []


for x in packages_json:
    emails.append(x["New Hire Email Address (first.last@translationllc.com)"])
    firstnames.append(x["Firstname"])
    lastnames.append(x["Lastname"])
    location.append(x["Office Location"])
    company.append(x["What Company Will This Person Work For"])
    user.append({"name": {"familyName": x["Lastname"], "givenName": x["Firstname"], }, "password": "Translation10jay", "primaryEmail": x["New Hire Email Address (first.last@translationllc.com)"],"changePasswordAtNextLogin": True})
    start_date.append(x["Start Date"])

search = []
skippable_emails = set()

for x in emails:
    try:
        search.append(service.users().get(userKey=x).execute())
    except googleapiclient.errors.HttpError as e:
        if e.resp.status != 404:
            raise
    else:
        skippable_emails.add(x)


for x in emails:
    group_add_email.append({'email': x, })


for x in user:
    if x['primaryEmail'] in skippable_emails:
        continue
    try:
        service.users().insert(body=x).execute()
    except:
         pass

    for x in group_add_email:
        try:
            service.members().insert(groupKey='allagency@translationllc.com', body=x).execute()
            service.members().insert(groupKey='alltranslationteam@translationllc.com', body=x).execute()
            service.members().insert(groupKey='all@translationllc.com', body=x).execute()
        except:
            pass

    for x, y in zip(company, group_add_email):
        try:
            if x == "United Masters":
                service.members().insert(groupKey='all.um.team@unitedmasters.com', body=y).execute()
        except:
            pass

    for x, y, z in zip(company, location, group_add_email):
        try:
            if x == "United Masters" and y == "Times Sq":
                service.members().insert(groupKey='um.nyc@translationllc.com', body=y).execute()
        except:
            pass

    for x, y, z in zip(company, location, group_add_email):
        try:
            if x == "United Masters" and y == "Dumbo - 10 Jay Street":
                service.members().insert(groupKey='um.nyc@translationllc.com', body=y).execute()
        except:
            pass

    for x, y, z in zip(company, location, group_add_email):
        try:
            if x == "United Masters" and y == "San Fransisco":
                service.members().insert(groupKey='sf@unitedmasters.com', body=y).execute()
        except:
            pass

    # slack_invite##########

    headers = {
        'Authorization': 'Bearer xoxp-29681298435-577964026864-578080848512-f9f26c9d20a8c478eac35c6b5f74c4f5',
        'Cache-Control': 'no-cache',
    }

    for x in emails:
        try:
            slack_add_email.append({'email': (None, x)}, )
        except:
            pass

    for x in slack_add_email:
        try:
            slack_invite = requests.post('https://slack.com/api/users.admin.invite', headers=headers, files=x)
        except:
            pass
    ###################################

    # Zoom Invite###

    encoded = jwt.encode({"iss": "l-pJkOPFTnSIGzyr3gI0aA", "exp": "1496091964000"},
                         'K4k0qiEoyq0xYjfoVy6i74xijvsX10R9Qr1f', algorithm='HS256').decode('utf-8')

    zoom_url = "https://api.zoom.us/v2/users"

    zoom_headers = {
        'Authorization': "Bearer {0}".format(encoded),
        'Content-Type': "application/json"
    }

    for x, y, z in zip(emails, firstnames, lastnames):
        payload_zoom.append(
            {"action": "create", "user_info": {"email": x, "type": "2", "first_name": y, "last_name": z}})

    for x in payload_zoom:
        try:
            zoom_invite = requests.request("POST", zoom_url, json=x, headers=zoom_headers)
        except:
            pass
    #############################################

    ###CREATE ZENDESK TICKET UPON SUCESS#########

    for x in user:
        if x['primaryEmail'] in skippable_emails:
            continue
        try:
            zenpy_client.tickets.create(Ticket(subject="New Hire | {}" .format(x['primaryEmail']), description="User Created {}\n username: {}\n password: {}" .format(x['primaryEmail'],x['primaryEmail'],x['password'])))
        except:
            pass

    ###CREATE ZENDESK TICKET UPON SUCESS#########