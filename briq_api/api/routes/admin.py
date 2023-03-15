import base64
import io
import logging
import os
import re
import tempfile
import concurrent.futures
import asyncio
from dataclasses import dataclass
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pathlib import Path
from PIL import Image
from pydantic import BaseModel
from typing import Any, List, Optional, Tuple

from briq_api.api.theme import list_booklets_of_theme
from briq_api.chain.networks import get_gateway_client, get_network_metadata
from briq_api.set_identifier import SetRID
from briq_api.set_indexer.create_set_metadata import create_booklet_metadata, create_set_metadata
from briq_api.stores import file_storage, theme_storage
from briq_api.mesh.briq import BriqData

from starknet_py.contract import Contract
from starknet_py.utils.typed_data import TypedData


from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger))


class NewNFTRequest(BaseModel):
    token_id: str
    data: dict[str, Any]
    owner: str
    signature: Tuple[int, int]
    preview_base64: bytes
    booklet_base64: bytes
    background_color: Optional[str] = None


@router.post("/admin/{chain_id}/{auction_theme}/validate_new_nft")
async def validate_new_nft(set: NewNFTRequest, chain_id: str, auction_theme: str):
    if auction_theme != "ducks_everywhere":
        raise HTTPException(status_code=400, detail="Invalid auction theme")

    # TODO:
    # - Check token_id is not already used

    await check_signature(chain_id, set.owner, set.token_id, set.signature)

    data = await generate_data(set, chain_id, auction_theme)
    serial, booklet_metadata, metadata = data.serial, data.booklet_metadata, data.metadata

    return {
        "set_meta": metadata,
        "booklet_meta": booklet_metadata,
        "serial_number": serial,
    }


class CompileRequest(BaseModel):
    data: dict[str, Any]
    serial_number: int
    owner: str
    signature: Tuple[int, int]
    token_id: str


@router.post("/admin/{chain_id}/{auction_theme}/compile_shape")
async def compile_shape(cr: CompileRequest, chain_id: str):
    await check_signature(chain_id, cr.owner, cr.token_id, cr.signature)

    data = BriqData()
    data.load(cr.data)

    loop = asyncio.get_event_loop()
    thread_pool = concurrent.futures.ThreadPoolExecutor(1)
    contract_json, class_hash = await loop.run_in_executor(thread_pool, compile_shape_contract, cr.serial_number, data)
    return {
        "contract_json": contract_json,
        "class_hash": class_hash,
    }


@router.post("/admin/{chain_id}/{auction_theme}/mint_new_nft")
async def mint_new_nft(set: NewNFTRequest, chain_id: str, auction_theme: str):
    if auction_theme != "ducks_everywhere":
        raise HTTPException(status_code=400, detail="Invalid auction theme")

    await check_signature(chain_id, set.owner, set.token_id, set.signature)

    data = await generate_data(set, chain_id, auction_theme)
    serial, booklet_metadata, metadata = data.serial, data.booklet_metadata, data.metadata

    # This doesn't reuse the API function because it skips the validation.
    rid = SetRID(chain_id=chain_id, token_id=set.token_id)
    file_storage.store_set_metadata(rid, metadata)

    PATH = f"genesis_themes/{auction_theme}/{set.data['name']}"
    file_storage.get_backend(chain_id).store_json(PATH + "/metadata_booklet.json", booklet_metadata)
    file_storage.get_backend(chain_id).store_bytes(PATH + "/cover.png", decode_base64(set.preview_base64))
    file_storage.get_backend(chain_id).store_bytes(PATH + "/booklet_cover.png", decode_base64(set.booklet_base64))

    # No existence check for those, subsumed by the HQ ones.
    image = Image.open(io.BytesIO(decode_base64(set.preview_base64)))
    # If there is a background color, presumably the image is not transparent,
    # so it doesn't really matter if we paste it on a white background or not.
    bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
    try:
        bg.paste(image, mask=image.getchannel('A'))
    except:
        bg.paste(image)
    output = io.BytesIO()
    bg.convert('RGB').save(output, format='JPEG', quality=60)
    preview_bytes = output.getvalue()
    file_storage.get_backend(chain_id).store_bytes(PATH + "/cover.jpg", preview_bytes)
    file_storage.store_set_preview(rid, preview_bytes)

    image = Image.open(io.BytesIO(decode_base64(set.booklet_base64)))
    # If there is a background color, presumably the image is not transparent,
    # so it doesn't really matter if we paste it on a white background or not.
    bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
    try:
        bg.paste(image, mask=image.getchannel('A'))
    except:
        bg.paste(image)
    output = io.BytesIO()
    bg.convert('RGB').save(output, format='JPEG', quality=50)
    file_storage.get_backend(chain_id).store_bytes(PATH + "/booklet_cover.jpg", output.getvalue())

    data = BriqData()
    data.load(metadata)
    briq_by_level, current_briqs = generate_layered_glb(data)

    i = 0
    for lev in briq_by_level:
        data.briqs = lev
        file_storage.get_backend(chain_id).store_bytes(f"{PATH}/step_{i}.glb", b''.join(data.to_gltf(separate_any_color=True).save_to_bytes()))
        i += 1

    i = 0
    for lev in current_briqs:
        data.briqs = lev
        file_storage.get_backend(chain_id).store_bytes(f"{PATH}/step_level_{i}.glb", b''.join(data.to_gltf(separate_any_color=True).save_to_bytes()))
        i += 1

    # Update booklet spec
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    # Backup the file
    theme_storage.get_backend(chain_id).backup_file(theme_storage.booklet_path())

    duck_collection_id = 3
    booklet_spec[f"{auction_theme}/{set.data['name']}"] = hex(duck_collection_id + 2**192 * serial)
    # TODO check properly serial
    theme_storage.get_backend(chain_id).store_json(theme_storage.booklet_path(), booklet_spec)
    # Reset the cache, otherwise for some time the old file keeps being used (it's cached)
    # NB -> if there are several instances of the API, this won't clear all of them.
    theme_storage.reset_cache()


