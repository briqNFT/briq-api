import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import logging
import time

from .stores import setup_stores
from .api.routes.router import router as api_router
from .mock_chain.router import router as mock_chain_router

from .api.legacy_api import app as legacy_router

logger = logging.getLogger(__name__)

app = FastAPI()

# Add a simple middleware to process request time.
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    t = time.time() - start_time
    logger.info('Request for "%(url)s" processing in %(time_s)s seconds', {'url': str(request.url), 'time_s': t})
    return response

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
app.include_router(api_router)

# Include the legacy api for alpha testnet support.
app.include_router(legacy_router)

if os.getenv("USE_MOCK_CHAIN"):
    app.include_router(mock_chain_router, prefix='/mock_chain')


@app.get("/health")
def health():
    return "ok"


@app.on_event("startup")
def startup_event():
    setup_stores(os.getenv("LOCAL"), os.getenv("USE_MOCK_CHAIN"))
