from typing import List, Sequence, Tuple
import numpy as np
import pygltflib

from dataclasses import dataclass


@dataclass
class Material:
    name: str
    material: str
    color: str  # as "#ffaa00"


@dataclass
class Primitive:
    points: List[Tuple[float, float, float]]
    triangles: List[Tuple[int, int, int]]
    material: Material

def parse_material(mat, col, byMaterial, primitives):
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

    primitives.append(Primitive(outPoints, outTriangles, Material(f"{mat}_{col}", mat, col)))

def to_primitives(briqs: Sequence):
    byMaterial = {}

    for briq in briqs:
        if briq['data']['material'] not in byMaterial:
            byMaterial[briq['data']['material']] = {briq['data']['color']: []}
        if briq['data']['color'] not in byMaterial[briq['data']['material']]:
            byMaterial[briq['data']['material']][briq['data']['color']] = []
        byMaterial[briq['data']['material']][briq['data']['color']].append(briq['pos'])

    primitives = []
    for mat in byMaterial:
        for col in byMaterial[mat]:
            parse_material(mat, col, byMaterial, primitives)

    return primitives

def to_gltf(briqs: Sequence):
    prims = to_primitives(briqs)

    primitives = []
    accessors = []
    bufferViews = []
    materials = []

    blobs = b""
    totalBufferOffset = 0

    for (i, primitive) in enumerate(prims):

        rgbaCol = [int(primitive.material.color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        if primitive.material.material == "0x3":
            materials.append(pygltflib.Material(
                name=primitive.material.name,
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(baseColorFactor=rgbaCol + [0.5],),
                alphaMode="BLEND",
            ))
        elif primitive.material.material == "0x4":
            materials.append(pygltflib.Material(
                name=primitive.material.name,
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                    baseColorFactor=rgbaCol + [1.0],
                    metallicFactor=0.5,
                    roughnessFactor=0.15,
                ),
            ))
        elif primitive.material.material == "0x5":
            materials.append(pygltflib.Material(
                name=primitive.material.name,
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                    baseColorFactor=rgbaCol + [1.0],
                ),
                emissiveFactor=rgbaCol,
            ))
        else:
            materials.append(pygltflib.Material(
                name=primitive.material.name,
                pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(baseColorFactor=rgbaCol + [1]),
                alphaCutoff=None,
            ))

        points = np.array(primitive.points, dtype="float32")
        triangles = np.array(primitive.triangles, dtype="uint32")
        triangles_binary_blob = triangles.flatten().tobytes()
        points_binary_blob = points.tobytes()
        primitives.append(pygltflib.Primitive(
            attributes=pygltflib.Attributes(POSITION=i * 2 + 1),
            indices=i * 2,
            material=i
        ))
        accessors.append(pygltflib.Accessor(
            bufferView=i * 2,
            componentType=pygltflib.UNSIGNED_INT,
            count=triangles.size,
            type=pygltflib.SCALAR,
            max=[int(triangles.max())],
            min=[int(triangles.min())],
        ))
        accessors.append(pygltflib.Accessor(
            bufferView=i * 2 + 1,
            componentType=pygltflib.FLOAT,
            count=len(points),
            type=pygltflib.VEC3,
            max=points.max(axis=0).tolist(),
            min=points.min(axis=0).tolist(),
        ))
        bufferViews.append(pygltflib.BufferView(
            buffer=0,
            byteOffset=totalBufferOffset,
            byteLength=len(triangles_binary_blob),
            target=pygltflib.ELEMENT_ARRAY_BUFFER,
        ))
        totalBufferOffset += len(triangles_binary_blob)
        bufferViews.append(pygltflib.BufferView(
            buffer=0,
            byteOffset=totalBufferOffset,
            byteLength=len(points_binary_blob),
            target=pygltflib.ARRAY_BUFFER,
        ))
        totalBufferOffset += len(points_binary_blob)
        blobs += triangles_binary_blob + points_binary_blob

    gltf = pygltflib.GLTF2(
        scene=0,
        scenes=[pygltflib.Scene(nodes=[0])],
        nodes=[pygltflib.Node(mesh=0)],
        meshes=[pygltflib.Mesh(primitives=primitives)],
        materials=materials,
        accessors=accessors,
        bufferViews=bufferViews,
        buffers=[
            pygltflib.Buffer(
                byteLength=totalBufferOffset
            )
        ],
    )
    gltf.set_binary_blob(blobs)
    return gltf
