import logging
from briq_api.storage.file_storage import FileStorage
from briq_api.storage.storage import IStorage

logger = logging.getLogger(__name__)

storage_client: IStorage = FileStorage()


def get_storage_client():
    return storage_client


def setup_local_storage(path=None):
    global storage_client
    if path is not None:
        storage_client = FileStorage(path)
    else:
        storage_client = FileStorage()
    return storage_client


def setup_storage(path=None):
    global storage_client
    try:
        from briq_api.storage.cloud_storage import CloudStorage
        if path is not None:
            storage_client = CloudStorage(path)
        else:
            storage_client = CloudStorage()
    except:
        logger.warning("Falling back to local storage")
        from briq_api.storage.file_storage import FileStorage
        if path is not None:
            storage_client = FileStorage(path)
        else:
            storage_client = FileStorage()
    return storage_client
