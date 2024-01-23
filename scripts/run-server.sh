#!/bin/sh
set -a

source .env
source .env.prod
LOGHUMAN=1 LOGLEVEL=DEBUG LOCAL=1 poetry run uvicorn briq_api.server:app --port 5055 --log-config "briq_api/logging/uvicorn_conf.json" --timeout-keep-alive 300