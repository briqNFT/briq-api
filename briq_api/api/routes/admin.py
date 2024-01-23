import base64
import io
import logging
import os
import re
import tempfile
import asyncio
from dataclasses import dataclass
from datetime import datetime
from time import time
from fastapi import APIRouter, HTTPException
from PIL import Image
from pydantic import BaseModel
from typing import Any, List, Optional
from briq_api.api import boxes

from briq_api.auth import IsAdminDep
from briq_api.chain.networks import get_network_metadata
from briq_api.config import ENV
from briq_api.set_indexer.create_set_metadata import create_booklet_metadata, create_set_metadata
from briq_api.stores import file_storage, theme_storage
from briq_api.mesh.briq import BriqData

from briq_protocol.binomial_ifs import generate_shape_check, generate_binary_search_function, ShapeItem, HEADER
from briq_protocol.gen_shape_check import ANY_MATERIAL_ANY_COLOR


from .common import ExceptionWrapperRoute

logger = logging.getLogger(__name__)

router = APIRouter(route_class=ExceptionWrapperRoute(logger), dependencies=[IsAdminDep])

STARKNET_COMPILE_PATH = os.getenv("STARKNET_COMPILE_PATH") or "starknet-compile"

COLLECTIONS_METADATA = {
    "ducks_everywhere": {
        "name": "Ducks Everywhere",
        "artist": "OutSmth",
    },
    "ducks_frens": {
        "name": "Ducks Frens",
        "artist": "OutSmth",
    },
    "lil_ducks": {
        "name": "Lil Ducks",
        "artist": "OutSmth",
    },
}


class UpdateBookletSpecRequest(BaseModel):
    booklet_spec: dict[str, str]


@router.head("/admin/update_booklet_spec/{chain_id}/{theme_id}")
@router.post("/admin/update_booklet_spec/{chain_id}/{theme_id}")
async def update_booklet_spec(data: UpdateBookletSpecRequest, chain_id: str, theme_id: str):
    # Backup the file
    theme_storage.get_backend(chain_id).backup_file(theme_storage.booklet_path())
    # Validate new file is sequential by reading all values, sorting, checking for holes
    new_booklet_spec_ids = list(data.booklet_spec.values())
    new_booklet_spec_ids.sort()
    last_id = new_booklet_spec_ids[0] # fail if no items, is OK
    for i in range(1, len(new_booklet_spec_ids)):
        if int(new_booklet_spec_ids[i], 16) != int(last_id, 16) + 1:
            raise HTTPException(status_code=400, detail="Booklet spec is not sequential")
        last_id = new_booklet_spec_ids[i]
    # Append the new keys to the existing file
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    booklet_spec.update(data.booklet_spec)
    theme_storage.get_backend(chain_id).store_json(theme_storage.booklet_path(), booklet_spec)
    theme_storage.reset_cache()


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
    # In this mode, we need to ensure that the object already exists, we're just filling in data.
    theme_storage.reset_cache()
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
    if file_storage.get_backend(chain_id).has_path(PATH + "/metadata_booklet.json"):
        file_storage.get_backend(chain_id).backup_file(PATH + "/metadata_booklet.json")
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

class UpdateTraitsRequest(BaseModel):
    data: dict[str, dict[str, str]]

@router.head("/admin/update_traits/{chain_id}/{theme_id}")
@router.post("/admin/update_traits/{chain_id}/{theme_id}")
async def update_traits(set: UpdateTraitsRequest, chain_id: str, theme_id: str):
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    updated_booklets = {}
    for object_id in set.data:
        if f"{theme_id}/{object_id}" not in booklet_spec:
            raise HTTPException(status_code=400, detail="Object does not exist: " + booklet_spec[f"{theme_id}/{object_id}"])
    
        # Load the existing booklet
        booklet_metadata = boxes.get_booklet_metadata(rid = boxes.BoxRID(chain_id, theme_id, object_id))

        for trait_key in set.data[object_id]:
            booklet_metadata["properties"][trait_key.lower()] = {
                "name": trait_key,
                "value": set.data[object_id][trait_key]
            }
            # Dumb but it works
            found = False
            for trait in booklet_metadata["attributes"]:
                if trait["trait_type"] == trait_key:
                    trait["value"] = set.data[object_id][trait_key]
                    found = True
            if not found:
                booklet_metadata["attributes"].append({
                    "trait_type": trait_key,
                    "value": set.data[object_id][trait_key],
                })

        updated_booklets[object_id] = booklet_metadata

    for object_id in updated_booklets:
        # backup file
        file_storage.get_backend(chain_id).backup_file(f"genesis_themes/{theme_id}/{object_id}/metadata_booklet.json")
        # Store at the end to ensure everything went right.
        file_storage.get_backend(chain_id).store_json(f"genesis_themes/{theme_id}/{object_id}/metadata_booklet.json", updated_booklets[object_id])


@router.head("/admin/update_glbs/{chain_id}/{theme_id}/{object_id}")
@router.post("/admin/update_glbs/{chain_id}/{theme_id}/{object_id}")
async def update_glbs(set: StoreThemeObjectRequest, chain_id: str, theme_id: str, object_id: str):
    # In this mode, we need to ensure that the object already exists, we're just filling in data.
    booklet_spec = theme_storage.get_booklet_spec(chain_id)
    if f"{theme_id}/{object_id}" not in booklet_spec:
        raise HTTPException(status_code=400, detail="Object does not exist: " + booklet_spec[f"{theme_id}/{object_id}"])

    # Load the existing booklet
    booklet_metadata = boxes.get_booklet_metadata(rid = boxes.BoxRID(chain_id, theme_id, object_id))

    PATH = f"genesis_themes/{theme_id}/{object_id}"

    data = await generate_object_data(set, chain_id, theme_id, object_id)

    booklet_metadata["nb_pages"] = data.booklet_metadata["nb_pages"]
    booklet_metadata["steps_progress"] = data.booklet_metadata["steps_progress"]

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

    # Store at the end to ensure everything went right.
    file_storage.get_backend(chain_id).store_json(PATH + "/metadata_booklet.json", booklet_metadata)


