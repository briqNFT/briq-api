#!/bin/sh
source .env
STARKNET_COMPILE_PATH=$STARKNET_COMPILE_PATH \
ALCHEMY_API_KEY_TESTNET=$ALCHEMY_API_KEY_TESTNET \
NETHERMIND_RPC_KEY_TESTNET=$NETHERMIND_RPC_KEY_TESTNET \
LOGHUMAN=1 LOGLEVEL=DEBUG LOCAL=1 poetry run uvicorn briq_api.server:app --port 5055 --log-config "briq_api/logging/uvicorn_conf.json"
