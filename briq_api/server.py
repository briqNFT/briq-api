from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging

from .storage.cloud_storage import CloudStorage, NotFoundException
from .storage.file_storage import FileStorage

from .mesh.briq import BriqData

from . import app_logic

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://realms.localhost:3000",
        "http://localhost:3000",
        "https://briq.construction",
        "https://www.briq.construction",
        "https://realms.briq.construction",
        "https://test-realms.briq.construction",
        "https://sltech.company",
        "https://www.sltech.company",
        "https://test.sltech.company",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from typing import Dict, Any, Tuple
from .storage.storage import get_storage
storage_client = get_storage()

@app.get("/health")
def health():
    return "ok"

@app.head("/store_get/{token_id}")
@app.post("/store_get/{token_id}")
@app.get("/store_get/{token_id}")
async def store_get(token_id: str):
    try:
        data = storage_client.load_json(path=token_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="File not found")
    return {
        "code": 200,
        "token_id": token_id,
        "data": data,
        "name": data['name'] if 'name' in data else '',
        "description": data['description'] if 'description' in data else '',
        "image": data['image'].replace('://briq.construction', '://api.briq.construction') if 'image' in data else '',
        "external_url": data['external_url'] if 'external_url' in data else '',
        "animation_url": data['animation_url'] if 'animation_url' in data else '',
        "background_color": data['background_color'] if 'background_color' in data else '',
    }

import io
from starlette.responses import StreamingResponse

