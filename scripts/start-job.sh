#!/usr/bin/env bash
set -e

TAG=${TAG:=$(git rev-parse HEAD)}
K8S_ENV=${K8S_ENV:="test"}

echo "TAG: ${TAG}"
echo "ENV: ${K8S_ENV}"

NAME=${NAME}

if [ -z $NAME ]; then
    echo "Error, name must be specified"
    exit 1
fi

echo "RUNNING ${NAME}"

ytt -f infra/schema.yaml -f jobs/_schema.yaml  -f infra/vals-${K8S_ENV}.yaml -f jobs/_generic_job.yaml --data-value "job_name=briq-job-${NAME//_/-}" --data-value "job=jobs/${NAME}.py" --data-value "image_tag=$TAG" > "jobs/${NAME}_${K8S_ENV}.yaml"

echo "validating client-side"
kubectl apply -f "jobs/${NAME}_${K8S_ENV}.yaml" --validate=true --dry-run=client
echo "validating server-side"
kubectl apply -f "jobs/${NAME}_${K8S_ENV}.yaml" --validate=true --dry-run=server

echo "Creating docker image"
TAG=$TAG ./infra/run-docker.sh

echo "Now running job"
kubectl apply -f "jobs/${NAME}_${K8S_ENV}.yaml"
