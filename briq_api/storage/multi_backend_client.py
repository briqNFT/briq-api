from typing import Union, TypeVar, Generic
import logging

logger = logging.getLogger(__name__)

StorageBackend = TypeVar('StorageBackend')


class StorageClient(Generic[StorageBackend]):
    """
    A straightforward abstraction to handle differention storage setups for different 'backends'.
    Used mostly to differentiate storage between chains.
    """
    def __init__(self):
        # Fallback backend.
        self.backend: Union[None, StorageBackend] = None
        # Backend for a specific chain. Higher priority than the fallback backend
        self.backend_for = {}

    def connect(self, backend: Union[None, StorageBackend]):
        self.backend = backend

    def connect_for_chain(self, chain_id: str, backend: Union[None, StorageBackend]):
        self.backend_for[chain_id] = backend

    def get_backend(self, chain_id: str) -> StorageBackend:
        # note: this on purpose returns None if that was explicitly specified.
        if chain_id in self.backend_for:
            if not self.backend_for[chain_id]:
                raise Exception(f"No available backend for {chain_id}")
            return self.backend_for[chain_id]
        if not self.backend:
            raise Exception(f"No available backend for {chain_id}")
        return self.backend
