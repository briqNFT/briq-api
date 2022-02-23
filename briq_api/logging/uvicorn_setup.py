import json
import os

from uvicorn.workers import UvicornWorker

class CustomLogUvicornWorker(UvicornWorker):
    """Make sure uvicorn loggers are propagated so they go into structured logging."""
    CONFIG_KWARGS = {"log_config": json.load(open(os.path.join(os.path.dirname(__file__), "uvicorn_conf.json"), "r"))}