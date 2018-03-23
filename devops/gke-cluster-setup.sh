#!/bin/bash

# Create gke cluster
clustercheck=$(gcloud container clusters describe "marketplace-istio" --zone "us-east1-b" --verbosity=none)
if [[ $clustercheck != *"RUNNING"* ]]; then
    gcloud beta container \
      clusters create "marketplace-istio" \
      --project "trusty-acre-156607" \
      --quiet \
      --enable-kubernetes-alpha \
      --cluster-version "latest" \
      --username="admin" \
      --zone "us-east1-b" \
      --node-locations "us-east1-b","us-east1-c","us-east1-d" \
      --machine-type "n1-standard-1" \
      --num-nodes "1" \
      --labels environment=development \
      --enable-cloud-logging \
      --enable-cloud-monitoring  
    # Retrieve cluster credentials
    gcloud container clusters get-credentials marketplace-istio \
      --zone us-east1-b --project trusty-acre-156607

    # Grant cluster admin permissions to the current user (admin permissions are required to create the necessary RBAC rules for Istio):
    kubectl create clusterrolebinding cluster-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value core/account)
fi

# Retrieve cluster credentials
    gcloud container clusters get-credentials marketplace-istio \
      --zone us-east1-b --project trusty-acre-156607