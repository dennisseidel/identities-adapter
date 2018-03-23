#!/bin/bash

#Get Istio

# Donwload latest version and set path variable to istio e.g. "$PATH:/Users/den/repo/test/istio-0.6.0/bin"
curl -L https://git.io/getLatestIstio | sh -

# Iternate of the list of all folder in the dir and search for the folder with pattern istio-* then save this
# foldername to env var ISTIO_DIR
export ISTIO_DIR="$(find . -type d -name istio-*.*  -exec basename {} \;)"

#install istio
kubectl apply -f $ISTIO_DIR/install/kubernetes/istio.yaml
kubectl apply -f $ISTIO_DIR/install/kubernetes/istio-auth.yaml


# Add-ons
kubectl apply \
  -f $ISTIO_DIR/install/kubernetes/addons/prometheus.yaml \
  -f $ISTIO_DIR/install/kubernetes/addons/grafana.yaml \
  -f $ISTIO_DIR/install/kubernetes/addons/servicegraph.yaml \
  -f $ISTIO_DIR/install/kubernetes/addons/zipkin.yaml \
  -f $ISTIO_DIR/install/kubernetes/addons/zipkin-to-stackdriver.yaml


# Configuring secure ingress (HTTPS)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /tmp/tls.key -out /tmp/tls.crt -subj "/CN=d10l.de"

istio_secret_check=$(kubectl get -n istio-system secrets)
if [[ $istio_secret_check != *"istio-ingress-certs"* ]]; then
  kubectl create -n istio-system secret tls istio-ingress-certs --key /tmp/tls.key --cert /tmp/tls.crt
fi