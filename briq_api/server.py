import os
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import time

from .stores import setup_stores
from .api.routes.router import router as api_router
from .mock_chain.router import router as mock_chain_router
from .auth import router as auth_router

from .api.legacy_api import app as legacy_router

from .config import ENV

logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def add_session_cookie(request: Request, call_next):
    session_id = request.cookies['session'] if 'session' in request.cookies else None
    request.state.session_id = session_id
    response: Response = await call_next(request)
    if request.state.session_id != session_id or session_id is not None:
        response.set_cookie('session', request.state.session_id, httponly=True, samesite='lax')
    return response


# Add a simple middleware to process request time.
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    t = time.time() - start_time
    if ENV == 'prod':
        logger.info('Request for "%(url)s" processing in %(time_s)s seconds', {'url': str(request.url), 'time_s': t})
    return response

# Because of credentials, I had to CORS restrict the API.
# If I had time I'd split the admin and non-admin endpoints, but meh.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ] if ENV == 'dev' else ['*'], # In dev env I don't have the API relay so need to rely on explicit CORS.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API
app.include_router(api_router, prefix="/v1")

app.include_router(auth_router, prefix="/v1/auth")

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
