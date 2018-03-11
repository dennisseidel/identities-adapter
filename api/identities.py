import connexion
import requests
import json
import urllib.parse
import os
from datetime import datetime
from pymongo import MongoClient

username= urllib.parse.quote_plus(os.environ['MONGODB_USERNAME'])
password = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
mdb_client = MongoClient('mongodb://%s:%s@mongodb:27017/identities' % (username, password))
auth0_client_id= urllib.parse.quote_plus(os.environ['auth0_client_id'])
auth0_client_secret= urllib.parse.quote_plus(os.environ['auth0_client_secret'])


def post(identityid, client):
  # TODO check if apigee token is in cache otherwise get new token
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
  res = requests.post(endpoint,json=request_body,headers=headers).json()
  # save in a key value store under the identityid the array of clients including everything needed to display in the portal
  identities = mdb_client['identities']
  identity = identities.identity
  identity_data = { '_id': identityid }
  client_data = {
    'client_id': res['client_id'],
    'client_name': res['name'],
    'client_description': res['description'],
    'date_created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
  }
  result = identity.update_one(identity_data, { '$push': { 'clients': client_data}}, upsert=True)
  client = {
    "name": res['name'], 
  }
  return client, 201

def get(identityid):
  return 201

def patch(identityid, identity):
  return 201