async def check_signature(chain_id: str, owner: str, token_id: str, signature: Tuple[int, int]):
    if int(owner, 16) not in {
        0x069cfa382ea9d2e81aea2d868b0dd372f70f523fa49a765f4da320f38f9343b3,
        0x059df66Af2E0E350842b11eA6b5a903b94640C4ff0418b04cCedCC320f531a08,  # sylve
        0x03eF5B02BCC5D30F3f0d35D55f365E6388fE9501ECA216cb1596940Bf41083E2,
        0x00c658ff012e337f56af9bf8d986e544092e6b81959218be9c6ae69b15fcf6cb,  # OutSmth
    }:
        raise HTTPException(status_code=400, detail="You are not authorized to call this function")

    contract = await Contract.from_address(
        address=owner,
        client=get_gateway_client(chain_id),
        proxy_config=True,
    )

    # Or if just a message hash is needed
    data = TypedData.from_dict({
        "types": {
            "StarkNetDomain": [
                {"name": 'name', "type": 'felt'},
                {"name": 'version', "type": 'felt'},
                {"name": 'chainId', "type": 'felt'},
            ],
            "Message": [
                {
                    "name": 'tokenId',
                    "type": 'felt',
                },
            ],
        },
        "domain": {
            "name": 'briq', "version": "1", "chainId": get_network_metadata(chain_id).chain_id
        },
        "primaryType": 'Message',
        "message": {
            "tokenId": int(token_id, 16),
        },
    })
    message_hash = data.message_hash(int(owner, 16))
    try:
        (value,) = await contract.functions["is_valid_signature"].call(
            message_hash, signature
        )
        if value != 1:
            raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")


async def generate_data(set: NewNFTRequest, chain_id: str, auction_theme: str):
    metadata = create_set_metadata(
        token_id=set.token_id,
        name=set.data["name"],
        description=set.data["description"],
        network=chain_id,
        briqs=set.data["briqs"],
    )
    if set.background_color:
        metadata["background_color"] = set.background_color
        # Check format matches 6 hex values without preceding #
        if not re.match(r"^[0-9a-fA-F]{6}$", set.background_color):
            raise HTTPException(status_code=400, detail="Invalid background color")

    data = BriqData()
    data.load(metadata)
    briq_by_level, current_briqs = generate_layered_glb(data)

    booklets = list_booklets_of_theme(chain_id, auction_theme)

    booklet_metadata = create_booklet_metadata(
        theme_id=auction_theme,
        booklet_id=set.data["name"],
        theme_name="Ducks Everywhere",
        theme_artist="OutSmth",
        theme_date=datetime.now().strftime("%Y-%m-%d"),
        name=set.data["name"],
        description=set.data["description"],
        network=chain_id,
        briqs=set.data["briqs"],
        nb_steps=len(briq_by_level),
        step_progress_data=[len(level) for level in briq_by_level],
    )

    serial = len(booklets) + 1

    run_validation(set, chain_id, auction_theme)

    @dataclass
    class Output:
        serial: int
        metadata: dict
        booklet_metadata: dict

    return Output(metadata=metadata, booklet_metadata=booklet_metadata, serial=serial)


