import json
from typing import Dict, Sequence


class BriqData:
    briqs: Sequence

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
        from .vox import to_vox
        writer = to_vox(self)
        writer.filename = filename
        return writer

    def to_gltf(self, separate_any_color: bool = False):
        from .gltf import to_gltf
        return to_gltf(self.briqs, separate_any_color)

    def to_png(self):
        from .png import to_png
        return to_png(self.briqs)
