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
auth0_endpoint = os.environ['auth0_endpoint'] # https://d10l.eu.auth0.com
apigee_management_endpoint = os.environ['apigee_management_endpoint'] # https://api.enterprise.apigee.com/v1/organizations/denseidel-trial
apigee_auth_endpoint = os.environ['apigee_auth_endpoint'] # https://login.apigee.com/oauth/token

def get_idp_access_token():
  # TODO check if token is in cache and only call auth0 if not available or expired
  endpoint= "%s/oauth/token" % (auth0_endpoint)
  request_body = {
    "client_id": auth0_client_id,
    "client_secret": auth0_client_secret, 
    "audience": "%s/api/v2/" % (auth0_endpoint),
    "grant_type": "client_credentials"
    }
  headers = { 'content-type': "application/json" }
  response = requests.post(endpoint, json=request_body, headers=headers)
  jsonData = response.json()
  access_token = jsonData['access_token']
  # TODO cache this token
  return access_token

def create_client_in_idp(access_token, client):
  request_body = {
    "name": client['client_name'],
    "description": client['client_description'],
    "callbacks": client['allowed_callback_urls'],
    "allowed_logout_urls": client['allowed_logout_urls']
  }
  headers = {"Authorization":"Bearer " + access_token}
  client = requests.post("%s/api/v2/clients" % (auth0_endpoint),json=request_body,headers=headers).json()
  return client

def get_apigw_access_token():
  # TODO check if apigee token is in cache otherwise get new token
  endpoint = apigee_auth_endpoint
  request_body = {
    'username': apigee_client_id,
    'password': apigee_client_secret, 
    'grant_type': 'password'
  }
  headers = {
    'Authorization': 'Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0'
  }
  r = requests.post(endpoint, data=request_body, headers=headers)
  jsonData = r.json()
  access_token=jsonData['access_token']
  return access_token

def create_client_in_apigw(access_token, client):
  # get the email from the profiledb and add it to the request 
  endpoint="%s/developers/den.seidel@gmail.com/apps" % (apigee_management_endpoint)
  request_body= {
    "name": client['name'],
  }
  headers = {
    "Authorization": "Bearer " + access_token,
    "Content-Type": "application/json",
  }
  r = requests.post(endpoint, json=request_body, headers=headers)
  # update the clientid and client secret with the one recieved from the IDM
  endpoint = '%s/developers/%s/apps/%s/keys/create' % (apigee_management_endpoint, 'den.seidel@gmail.com', client['client_name'])
  request_body = {
    "consumerKey": client['client_id'], 
    "consumerSecret": client['client_secret']
  }
  requests.post(endpoint,json=request_body,headers=headers)

def save_client_to_profiledb(client, identityid):
  # save in a key value store under the identityid the array of clients including everything needed to display in the portal
  identities = mdb_client['identities']
  identity = identities.identity
  identity_data = { '_id': identityid }
  client_data = {
    'client_id': client['client_id'],
    'client_name': client['name'],
    'client_description': client['description'],
    'date_created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
  }
  result = identity.update_one(identity_data, { '$push': { 'clients': client_data}}, upsert=True)
  client = {
    "client_id": client_data['client_id'],
    "client_name": client_data['client_name'],
    "client_description": client_data['client_description'],
    "date_created": client_data['date_created']
  }
  return client

def post(identityid, client):
  idp_access_token = get_idp_access_token()
  idp_created_client = create_client_in_idp(idp_access_token,client)
  apigw_access_token = get_apigw_access_token()
  create_client_in_apigw(apigw_access_token, idp_created_client)
  client = save_client_to_profiledb(idp_created_client, identityid)
  return client, 201

def get(identityid):
  # get the data for the identityid from the profile db
  identities = mdb_client['identities']
  identity = identities.identity
  result = identity.find_one({"_id": identityid})
  clients = {
    "clients": []
  }
  for client in result["clients"]:
    clients['clients'].append(client) 
  return clients, 201

def patch(identityid, identity):
  return 201