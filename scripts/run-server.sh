#!/bin/sh
LOGHUMAN=1 LOGLEVEL=DEBUG SET_ADDRESS=$SET_ADDRESS USE_MOCK_CHAIN=1 LOCAL=1 uvicorn briq_api.server:app --port 5055 --log-config "briq_api/logging/uvicorn_conf.json"