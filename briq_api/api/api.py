import io
import logging
import base64

from PIL import Image

from briq_api.chain.contracts import NETWORKS

from briq_api.set_identifier import SetRID
from briq_api.stores import genesis_storage, file_storage
from briq_api.indexer.storage import mongo_storage

from briq_api.mesh.briq import BriqData

logger = logging.getLogger(__name__)


def get_metadata(rid: SetRID):
    data = file_storage.load_set_metadata(rid)
    if 'version' not in data:
        data['description'] = data['description'] if 'description' in data else 'A set made of briqs'
        data['image'] = data['image'].replace('://briq.construction', '://api.briq.construction') if 'image' in data else ''
        data['external_url'] = data['external_url'] if 'external_url' in data else '',
        data['animation_url'] = data['animation_url'] if 'animation_url' in data else '',
        data['background_color'] = data['background_color'] if 'background_color' in data else '',

    return data


def get_preview(rid: SetRID):
    return file_storage.load_set_preview(rid)


def get_model(rid: SetRID, kind: str) -> bytes:
    return file_storage.load_set_model(rid, kind)


def create_model(metadata: dict, kind: str) -> bytes:
    briqData = BriqData().load(metadata)
    if kind == "glb" or kind == "gltf":
        return b''.join(briqData.to_gltf().save_to_bytes())
    elif kind == "vox":
        return briqData.to_vox("").to_bytes()
    else:
        raise Exception("Unknown model type " + kind)


def store_model(rid: SetRID, kind: str, model_data: bytes):
    if kind == "glb" or kind == "gltf":
        file_storage.store_set_model(rid, "glb", model_data)
    elif kind == "vox":
        file_storage.store_set_model(rid, "vox", model_data)
    else:
        raise Exception("Unknown model type " + kind)


def store_preview_image(rid: SetRID, image_base64: bytes):
    HEADER = b'data:image/png;base64,'
    if image_base64[0:len(HEADER)] != HEADER:
        raise Exception("Only base-64 encoded PNGs are accepted.")
    if len(image_base64) > 1000 * 1000:
        raise Exception("Image is too heavy, max size is 1MB")

    png_data = base64.decodebytes(image_base64[len(HEADER):])
    image = Image.open(io.BytesIO(png_data))

    if image.width > 1000 or image.height > 1000 or image.width < 10 or image.height < 10:
        raise Exception("Image is too large, acceptable size range from 10x10 to 1000x1000")

    file_storage.store_set_preview(rid, png_data)


def get_set_owner(rid: SetRID):
    return NETWORKS[rid.chain_id]["set_contract"].functions["ownerOf_"].call(int(rid.token_id, 16))


async def store_set(rid: SetRID, setData: dict, image_base64: bytes):
    # If we already have data stored, it may have been from an earlier failed attempt.
    # Check that the NFT has no owner on-chain
    if file_storage.has_set_metadata(rid):
        owner = get_set_owner(rid)
        if await owner != 0:
            raise Exception("NFT already exists")

    # Will overwrite, which is OK since we checked the owner.
    if len(image_base64) > 0:
        store_preview_image(rid, image_base64)
    file_storage.store_set_metadata(rid, setData)


def get_user_bids(chain_id: str, user_id: str):
    try:
        encoded_user_id = int(user_id)
    except:
        encoded_user_id = int(user_id, 16)
    data = mongo_storage.get_backend(chain_id).db["bids"].find({"bidder": encoded_user_id.to_bytes(32, "big"), "valid_to": None})
    bids = [
        {
            "box_token_id": hex(int.from_bytes(item['box_token_id'], "big")),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        for item in data
    ]
    return bids


def get_bids_for_box(chain_id: str, box_id: str):
    box_data = genesis_storage.get_backend(chain_id).load_json("box_spec.json")
    data = mongo_storage.get_backend(chain_id).db["bids"].find({"box_token_id": box_data[box_id].to_bytes(32, "big"), "valid_to": None})
    bids = [
        {
            "bidder": hex(int.from_bytes(item['bidder'], "big")),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        for item in data
    ]
    return bids
