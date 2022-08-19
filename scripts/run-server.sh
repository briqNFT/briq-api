#!/bin/sh
LOGHUMAN=1 LOGLEVEL=DEBUG USE_MOCK_CHAIN=1 LOCAL=1 poetry run uvicorn briq_api.server:app --port 5055 --log-config "briq_api/logging/uvicorn_conf.json"
