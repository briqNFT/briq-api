from uvicorn.workers import UvicornWorker

class CustomLogUvicornWorker(UvicornWorker):
    """Make sure uvicorn loggers are propagated so they go into structured logging."""
    CONFIG_KWARGS = {
        "log_config": {
            "version": 1,
            "disable_existing_loggers": False,
            "propagate": True,
            "loggers": {
                "uvicorn.error": {
                    "propagate": True,
                },
                "uvicorn.access": {
                    "propagate": True,
                }
            }
        }
    }
