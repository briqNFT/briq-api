# Briq API

Python backend for the briq Dapp.

## Setup

1. Install poetry (https://python-poetry.org/docs/#installation)
2. `poetry update`

You may need to prefix with ```CFLAGS=-I`brew --prefix gmp`/include LDFLAGS=-L`brew --prefix gmp`/lib``` if you're on an M1 mac because GMP is apparently no longer provided by macOS. This requires you to install gmp via homebrew first: `brew install gmp`.

#### Running tests
`poetry run pytest`


#### Running the server locally

`scripts/run-server.sh` will start the server in debug configuration.
You will also need to run the docker-compose for the mongoDB backend fo apibara: `cd scripts && docker-compose up`.
Finally, the indexer service can be run using `scripts/indexer.sh`.

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

