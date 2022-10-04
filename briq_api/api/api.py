import io
import logging
import base64

from PIL import Image

from briq_api.set_identifier import SetRID
from briq_api.stores import genesis_storage, file_storage
from briq_api.indexer.storage import mongo_storage

from briq_api.mesh.briq import BriqData

logger = logging.getLogger(__name__)


def get_metadata(rid: SetRID):
    data = file_storage.load_set_metadata(rid)
    booklets = mongo_storage.get_user_nfts(rid.chain_id, rid.token_id, 'booklet')
    if len(booklets.nfts):
        data['booklet_id'] = genesis_storage.get_booklet_id(rid.chain_id, booklets.nfts[0])
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
    if len(image_base64) > 5000 * 1000:
        raise Exception("Image is too heavy, max size is 5MB")

    png_data = base64.decodebytes(image_base64[len(HEADER):])
    image = Image.open(io.BytesIO(png_data))

    if image.width > 2000 or image.height > 2000 or image.width < 10 or image.height < 10:
        raise Exception("Image is too large, acceptable size range from 10x10 to 2000x2000")

    file_storage.store_set_preview(rid, png_data)


async def store_set(rid: SetRID, setData: dict, image_base64: bytes):
    # Fail silently if we already have some metadata, we'll let the indexer handle things.
    # This can happen if a first mint fails for some reason but the 'hint' went through,
    # or if a set happens to have the same token ID as an earlier one.
    if file_storage.has_set_metadata(rid):
        return
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
            "box_id": genesis_storage.get_box_id(chain_id, hex(int.from_bytes(item['box_token_id'], "big"))),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "bid_id": hex(int.from_bytes(item['_tx_hash'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        for item in data
    ]
    return bids


def get_bids_for_box(chain_id: str, box_id: str):
    box_token_id = genesis_storage.get_box_token_id(chain_id, box_id)
    data = mongo_storage.get_backend(chain_id).db["bids"].find({"box_token_id": box_token_id.to_bytes(32, "big"), "valid_to": None})
    bids = [
        {
            "bidder": hex(int.from_bytes(item['bidder'], "big")),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "bid_id": hex(int.from_bytes(item['_tx_hash'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        for item in data
    ]
    return bids
