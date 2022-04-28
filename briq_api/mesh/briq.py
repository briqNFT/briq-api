import json
from typing import Dict, Sequence

from .vox import to_vox

from .gltf import to_gltf

class BriqData:
    briqs: Sequence
    def __init__(self):
        pass

    def load_file(self, filename):
        filedata = None
        with open(filename, "r") as f:
            filedata = json.load(f)
        self.load(filedata)
        return self

    def load(self, jsonData: Dict):
        self.briqs = jsonData['briqs']
        return self


    def to_vox(self, filename: str):
        writer = to_vox(self)
        writer.filename = filename
        return writer

    def to_gltf(self):
        return to_gltf(self.briqs)

