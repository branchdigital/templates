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

headers = {}

scopes = ['https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/admin.directory.group']

credentials = ServiceAccountCredentials.from_json_keyfile_name('onboarding-258717-1c194ff25527.json', scopes=scopes)

account_sub = 'branchdigital@wavelengthproductions.com'

delegated_credentials=credentials.create_delegated(account_sub)

httplib2.debuglevel=5

http = delegated_credentials.authorize(Http())

service = discovery.build('admin', 'directory_v1', http=http)


r = requests.get('https://sheetdb.io/api/v1/3wq7wwc6n45v8')

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
    emails.append(x["New Hire Email Address"])
    firstnames.append(x["Firstname"])
    lastnames.append(x["Lastname"])
    user.append({"name": {"familyName": x["Lastname"], "givenName": x["Firstname"], }, "password": "wavelength@gmail", "primaryEmail": x["New Hire Email Address"],"changePasswordAtNextLogin": True})

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



    # slack_invite##########

    headers = {
        'Authorization': 'Bearer xoxp-623161294071-776802075554-831803212823-40326856057e697c8964963d232c8126',
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


    