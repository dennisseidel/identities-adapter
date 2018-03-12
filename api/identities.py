import connexion
import requests
import json
import urllib.parse
import os
from datetime import datetime
from pymongo import MongoClient

username= urllib.parse.quote_plus(os.environ['MONGODB_USERNAME'])
password = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
mongo_url = urllib.parse.quote_plus(os.environ['MONGODB_URL'])
mdb_client = MongoClient('mongodb://%s:%s@%s/identities' % (username, password, mongo_url))
auth0_client_id= urllib.parse.quote_plus(os.environ['auth_client_id'])
auth0_client_secret= urllib.parse.quote_plus(os.environ['auth_client_secret'])
apigee_client_id= os.environ['apigee_client_id']
apigee_client_secret= os.environ['apigee_client_secret']

def post(identityid, client):
  # TODO check if token is in cache and only call auth0 if not available or expired 
  # TODO put this into it's own function
  token_endpoint = "https://d10l.eu.auth0.com/oauth/token"
  token_request_body = {
    "client_id": auth0_client_id,
    "client_secret": auth0_client_secret, 
    "audience": "https://d10l.eu.auth0.com/api/v2/",
    "grant_type": "client_credentials"
    }
  token_headers = { 'content-type': "application/json" }
  response = requests.post(token_endpoint, json=token_request_body, headers=token_headers)
  jsonData = response.json()
  access_token = jsonData['access_token']
  # TODO cache this token
  # function create client in auth0 
  endpoint = "https://d10l.eu.auth0.com/api/v2/clients"
  request_body = {
    "name": client['client_name'],
    "description": client['client_description'],
    "callbacks": client['allowed_callback_urls'],
    "allowed_logout_urls": client['allowed_logout_urls']
  }
  headers = {"Authorization":"Bearer " + access_token}
  auth0_client_created = requests.post(endpoint,json=request_body,headers=headers).json()
  # TODO check if apigee token is in cache otherwise get new token
  apigee_token_endpoint = "https://login.apigee.com/oauth/token"
  apigee_token_request_body = {
    'username': apigee_client_id,
    'password': apigee_client_secret, 
    'grant_type': 'password'
  }
  apigee_token_headers = {
    'Authorization': 'Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0'
  }
  r = requests.post(apigee_token_endpoint, data=apigee_token_request_body, headers=apigee_token_headers)
  jsonData = r.json()
  apigee_access_token=jsonData['access_token']
  # get the email from the profiledb and add it to the request 
  apigee_endpoint="https://api.enterprise.apigee.com/v1/organizations/denseidel-trial/developers/den.seidel@gmail.com/apps"
  apigee_add_app_request_body= {
    "name": client['client_name'],
    #"callbackUrl" : "https://url-for-3-legged-oauth/"
  }
  apigee_add_app_request_headers = {
    "Authorization": "Bearer " + apigee_access_token,
    "Content-Type": "application/json",
  }
  r = requests.post(apigee_endpoint, json=apigee_add_app_request_body, headers=apigee_add_app_request_headers)
  # update the clientid and client secret with the one recieved from the IDM
  apigee_update_client_credentials_endpoint = 'https://api.enterprise.apigee.com/v1/organizations/denseidel-trial/developers/%s/apps/%s/keys/create' % ('den.seidel@gmail.com', client['client_name'])
  apigee_update_client_credentials_request_body = {
    "consumerKey": auth0_client_created['client_id'], 
    "consumerSecret": auth0_client_created['client_secret']
  }
  apigee_updated_client_credentials = requests.post(apigee_update_client_credentials_endpoint,json=apigee_update_client_credentials_request_body,headers=apigee_add_app_request_headers)
  # save in a key value store under the identityid the array of clients including everything needed to display in the portal
  identities = mdb_client['identities']
  identity = identities.identity
  identity_data = { '_id': identityid }
  client_data = {
    'client_id': auth0_client_created['client_id'],
    'client_name': auth0_client_created['name'],
    'client_description': auth0_client_created['description'],
    'date_created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
  }
  result = identity.update_one(identity_data, { '$push': { 'clients': client_data}}, upsert=True)
  client = {
    "name": client_data['client_name'], 
  }
  return client, 201

def get(identityid):
  print(identityid)
  # get the data for the identityid from the profile db
  identities = mdb_client['identities']
  identity = identities.identity
  result = identity.find_one({"_id": identityid})
  clients = {
    "clients": []
  }
  for client in result["clients"]:
    clients['clients'].append(client) 
    #{'client_id': 'yecR7Dprg7tbip4P3d4gAbcnW6leQcqG', 'client_name': 'test', 'client_description': 'test', 'date_created': '2018-03-11T19:41:14'}
  return clients, 201

def patch(identityid, identity):
  return 201