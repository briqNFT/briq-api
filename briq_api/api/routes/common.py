from typing import Callable

from fastapi import HTTPException, Request, Response
from fastapi.routing import APIRoute

from briq_api.storage.multi_backend_client import NoBackendException


def ExceptionWrapperRoute(logger):
    class ExceptionWrapperRoute_(APIRoute):
        def get_route_handler(self) -> Callable:
            original_route_handler = super().get_route_handler()

            async def custom_route_handler(request: Request) -> Response:
                try:
                    return await original_route_handler(request)
                except NoBackendException as e:
                    logger.warning("No backend found for network %(network)s", {"network": e.chain_id}, exc_info=e, extra={"request_url": str(request.url)})
                except FileNotFoundError as e:
                    logger.warning("File not found", exc_info=e, extra={"request_url": str(request.url)})
                except HTTPException as e:
                    logger.error(e, exc_info=e, extra={"request_url": str(request.url)})
                    raise e
                except Exception as e:
                    logger.error(e, exc_info=e, extra={"request_url": str(request.url)})
                raise HTTPException(status_code=500, detail="Data could not be returned.")
            return custom_route_handler
    return ExceptionWrapperRoute_
