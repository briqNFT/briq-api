import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from briq_api.legacy_api import on_startup, app as legacy_api_router, legacy_chain_id
from briq_api.storage.backends.cloud_storage import CloudStorage
from briq_api.storage.backends.file_storage import FileStorage
from briq_api.storage.backends.legacy_cloud_storage import LegacyCloudStorage
from briq_api.storage.client import storage_client
from .api.router import router as api_router
from .mock_chain.router import router as mock_chain_router

logger = logging.getLogger(__name__)

app = FastAPI()

# This is a public API, so allow any CORS origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API
app.include_router(api_router, prefix="/v1")

app.include_router(legacy_api_router)

if os.getenv("USE_MOCK_CHAIN"):
    app.include_router(mock_chain_router, prefix='/mock_chain')

@app.get("/health")
def health():
    return "ok"


@app.on_event("startup")
def startup_event():
    if not os.getenv("LOCAL"):
        logger.info("Connecting normally.")
        storage_client.connect_for_chain(chain_id="starknet-testnet", backend=CloudStorage('briq-bucket-test-1'))
        storage_client.connect_for_chain(legacy_chain_id, LegacyCloudStorage())
    else:
        # Don't attempt connecting to the cloud in that mode,
        # we expect to run locally and it makes it faster to reload the API
        logger.info("Connecting locally.")
        storage_client.connect(FileStorage())
    if os.getenv("USE_MOCK_CHAIN"):
        logger.info("Connecting for mock chain.")
        mock_storage = FileStorage()
        # Add an artificial slowdown
        mock_storage.slowdown = 0.5
        storage_client.connect_for_chain('mock', mock_storage)

    on_startup()
