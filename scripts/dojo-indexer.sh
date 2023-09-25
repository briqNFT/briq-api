#!/bin/sh
source .env
APIBARA_AUTH_TOKEN=$APIBARA_AUTH_TOKEN LOGHUMAN=1 LOGLEVEL=DEBUG \
    INDEXER_ID=dojo-0 NETWORK_NAME="starknet-testnet-dojo" poetry run python3 -m briq_api.indexer.runner
