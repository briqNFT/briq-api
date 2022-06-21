## Objectives:
# Delete all stored .glb to update them for color correctedness.

import logging
from briq_api.storage.backends.cloud_storage import CloudStorage

logger = logging.getLogger(__name__)

if __name__ != '__main__':
    logger.error("Must be called as a script")

from briq_api.legacy_api import legacy_chain_id

from briq_api.storage.client import storage_client
from briq_api.storage.backends.legacy_cloud_storage import LegacyCloudStorage

def delete_glb():
    storage = LegacyCloudStorage()
    files = storage.storage_client.list_blobs(storage.bucket)
    for file in files:
        if file.name.endswith(".glb"):
            logger.info("Deleting %(file)s", {"file": file.name})
            file.delete()

delete_glb()
