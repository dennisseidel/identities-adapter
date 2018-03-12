# Identities Service

This includes the service that manages all the events in the Identities Domain. 

## Repository Structure

* `Dockerfile`: running the service just do a `docker run`
* `docker-compose.yml`: starts your development setup including the swagger editor as well as a mock server based on the `swagger.yaml` file located in `/swagger`/ directory
* `/api`: including the python modules for the api implementation (described in the sections below)
* `/lib`: includes currently only the library which implements a customer token validation. 

### Develop

You either can work with the dockerfile which includes all the commands to start the server or you develop locally which is suggested for development speed. 

1. Create your swagger file including examples (they are used for the mock) and place it under `/swagger/swagger.yaml`
1. Setup your environment by doing 
```
virtualenv venv --python=python3
source venv/bin/activate
# install pylint
pip install pylint
pip install -r requirements.txt
```
1. Then start the connxion mock server based on the swagger file: `connexion run swagger/swagger.yaml --mock=all`
1. Validate this with your customers like external API developers and your frontend developer and improve the API. 
1. Then implement the API resources and methods under `api`. 


### Deploy and Run

It is suggested to use the docker container for your deployment using the container runtime of your choice.

We save the environment config: 

```
# config for mongodb
export MONGODB_USERNAME=sampleUser
export MONGODB_PASSWORD=samplePassword
export MONGODB_ROOT_PASSWORD=samplePassword
export MONGODB_URL=http://localhost:27017
# config apigee
export apigee_client_id=user@sample.com
export apigee_client_secret=samplePassword
#config auth0
export auth_client_id=dsfdfndfernd34fdfn3234djfdf
export auth_client_secret=ldfjn3f3o23nf23lfj0j23fn2lfn23nf232nf23nf2nfn32fn2ffn2
```