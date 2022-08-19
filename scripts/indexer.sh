#!/bin/sh
LOGHUMAN=1 LOGLEVEL=DEBUG poetry run python3 -m briq_api.indexer.runner
