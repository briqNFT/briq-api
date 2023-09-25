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
from PIL import Image
from pydantic import BaseModel
from typing import Any, List, Optional, Tuple

from briq_api.api.theme import get_all_theme_object_ids
from briq_api.auth import IsAdminDep
from briq_api.chain.networks import get_gateway_client, get_network_metadata
from briq_api.set_identifier import SetRID
from briq_api.set_indexer.create_set_metadata import create_booklet_metadata, create_set_metadata
from briq_api.stores import file_storage, theme_storage
from briq_api.mesh.briq import BriqData

from briq_protocol.binomial_ifs import generate_shape_check, generate_binary_search_function, ShapeItem, HEADER

from starknet_py.contract import Contract
from starknet_py.utils.typed_data import TypedData

from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger), dependencies=[IsAdminDep])

STARKNET_COMPILE_PATH = os.getenv("STARKNET_COMPILE_PATH") or "starknet-compile"

COLLECTIONS_METADATA = {
    "ducks_everywhere": {
        "name": "Ducks Everywhere",
        "artist": "OutSmth",
    }
}


@router.get("/admin/authorized")
def check_authorized():
    return "ok"


class StoreThemeObjectRequest(BaseModel):
    data: dict[str, Any]
    preview_base64: bytes
    booklet_base64: bytes
    background_color: Optional[str] = None


