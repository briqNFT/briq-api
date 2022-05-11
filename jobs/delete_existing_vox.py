## Objectives:
# Delete all stored .vox, as they are broken.

import copy
import logging
from briq_api.storage.backends.cloud_storage import CloudStorage

logger = logging.getLogger(__name__)

if __name__ != '__main__':
    logger.error("Must be called as a script")


from briq_api.storage.backend_interface import get_storage
set_storage = get_storage()
state_storate = get_storage("jobs/delete_existing_vox/")


def delete_vox():
    files = set_storage.iterate_files()
    for file in files:
        if file.endswith(".vox"):
            if isinstance(set_storage, CloudStorage):
                set_storage.bucket.blob(set_storage.path + file).delete()
                logger.info("Deleting %(file)s", {"file": file})

delete_vox()
