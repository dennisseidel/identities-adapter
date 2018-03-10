import connexion
import requests
import json

def post(identityid, client):
  # TODO check if token is in cache and only call auth0 if not available or expired 
  # TODO put this into it's own function
  token_endpoint = "https://d10l.eu.auth0.com/oauth/token"
  token_request_body = {
    "client_id": "ZT1Gz9XC3gvLa4tPFAz76uZadrkIG1md",
    "client_secret": "cVijBVMw6kPRI00oiJOS7O3XTn-EzrZKATFCcuBLr7ItlRDeZoPNeM3pVIH9JqWb", 
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
  # [client_id, client_name, client_description, date-created]
  client = {
    "name": res['name'], 
  }
  return client, 201

def get(identityid):
  return 201

def patch(identityid, identity):
  return 201