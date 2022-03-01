from __future__ import annotations

from pyvox.parser import VoxParser
from pyvox.writer import VoxWriter
from pyvox.models import Vox, Model, Voxel, Size, Color

# sometimes Python is horrible
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from briq_api.mesh.briq import BriqData


def to_vox(briqData: BriqData):
    voxels = []
    colors = []
    colorSet = {}
    x0 = None
    y0 = None
    z0 = None
    x1 = None
    y1 = None
    z1 = None
    # Vox is Y-up, so we need to rotate coordinates
    for briq in briqData.briqs:
        col = briq['data']['color']
        if col not in colorSet:
            colorSet[col] = len(colors) + 1
            rgbaCol = [int(col[i:i + 2], 16) for i in (1, 3, 5)]
            colors.append(Color(*rgbaCol, a=255))
        if x0 is None or briq["pos"][0] < x0:
            x0 = briq["pos"][0]
        if y0 is None or briq["pos"][2] < y0:
            y0 = briq["pos"][2]
        if z0 is None or briq["pos"][1] < z0:
            z0 = briq["pos"][1]
        if x1 is None or briq["pos"][0] > x1:
            x1 = briq["pos"][0]
        if y1 is None or briq["pos"][2] > y1:
            y1 = briq["pos"][2]
        if z1 is None or briq["pos"][1] > z1:
            z1 = briq["pos"][1]
    if len(briqData.briqs) == 0:
        x0 = x1 = z0 = z1 = y0 = y1 = 0
    x1 += 1
    y1 += 1
    z1 += 1

    for briq in briqData.briqs:
        voxels.append(Voxel(x=x1 - briq["pos"][0] - 1, y=briq["pos"][2] - y0, z=briq["pos"][1] - z0, c=colorSet[briq['data']['color']]))

    vox = Vox(models=[Model(size=Size(x=x1 - x0, y=y1 - y0, z=z1 - z0), voxels=voxels)], palette=colors)
    return VoxWriter("temp.vox", vox)
