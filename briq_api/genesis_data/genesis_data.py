
from briq_api.storage.backends.file_storage import FileStorage
from briq_api.storage.client import StorageClient


genesis_storage = StorageClient()
genesis_storage.connect_for_chain("localhost", FileStorage("briq_api/genesis_data/localhost/"))