def run_validation(set: NewNFTRequest, chain_id: str, auction_theme: str):
    # TODO move to validate
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    if f"{auction_theme}/{set.data['name']}" in booklet_spec:
        raise HTTPException(status_code=400, detail="Booklet already exists")

    if file_storage.get_backend(chain_id).has_path(f"sets/{chain_id}/{set.token_id}_metadata.json"):
        raise HTTPException(status_code=400, detail="Set JSON already exists")

    PATH = f"genesis_themes/{auction_theme}/{set.data['name']}"
    if file_storage.get_backend(chain_id).has_path(PATH + "/metadata_booklet.json"):
        raise HTTPException(status_code=400, detail="Booklet already exists")
    if file_storage.get_backend(chain_id).has_path(PATH + "/cover.png"):
        raise HTTPException(status_code=400, detail="Cover already exists")
    if file_storage.get_backend(chain_id).has_path(PATH + "/booklet_cover.png"):
        raise HTTPException(status_code=400, detail="Booklet cover already exists")


from starkware.starknet.compiler.compile import compile_starknet_files
from briq_protocol.generate_shape import generate_shape_code
from briq_protocol.shape_utils import compress_shape_item
import briq_protocol
from starkware.starknet.core.os.class_hash import compute_class_hash

def compile_shape_contract(serial_num: int, data: BriqData):
    shape_data = []
    for briq in data.briqs:
        int_mat = int(briq['data']['material'], 16)
        shape_data.append(('any_color_any_material' if 'any_color' in briq['data'] else briq['data']['color'], int_mat, *briq['pos']))
    shape_data.sort(key=lambda x: compress_shape_item('#000000', 1, x[2], x[3], x[4])[1])
    data_code = generate_shape_code([(shape_data, [])])
    # Compile the contract by setting up an env in which the data is our higher-priority temp folder.
    with tempfile.TemporaryDirectory() as tmpdirname:
        Path(tmpdirname + '/contracts/shape').mkdir(parents=True, exist_ok=True)
        with open(os.path.join(tmpdirname, "contracts/shape/data_ducks.cairo"), "w") as f:
            f.write(data_code)
        path = os.path.dirname(briq_protocol.__file__)
        with open(os.path.join(path, "contracts/shape/shape_store_ducks.cairo"), "r") as f:
            shape_store = f.read()
        with open(os.path.join(tmpdirname, "contracts/shape/shape_store_ducks.cairo"), "w") as f:
            # robust AF
            f.write(shape_store.replace(
                '(global_index - DUCKS_COLLECTION) / (2 ** 192) - 1',
                f'(global_index - DUCKS_COLLECTION) / (2 ** 192) - {serial_num}')
            )
        compile = compile_starknet_files(
            files=[os.path.join(tmpdirname, "contracts/shape/shape_store_ducks.cairo")],
            cairo_path=[tmpdirname, path],
            debug_info=False,
            disable_hint_validation=False
        )
    return compile.dumps(), hex(compute_class_hash(compile))


def decode_base64(image_base64: bytes):
    HEADER = b'data:image/png;base64,'
    if image_base64[0:len(HEADER)] != HEADER:
        raise Exception("Only base-64 encoded PNGs are accepted.")
    #if len(image_base64) > 5000 * 1000:
    #    raise Exception("Image is too heavy, max size is 5MB")

    png_data = base64.decodebytes(image_base64[len(HEADER):])
    #image = Image.open(io.BytesIO(png_data))

    #if image.width > 2000 or image.height > 2000 or image.width < 10 or image.height < 10:
    #    raise Exception("Image is too large, acceptable size range from 10x10 to 2000x2000")

    return png_data


# Print a layer-by-layer set of GLB files.
def generate_layered_glb(data: BriqData):
    total_briqs = data.briqs

    briq_by_level: List[List[dict[str, Any]]] = []
    current_briqs: List[List[dict[str, Any]]] = []
    i = 0
    while True:
        briq_by_level.append([])
        current_briqs.append([])
        found = False
        for briq in total_briqs:
            if briq['pos'][1] == i:
                found = True
                current_briqs[-1].append(briq)
            if briq['pos'][1] <= i:
                briq_by_level[-1].append(briq)
        i += 1
        if not found:
            briq_by_level.pop()
            break

    return briq_by_level, current_briqs
