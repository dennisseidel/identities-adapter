#!/bin/bash

#check where gcloud is installed 
which gcloud

# Set Google Application Credentials
echo $GCLOUD_SERVICE_KEY | base64 --decode --ignore-garbage > ${HOME}/gcloud-service-key.json && export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/gcloud-service-key.json"

# Authenticate the gcloud tool
gcloud auth activate-service-account --key-file=${HOME}/gcloud-service-key.json
gcloud config set project $GCLOUD_PROJECT

# Install kubectl
apt-get install kubectl