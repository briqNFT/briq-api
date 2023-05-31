#!/bin/sh
source .env
APIBARA_AUTH_TOKEN=$APIBARA_AUTH_TOKEN LOGHUMAN=1 LOGLEVEL=DEBUG poetry run python3 -m briq_api.indexer.runner
