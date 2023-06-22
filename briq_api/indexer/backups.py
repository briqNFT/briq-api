import logging
import os
import subprocess

from pymongo import MongoClient

from briq_api.storage.file.backends.cloud_storage import CloudStorage
from .config import MONGO_USERNAME, MONGO_PASSWORD

logger = logging.getLogger(__name__)


def load_backup():
    # Connect to google cloud and find an appropriate backup.
    storage = {
        "test": 'briq-bucket-test-1',
        "prod": 'briq-bucket-prod-1',
    }[os.getenv('ENV') or "test"]
    cloud_storage = CloudStorage(storage)

    backup = cloud_storage.load_bytes("mongo_backups/backup.archive")
    with open("backup.archive", "wb") as f:
        f.write(backup)

    # Restore the backup using mongorestore in a subprocess.
    subprocess.call(['mongorestore', '--username', MONGO_USERNAME, '--password', MONGO_PASSWORD, '--archive=backup.archive'])

    # Remove the backup file.
    os.remove("backup.archive")


def write_backup():
    # Connect to google cloud and find an appropriate backup.
    storage = {
        "test": 'briq-bucket-test-1',
        "prod": 'briq-bucket-prod-1',
    }[os.getenv('ENV') or "test"]
    cloud_storage = CloudStorage(storage)

    # Obtain a backup
    subprocess.call(['mongodump', '--username', MONGO_USERNAME, '--password', MONGO_PASSWORD, '--archive=backup.archive'])

    # Save the current archive to the backup folder.
    with open("backup.archive", "rb") as f:
        # Backup the existing file
        try:
            cloud_storage.backup_file("mongo_backups/backup.archive")
        except:
            logger.info("No existing backup")
        cloud_storage.store_bytes("mongo_backups/backup.archive", f.read())

    # Remove the backup file.
    os.remove("backup.archive")


from fastapi import FastAPI
app = FastAPI()


@app.get("/health")
def health():
    return "ok"


@app.get("/write_backup")
def api_write_backup():
    write_backup()
    return "ok"

from pymongo.errors import ServerSelectionTimeoutError
import time


@app.on_event("startup")
async def startup_event():
    while True:
        try:
            # Hardcode localhost mongo, as we're not ready yet so not accessible via the regular URL.
            mongo = MongoClient(host=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost", serverSelectionTimeoutMS=1000)
            # The ismaster command is cheap and does not require auth.
            mongo.admin.command('ismaster')
            break
        except ServerSelectionTimeoutError:
            logger.info("Server is not yet available. Retrying...")
            time.sleep(1)
    try:
        load_backup()
        logger.info("Loaded backup")
    except:
        logger.warning("Could not load backup")
