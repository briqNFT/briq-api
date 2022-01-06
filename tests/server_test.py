from unittest.mock import patch, MagicMock

from briq_api import server

# TODO: figure out why I can't test the server?
@patch('briq_api.storage.storage.get_storage', autospec=True)
def test_store_list(get_storage):
    ret = MagicMock()
    get_storage.return_value = ret
    server.store_list()
    ret.list_json.assert_called_once
