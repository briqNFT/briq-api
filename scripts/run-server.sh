#!/bin/sh
source .env
ALCHEMY_API_KEY_TESTNET=$ALCHEMY_API_KEY_TESTNET LOGHUMAN=1 LOGLEVEL=DEBUG LOCAL=1 poetry run uvicorn briq_api.server:app --port 5055 --log-config "briq_api/logging/uvicorn_conf.json"