@app.head("/preview/{token_id}")
@app.get("/preview/{token_id}")
@app.head("/preview/{token_id}.png")
@app.get("/preview/{token_id}.png")
async def get_preview(token_id: str):
    try:
        data = storage_client.load_image(path=token_id)
        return StreamingResponse(io.BytesIO(data), media_type="image/png", headers={
            "Cache-Control": f"public, max-age={3600 * 24}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail="File not found")

@app.head("/get_model/{token_id}.{kind}")
@app.get("/get_model/{token_id}.{kind}")
async def get_model(kind: str, token_id: str):
    mime_type = {
        "glb": "model/gltf-binary",
        "vox": "application/octet-stream",
    }
    try:
        data = storage_client.load_bytes(path_including_ext=token_id + '.' + kind)
        return StreamingResponse(io.BytesIO(data), media_type=mime_type[kind], headers={
            "Cache-Control": f"public, max-age={3600 * 24}"
        })
    except (NotFoundException, OSError):
        try:
            data = storage_client.load_json(path=token_id)
            briqData = BriqData().load(data)
            output = None
            if kind == "glb":
                output = b''.join(briqData.to_gltf().save_to_bytes())
                storage_client.store_bytes(path_including_ext=token_id + ".glb", data=output)
            elif kind == "vox":
                output = briqData.to_vox(token_id).to_bytes()
                storage_client.store_bytes(path_including_ext=token_id + ".vox", data=output)
            else:
                raise Exception("Unknown model type " + kind)
            logging.info("Created %(type)s model for %(set)s on the fly.", {"type": kind, "set": token_id})
            return StreamingResponse(io.BytesIO(output), media_type=mime_type[kind], headers={
                "Cache-Control": f"public, max-age={3600 * 24}"
            })
        except Exception as e:
            logging.error(e, exc_info=e)
            raise HTTPException(status_code=500, detail="Error while creating model.")
    except Exception as e:
        logging.error(e, exc_info=e)
        raise HTTPException(status_code=500, detail="Error while fetching model.")

@app.post("/store_list")
@app.get("/store_list")
def store_list():
    return {
        "code": 200,
        "sets": storage_client.list_json()
    }


gallery_items = { "sets": [], "sets_v06": [] }
future_gallery_items = { "sets": [], "sets_v06": [] }
updating_task = None

async def update_gallery_items_unused():
    global future_gallery_items
    global gallery_items
    global updating_task
    future_gallery_items = []

    logger.info("UPDATING GALLERY ITEMS")
    files = storage_client.list_json()

    async def get_set_if_owner(filename: str) -> str:
        set_id = filename.replace(".json", "")
        try:
            owner = 0  #(owner,) = await (await app_logic.get_set_contract()).functions["ownerOf"].call(int(set_id, base=16))
            if owner == 0:
                return ""
            return set_id
        except Exception as err:
            logger.error("Error querying gallery item ", set_id)
            logger.error(err)
            return ""

    # Send some requests in parallel but throttle to avoid problems.
    GROUP = 1
    for i in range(len(files) // GROUP):
        future_gallery_items.append(files[i].replace(".json", ""))
        continue
        futures = []
        for j in range(GROUP):
            if len(files) > i * GROUP + j:
                futures.append(get_set_if_owner(files[i * GROUP + j]))
        ids = await asyncio.gather(*futures)
        for id in ids:
            if len(id) > 0:
                future_gallery_items.append(id)
    logger.info("DONE UPDATING, FOUND %s items", str(len(future_gallery_items)))
    gallery_items = future_gallery_items
    updating_task = None


def parse_gallery_data(storage: CloudStorage):
    try:
        data = storage.bucket.blob("gallery_sets.json").download_as_text()
        data = json.loads(data)
    except Exception as ex:
        logging.exception(ex, exc_info=ex)
        raise
    return data


async def update_gallery_items():
    global future_gallery_items
    global gallery_items
    global updating_task
    future_gallery_items = []

    logger.info("UPDATING GALLERY ITEMS")
    if isinstance(storage_client, FileStorage):
        future_gallery_items = {
            "items": [x.replace(".json", "") for x in storage_client.list_json()],
            "items_vO6": []
        }
    else:
        future_gallery_items = parse_gallery_data(storage_client)
    logger.info("DONE UPDATING, FOUND %(items)s items", {"items": len(future_gallery_items['items'])})
    gallery_items = future_gallery_items
    updating_task = None

@app.on_event("startup")
async def startup_event():
    global updating_task
    updating_task = asyncio.create_task(update_gallery_items())
    # asyncio.create_task(set_contract_promise)

@app.get("/gallery_items")
async def get_gallery_items():
    global updating_task
    if updating_task is None or updating_task.done():
        updating_task = asyncio.create_task(update_gallery_items())
    return {
        "code": 200,
        "version": 2,
        "sets": gallery_items['items'] if len(gallery_items) > 0 else future_gallery_items['items'],
        "sets_v06": gallery_items['items_v06'] if len(gallery_items) > 0 else future_gallery_items['items_v06']
    }

import base64

from PIL import Image

@app.post("/store_set")
async def store_set(set: app_logic.StoreSetRequest):
    #if False and CUSTOM_SET_ADDRESS == "":
    #    (owner,) = await (await get_set_contract()).functions["ownerOf"].call(int(set.token_id, base=16))
    #    # NB: this is a data-race, as there may be pending transactions, but we'll ignore that for now.
    #    if owner != 0:
    #        # Check that we are the owner.
    #        # TODO: add ABI here.
    #        contract = await Contract.from_address(set.owner, client)
    #        (is_valid,) = await contract.functions["is_valid_signature"].call(hash=int(set.message_hash, base=16), sig=set.signature)
    #        if not is_valid:
    #            raise HTTPException(status_code=403, detail="Wrong signature for the public key.")
    #        if owner != set.owner:
    #            raise HTTPException(status_code=403, detail="You are not the owner of the NFT.")

    if len(set.image_base64) > 0:
        HEADER = b'data:image/png;base64,'
        if set.image_base64[0:len(HEADER)] != HEADER:
            raise HTTPException(status_code=403, detail="Only base-64 encoded PNGs are accepted.")
        if len(set.image_base64) > 1000 * 1000:
            raise HTTPException(status_code=403, detail="Image is too heavy, max size is 1MB")

        png_data = base64.decodebytes(set.image_base64[len(HEADER):])
        image = Image.open(io.BytesIO(png_data))

        if image.width > 1000 or image.height > 1000 or image.width < 10 or image.height < 10:
            raise HTTPException(status_code=403, detail="Image is too large, acceptable size range from 10x10 to 1000x1000")

        storage_client.store_image(path=set.token_id, data=png_data)

    try:
        # Attempt converting to GLTF but don't store it before it's first accessed.
        # Further, don't try .vox because that can fail somewhat spuriously.
        briqData = BriqData().load(set.data)
        briqData.to_gltf()
        #storage_client.store_bytes(path_including_ext=set.token_id + ".glb", data=b''.join(briqData.to_gltf().save_to_bytes()))
        #storage_client.store_bytes(path_including_ext=set.token_id + ".vox", data=briqData.to_vox(set.token_id).to_bytes())
    except Exception as err:
        logging.warning("Error when converting the set data to 3D models. Set data: %(setdata)s", {"setdata": set.data}, exc_info=err)
        raise HTTPException(status_code=500, detail="Error when converting the set data to 3D models. Details: \n" + str(err))

    # ERC 721 metadata compliance
    set.data["image"] = f"https://api.briq.construction/preview/{set.token_id}.png"
    set.data["description"] = "A set made of briqs"
    set.data["external_url"] = f"https://briq.construction/share?set_id={set.token_id}&network=testnet&version=2"
    if 'recommendedSettings' in set.data:
        set.data['background_color'] = set.data['recommendedSettings']['backgroundColor'][1:]
    set.data["animation_url"] = f"https://api.briq.construction/get_model/{set.token_id}.glb"

    # Will overwrite, which is OK since we checked the owner.
    try:
        storage_client.store_json(path=set.token_id, data=set.data)
    except Exception as err:
        logging.error("Error exporting JSON", exc_info=err)
        raise HTTPException(status_code=500, detail="Error saving JSON")

    logging.info("Stored new set %(token_id)s for %(owner)s", {
        "token_id": set.token_id,
        "owner": set.owner
    })

    # Run the webhook job asynchronously.
    app_logic.store_set(set)

    return {
        "code": 200,
        "value": set.token_id
    }
