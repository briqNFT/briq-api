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
    briq.to_gltf().save_to_bytes()


def test_briq_to_vox(briq_data):
    briq = BriqData().load(json.loads(briq_data))
    voxFile = briq.to_vox("test.vox")
    voxFile.to_bytes()
    # Not truncated
    assert len(voxFile.vox.models[0].voxels) == 3

@pytest.fixture
def too_large_briq_data():
    briqs = []
    for i in range(0, 300):
        briqs.append((str(i), f'"#{hex(i//2)[2:].ljust(2, "0")}{hex((i+1)//2)[2:].ljust(2, "0")}00"'))
    return """
{
    "id": "0x1234",
    "description": "",
    "name": "toto",
    "regionSize": 10,
    "version": 1,
    "briqs": [
""" + ','.join(["""{"pos": [""" + x[0] + """, 0, 0], "data": {"material": "0x2", "color": """ + x[1] + "}}" for x in briqs]) + "]}"


def test_large_briq_to_vox(too_large_briq_data):
    briq = BriqData().load(json.loads(too_large_briq_data))
    voxFile = briq.to_vox("test.vox")
    voxFile.to_bytes()
    # Truncated
    assert len(voxFile.vox.models[0].voxels) == 255
