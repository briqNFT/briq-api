import pathlib
from briq_api.storage.file.backends.file_storage import FileStorage
from briq_api.theme_storage import ThemeStorage


def test_theme_storage_booklet(tmp_path: pathlib.Path):
    storage = ThemeStorage()
    storage.connect(FileStorage(str(tmp_path) + '/', True))
    storage.reset_cache()

    # Create a file at genesis_themes/booklet_spec.json
    storage.get_backend('anyone').store_json('genesis_themes/booklet_spec.json', {
        'test': '0x1234',
        'version': 1,
        "test-network-2": {
            "test": "0x5555"
        }
    })

    assert storage.get_booklet_spec('test-network-1')['test'] == '0x1234'
    assert storage.get_booklet_spec('test-network-2')['test'] == '0x5555'