async def generate_object_data(set: StoreThemeObjectRequest, chain_id: str, theme_id: str, object_id: str):
    metadata = create_set_metadata(
        token_id="",
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
    glb_briq_by_level, glb_current_briqs = generate_layered_glb(data)

    booklet_metadata = create_booklet_metadata(
        theme_id=theme_id,
        booklet_id=object_id,
        theme_name=COLLECTIONS_METADATA[theme_id]["name"],
        theme_artist=COLLECTIONS_METADATA[theme_id]["artist"],
        theme_date=datetime.now().strftime("%Y-%m-%d"),
        name=set.data["name"],
        description=set.data["description"],
        network=chain_id,
        briqs=set.data["briqs"],
        nb_steps=len(glb_briq_by_level),
        step_progress_data=[len(level) for level in glb_briq_by_level],
    )

    @dataclass
    class Output:
        metadata: dict
        booklet_metadata: dict
        glb_briq_by_level: list[list[dict[str, Any]]]
        glb_current_briqs: list[list[dict[str, Any]]]

    return Output(metadata=metadata,
                  booklet_metadata=booklet_metadata,
                  glb_briq_by_level=glb_briq_by_level,
                  glb_current_briqs=glb_current_briqs)


def gen_lower_res_image(img: bytes):
    image = Image.open(io.BytesIO(img))
    # If there is a background color, presumably the image is not transparent,
    # so it doesn't really matter if we paste it on a white background or not.
    bg = Image.new("RGBA", image.size, (255, 255, 255, 255))
    try:
        bg.paste(image, mask=image.getchannel('A'))
    except:
        bg.paste(image)
    output = io.BytesIO()
    bg.convert('RGB').save(output, format='JPEG', quality=60)
    return output.getvalue()



@router.head("/admin/store_theme_object/{chain_id}/{theme_id}/{object_id}")
@router.post("/admin/store_theme_object/{chain_id}/{theme_id}/{object_id}")
async def store_theme_object(set: StoreThemeObjectRequest, chain_id: str, theme_id: str, object_id: str):
    raise_if_replacing_data(chain_id, theme_id, object_id)

    # In this mode, we need to ensure that the object already exists, we're just filling in data.
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    if f"{theme_id}/{object_id}" not in booklet_spec:
        raise HTTPException(status_code=400, detail="Object does not exist: " + booklet_spec[f"{theme_id}/{object_id}"])

    data = await generate_object_data(set, chain_id, theme_id, object_id)
    booklet_metadata, _ = data.booklet_metadata, data.metadata

    # Convert those beforehand in case of errors
    preview = decode_base64(set.preview_base64)
    booklet = decode_base64(set.booklet_base64)
    preview_lower = gen_lower_res_image(preview)
    booklet_lower = gen_lower_res_image(booklet)

    PATH = f"genesis_themes/{theme_id}/{object_id}"
    file_storage.get_backend(chain_id).store_json(PATH + "/metadata_booklet.json", booklet_metadata)
    file_storage.get_backend(chain_id).store_bytes(PATH + "/cover.png", preview)
    file_storage.get_backend(chain_id).store_bytes(PATH + "/booklet_cover.png", booklet)

    file_storage.get_backend(chain_id).store_bytes(PATH + "/cover.jpg", preview_lower)
    file_storage.get_backend(chain_id).store_bytes(PATH + "/booklet_cover.jpg", booklet_lower)

    briq_by_level, current_briqs = data.glb_briq_by_level, data.glb_current_briqs
    glb_data = BriqData()

    i = 0
    for lev in briq_by_level:
        glb_data.briqs = lev
        file_storage.get_backend(chain_id).store_bytes(f"{PATH}/step_{i}.glb", b''.join(glb_data.to_gltf(separate_any_color=True).save_to_bytes()))
        i += 1

    i = 0
    for lev in current_briqs:
        glb_data.briqs = lev
        file_storage.get_backend(chain_id).store_bytes(f"{PATH}/step_level_{i}.glb", b''.join(glb_data.to_gltf(separate_any_color=True).save_to_bytes()))
        i += 1

    theme_storage.reset_cache()


class CompileShapeContractRequest(BaseModel):
    shapes_by_attribute_id: dict[str, List[Any]]


@router.head("/admin/compile_shape_contract/")
@router.post("/admin/compile_shape_contract/")
async def store_theme_object(shapes: CompileShapeContractRequest):
    ids = {}
    for attr_id in shapes.shapes_by_attribute_id:
        items = []
        for shape in shapes.shapes_by_attribute_id[attr_id]:
            items.append(ShapeItem(
                shape['pos'][0],
                shape['pos'][1],
                shape['pos'][2],
                shape['data']['color'].lower(),
                int(shape['data']['material'], 16)
            ))
        ids[int(attr_id, 16)] = generate_shape_check(items)
    sorted_ids = list(ids.keys())
    sorted_ids.sort()
    code = HEADER + generate_binary_search_function(sorted_ids, lambda x: ids[x]) + "\n}"

    # Call starknet-compile via subprocess
    with tempfile.TemporaryDirectory() as tmpdirname:
        code_path = os.path.join(tmpdirname, "code.cairo")
        with open(code_path, "w") as f:
            f.write(code)

        process = await asyncio.create_subprocess_exec(
            STARKNET_COMPILE_PATH,
            code_path, "--single-file", os.path.join(tmpdirname, "code.json"),
        )
        await process.communicate()

        if process.returncode != 0:
            raise HTTPException(status_code=400, detail="Compilation failed")

        with open(os.path.join(tmpdirname, "code.json")) as f:
            return f.read()


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
    contract_json, class_hash = (0, 1) # await loop.run_in_executor(thread_pool, compile_shape_contract, cr.serial_number, data)
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
    if chain_id == "starknet-mainnet":
        if int(owner, 16) not in {
            0x03eF5B02BCC5D30F3f0d35D55f365E6388fE9501ECA216cb1596940Bf41083E2,
            0x059df66Af2E0E350842b11eA6b5a903b94640C4ff0418b04cCedCC320f531a08,
            0x02ef9325a17d3ef302369fd049474bc30bfeb60f59cca149daa0a0b7bcc278f8  # OutSmth
        }:
            raise HTTPException(status_code=400, detail="You are not authorized to call this function")
    elif int(owner, 16) not in {
        0x069cfa382ea9d2e81aea2d868b0dd372f70f523fa49a765f4da320f38f9343b3,
        0x059df66Af2E0E350842b11eA6b5a903b94640C4ff0418b04cCedCC320f531a08,  # sylve
        0x03eF5B02BCC5D30F3f0d35D55f365E6388fE9501ECA216cb1596940Bf41083E2,
        0x00c658ff012e337f56af9bf8d986e544092e6b81959218be9c6ae69b15fcf6cb,  # OutSmth
    }:
        raise HTTPException(status_code=400, detail="You are not authorized to call this function")

    contract = Contract(owner, [{
            "name": "is_valid_signature",
            "type": "function",
            "inputs": [
            {
                "name": "hash",
                "type": "felt"
            },
            {
                "name": "signature_len",
                "type": "felt"
            },
            {
                "name": "signature",
                "type": "felt*"
            }
            ],
            "outputs": [
            {
                "name": "is_valid",
                "type": "felt"
            }
            ],
            "stateMutability": "view"
        },
        {
            "name": "isValidSignature",
            "type": "function",
            "inputs": [
            {
                "name": "hash",
                "type": "felt"
            },
            {
                "name": "signature_len",
                "type": "felt"
            },
            {
                "name": "signature",
                "type": "felt*"
            }
            ],
            "outputs": [
            {
                "name": "isValid",
                "type": "felt"
            }
            ],
            "stateMutability": "view"
        },
    ], get_gateway_client(chain_id))

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

    booklets = list(get_all_theme_object_ids(chain_id, auction_theme).keys())

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

    #run_validation(set, chain_id, auction_theme)

    @dataclass
    class Output:
        serial: int
        metadata: dict
        booklet_metadata: dict

    return Output(metadata=metadata, booklet_metadata=booklet_metadata, serial=serial)


def raise_if_replacing_data(chain_id: str, theme_id: str, object_id: str):
    PATH = f"genesis_themes/{theme_id}/{object_id}"
    if file_storage.get_backend(chain_id).has_path(PATH + "/metadata_booklet.json"):
        raise HTTPException(status_code=400, detail="Booklet already exists")
    if file_storage.get_backend(chain_id).has_path(PATH + "/cover.png"):
        raise HTTPException(status_code=400, detail="Cover already exists")
    if file_storage.get_backend(chain_id).has_path(PATH + "/booklet_cover.png"):
        raise HTTPException(status_code=400, detail="Booklet cover already exists")


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
