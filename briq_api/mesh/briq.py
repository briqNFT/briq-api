import json
from typing import Dict, Sequence

from .vox import to_vox

from .gltf import to_gltf, Primitive, Material


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
        byMaterial = {}

        for briq in self.briqs:
            if briq['data']['material'] not in byMaterial:
                byMaterial[briq['data']['material']] = {briq['data']['color']: []}
            if briq['data']['color'] not in byMaterial[briq['data']['material']]:
                byMaterial[briq['data']['material']][briq['data']['color']] = []
            byMaterial[briq['data']['material']][briq['data']['color']].append(briq['pos'])

        primitives = []
        for mat in byMaterial:
            for col in byMaterial[mat]:
                outPoints = []
                outTriangles = []
                SIZE = 0.5
                for (index, briqPos) in enumerate(byMaterial[mat][col]):
                    # Bottom: 0 1 5 4
                    # Top: 2 3 7 6
                    outPoints.append([briqPos[0] - SIZE, briqPos[1] - SIZE, briqPos[2] - SIZE])
                    outPoints.append([briqPos[0] - SIZE, briqPos[1] - SIZE, briqPos[2] + SIZE])
                    outPoints.append([briqPos[0] - SIZE, briqPos[1] + SIZE, briqPos[2] - SIZE])
                    outPoints.append([briqPos[0] - SIZE, briqPos[1] + SIZE, briqPos[2] + SIZE])
                    outPoints.append([briqPos[0] + SIZE, briqPos[1] - SIZE, briqPos[2] - SIZE])
                    outPoints.append([briqPos[0] + SIZE, briqPos[1] - SIZE, briqPos[2] + SIZE])
                    outPoints.append([briqPos[0] + SIZE, briqPos[1] + SIZE, briqPos[2] - SIZE])
                    outPoints.append([briqPos[0] + SIZE, briqPos[1] + SIZE, briqPos[2] + SIZE])

                    outTriangles.append([index * 8 + 0, index * 8 + 1, index * 8 + 2])
                    outTriangles.append([index * 8 + 2, index * 8 + 1, index * 8 + 3])

                    outTriangles.append([index * 8 + 2, index * 8 + 4, index * 8 + 0])
                    outTriangles.append([index * 8 + 6, index * 8 + 4, index * 8 + 2])

                    outTriangles.append([index * 8 + 1, index * 8 + 0, index * 8 + 5])
                    outTriangles.append([index * 8 + 5, index * 8 + 0, index * 8 + 4])

                    outTriangles.append([index * 8 + 2, index * 8 + 3, index * 8 + 7])
                    outTriangles.append([index * 8 + 2, index * 8 + 7, index * 8 + 6])

                    outTriangles.append([index * 8 + 7, index * 8 + 3, index * 8 + 5])
                    outTriangles.append([index * 8 + 5, index * 8 + 3, index * 8 + 1])

                    outTriangles.append([index * 8 + 6, index * 8 + 7, index * 8 + 5])
                    outTriangles.append([index * 8 + 4, index * 8 + 6, index * 8 + 5])
                # Mesh optimisation (NB: this algorithm is rather dumb)
                # - First remove identical points
                # - Then any face that's in the mesh twice must be an 'inner' face, and we can remove it.
                # NB: because I'm using different primitives for each color, different colors will keep full cubes,
                # which seems fine enough.
                firstIdx = {}
                matchIdx = {}
                actualPoints = []
                for i, point in enumerate(outPoints):
                    pt = '_'.join([str(p) for p in point])
                    if pt not in firstIdx:
                        firstIdx[pt] = len(actualPoints)
                        actualPoints.append(point)
                    matchIdx[i] = firstIdx[pt]
                outTriangles = [tuple([matchIdx[t] for t in triangle]) for triangle in outTriangles]
                outPoints = actualPoints

                matcha = {}
                for triangle in outTriangles:
                    pt = '_'.join([str(i) for i in sorted(triangle)])
                    if pt not in matcha:
                        matcha[pt] = 0
                    matcha[pt] += 1
                out = []
                for triangle in outTriangles:
                    pt = '_'.join([str(i) for i in sorted(triangle)])
                    if matcha[pt] == 1:
                        out.append(triangle)
                outTriangles = out

                primitives.append(Primitive(outPoints, outTriangles, Material(f"{mat}_{col}", col)))
        return to_gltf(primitives)
