# Briq API

Python backend for the briq DAPP.

## Setup

1. Create a python VirtualEnv
2. `pip3 install -r requirements.txt`
3. `pip3 install -e .`

#### Running tests
`pytest`

## API Documentation

#### JSON Metadata / Token URI
GET `https://api.briq.construction/store_get/[set_id]` where set_id is `0xCAFE1234`...

This returns a JSON payload containing the set metadata, matching the NFT Token URI

#### Image preview
GET `https://api.briq.construction/preview/[set_id]` where set_id is `0xCAFE1234`...
This returns the PNG image preview of the set.

#### 3D Model
GET `https://api.briq.construction/get_model/[set_id].[format]` where set_id is `0xCAFE1234` & format is one of `.vox`, `.glb`
This returns the 3D model in the corresponding format.
Querying `.vox` will return a [MagicaVoxel](https://ephtracy.github.io/) .vox file, which is compatible with most voxel-based tools.
Querying `.glb` will return a BInary GLTF file, which can be imported in most 3D editors and viewers like https://gltf-viewer.donmccurdy.com/.

