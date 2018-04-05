#!/bin/bash

set -ex
# SET THE FOLLOWING VARIABLES
# docker hub username 
USERNAME=dennisseidel
# image name TODO get this from config? 
IMAGE=identitiesadapter
# get latest githash
LATEST_GIT_HASH=$(git log -1 --format=%h)

# Donwload latest version and set path variable to istio for istioctl e.g. "$PATH:/Users/den/repo/test/istio-0.6.0/bin"
curl -L https://git.io/getLatestIstio | sh -
export ISTIO_DIR="$(find . -type d -name istio-*.*  -exec basename {} \;)"

# ensure we're up to date
git pull

# bump version
bump patch
version=`cat VERSION`
echo "version: $version"
# run build
docker build -t $USERNAME/$IMAGE:latest --build-arg GIT_COMMIT=$LATEST_GIT_HASH .

#display the githash in the image
docker inspect $USERNAME/$IMAGE:latest | jq '.[].ContainerConfig.Labels'

# UNIT TESTS
# docker exec $USERNAME/$IMAGE:latest npm run test

# GETS THE CURRENT CANARY VERSION FROM VERSION FILE
cd ./devops/config
sed "s@\$CANARY_VERSION@$version@g" identitiesadapter-template.yaml > identitiesadapter.yaml
cd ../../

# push to docker hub
docker login -u $USERNAME -p $DOCKER_PASSWORD 
docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$version
# push it
docker push $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$version

# install app
cluster_ip=$(gcloud container clusters describe marketplace-istio --zone=us-east1-b | grep -e clusterIpv4Cidr -e servicesIpv4Cidr | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{2}\b" | paste -sd "," -)
kubectl apply -f <($PWD/$ISTIO_DIR/bin/istioctl kube-inject -f devops/config/identitiesadapter.yaml --includeIPRanges={$cluster_ip})
# kubectl apply -f <(istioctl kube-inject -f $ISTIO_DIR/samples/bookinfo/kube/bookinfo.yaml)

# Confirm all services and pods are correctly defined and running
kubectl get services
kubectl get pods

# Determining the ingress IP and Port https://istio.io/docs/tasks/traffic-management/ingress.html
#export GATEWAY_URL=<workerNodeAddress>:$(kubectl get svc istio-ingress -n istio-system -o jsonpath='{.spec.ports[0].nodePort}')
#kubectl get ingress -o wide
clustercheck=$(gcloud compute firewall-rules describe "allow-book" --verbosity=none)
if [[ $clustercheck != *"allow-book"* ]]; then
  gcloud compute firewall-rules create allow-book --allow tcp:$(kubectl get svc istio-ingress -n istio-system -o jsonpath='{.spec.ports[0].nodePort}')
fi

# confirm bookinfo app is running (can I use a health-check or prometheus?)
#curl -o /dev/null -s -w "%{http_code}\n" http://${GATEWAY_URL}/productpage

#Delete istio binaries
rm -rf $ISTIO_DIR
# RLEASE AS BUILD VERSION (X.X.X+1)
# login to github
git config --global user.email "den.seidel+cicd@gmail.com"
git config --global user.name "cicd"
git config --global push.default simple
# tag it
git add -A
git commit -m "version $version [skip ci]"
git tag -a "$version" -m "version $version"
#git push
git push
git push --tags