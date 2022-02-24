#!/bin/sh
LOGHUMAN=1 LOGLEVEL=DEBUG SET_ADDRESS=$SET_ADDRESS uvicorn briq_api.server:app --port 5050 --log-config "briq_api/logging/uvicorn_conf.json"