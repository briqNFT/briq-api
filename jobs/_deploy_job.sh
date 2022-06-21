#!/usr/bin/env bash
set -e

export TAG=${TAG:=$(git rev-parse HEAD)}

[ -z $JOB ] && echo 'no job' && exit 1
[ -z $JOB_NAME ] && echo 'no job' && exit 1

infra/run-docker.sh

ytt -f infra/schema.yaml -f infra/vals-test.yaml -f jobs/_schema.yaml -f jobs/_generic_job.yaml --data-value "image_tag=$TAG" \
    --data-value "job=jobs/${JOB}.py" --data-value "job_name=${JOB_NAME}" > "${JOB_NAME}.yaml"

kubectl apply -f "${JOB_NAME}.yaml"
