import json
import pytest
import pygltflib

from pyvox.writer import VoxWriter

from briq_api.mesh.briq import BriqData

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

def test_large_briq_to_vox(too_large_for_vox_briq_data):
    briq = BriqData().load(json.loads(too_large_for_vox_briq_data))
    voxFile = briq.to_vox("test.vox")
    voxFile.to_bytes()
    # Truncated
    assert len(voxFile.vox.models[0].voxels) == 256