class CompileShapeContractRequest(BaseModel):
    shapes_by_attribute_id: dict[str, List[Any]]


@router.head("/admin/compile_shape_contract/")
@router.post("/admin/compile_shape_contract/")
async def compile_shape_contract(shapes: CompileShapeContractRequest):
    ids = {}
    for attr_id in shapes.shapes_by_attribute_id:
        items = []
        for shape in shapes.shapes_by_attribute_id[attr_id]:
            items.append(ShapeItem(
                shape['pos'][0],
                shape['pos'][1],
                shape['pos'][2],
                shape['data']['color'].lower(),
                ANY_MATERIAL_ANY_COLOR if ("any_color" in shape['data'] and shape['data']['any_color']) else int(shape['data']['material'], 16)
            ))
        items.sort(key=lambda x: x.x_y_z)
        ids[int(attr_id, 16)] = generate_shape_check(items)
    sorted_ids = list(ids.keys())
    sorted_ids.sort()
    code = HEADER + generate_binary_search_function(sorted_ids, lambda x: ids[x]) + "\n}"

    # Call starknet-compile via subprocess
    with tempfile.TemporaryDirectory() as tmpdirname:
        if ENV == "dev":
            tmpdirname = "tmp_contracts/"
            os.makedirs(tmpdirname, exist_ok=True)
        code_path = os.path.join(tmpdirname, "code.cairo")
        with open(code_path, "w") as f:
            f.write(code)

        process = await asyncio.create_subprocess_exec(
            STARKNET_COMPILE_PATH,
            code_path, "--single-file", os.path.join(tmpdirname, "sierra.json"),
        )
        await process.communicate()

        casm_process = await asyncio.create_subprocess_exec(
            STARKNET_COMPILE_PATH.replace('starknet-compile', 'starknet-sierra-compile'),
            os.path.join(tmpdirname, "sierra.json"), os.path.join(tmpdirname, "casm.json"),
            "--add-pythonic-hints"
        )
        await casm_process.communicate()

        if process.returncode != 0 or casm_process.returncode != 0:
            raise HTTPException(status_code=400, detail="Compilation failed")

        with open(os.path.join(tmpdirname, "sierra.json")) as f:
            sierra = f.read()
        with open(os.path.join(tmpdirname, "casm.json")) as f:
            casm = f.read()
        
        return await declare_contract(chain_id="starknet-testnet", sierra=sierra, casm=casm)


async def declare_contract(chain_id: str, sierra: str, casm: str):
    from briq_api.chain.rpcs import alchemy_endpoint
    from starknet_py.net.account.account import Account
    from starknet_py.net.full_node_client import FullNodeClient
    from starknet_py.net.signer.stark_curve_signer import KeyPair
    from starknet_py.common import create_casm_class
    from starknet_py.hash.casm_class_hash import compute_casm_class_hash
    from starknet_py.hash.sierra_class_hash import compute_sierra_class_hash
    from starknet_py.net.client_errors import ClientError

    DECLARER_ADDRESS = (os.getenv("DECLARER_ADDRESS") or "0xcafe")
    DECLARER_PUBLIC_KEY = (os.getenv("DECLARER_PUBLIC_KEY") or "0xdeadbeef")
    DECLARER_PRIVATE_KEY = (os.getenv("DECLARER_PRIVATE_KEY") or "0xdeadbeef")

    client = FullNodeClient(node_url=alchemy_endpoint[chain_id])
    account = Account(
        client=client,
        #address="0x4a51bd929bf274c66768908e2355a56181d3dc25bad2502c2319c786828e6e1",
        #key_pair=KeyPair(private_key=0x0176c9450e105a76362e53129e8ebcefb03571c0b58cf8785e7d6473cea554b7, public_key=0x3d7642db8ea33140afb852477670b0224f69f38fa1e0ed6eb721c6c80cabf69),
        address=DECLARER_ADDRESS,
        key_pair=KeyPair(private_key=DECLARER_PRIVATE_KEY, public_key=DECLARER_PUBLIC_KEY),
        chain=get_network_metadata(chain_id).chain_id,
    )

    # contract_compiled_casm is a string containing the content of the starknet-sierra-compile (.casm file)
    casm_class = create_casm_class(casm)

    # Compute Casm class hash
    casm_class_hash = compute_casm_class_hash(casm_class)

    # Create Declare v2 transaction (to create Declare v3 transaction use `sign_declare_v3_transaction` method)
    declare_v2_transaction = await account.sign_declare_v2_transaction(
        # compiled_contract is a string containing the content of the starknet-compile (.json file)
        compiled_contract=sierra,
        compiled_class_hash=casm_class_hash,
        max_fee=10**16,
    )

    class_hash = compute_sierra_class_hash(declare_v2_transaction.contract_class)
    try:
        tx = await account.client.declare(transaction=declare_v2_transaction)
        logger.info(f"Declared contract with TX hash {hex(tx.transaction_hash)} - {hex(tx.class_hash)} (expected {hex(class_hash)}))")
    except ClientError as err:
        logger.info(f"Failed to declare contract with expected class hash {hex(class_hash)}, got {err.message}")
        if str(err.code) == "59":  # TX already exists (also they lie about the type of err.code here)
            pass
        else:
            raise err

    # Don't wait for it, return immediately
    return { "class_hash": hex(class_hash) }


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
