import json
import pytest
import pygltflib

from pyvox.writer import VoxWriter

from briq_api.mesh.briq import BriqData

@pytest.fixture
def briq_data():
    return """
{
    "id": "0x1234",
    "description": "",
    "name": "toto",
    "regionSize": 10,
    "version": 1,
    "briqs": [
        {"pos": [-3, 0, 0], "data": {"material": "0x1", "color": "#c5ac73"}},
        {"pos": [-2, 0, 0], "data": {"material": "0x1", "color": "#c5ac73"}},
        {"pos": [-1, 0, 0], "data": {"material": "0x2", "color": "#fafafa"}}
    ]
}
"""

def test_briq_to_gltf(briq_data):
    briq = BriqData().load(json.loads(briq_data))
    assert isinstance(briq.to_gltf(), pygltflib.GLTF2)


def test_briq_to_vox(briq_data):
    briq = BriqData().load(json.loads(briq_data))
    assert isinstance(briq.to_vox("test.vox"), VoxWriter)
