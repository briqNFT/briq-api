import io
import logging
import base64
import pathlib

from PIL import Image

from datetime import datetime
from briq_api.memory_cache import CacheData

from briq_api.set_identifier import SetRID
from briq_api.stores import genesis_storage, file_storage, theme_storage
from briq_api.indexer.storage import mongo_storage
from briq_api.api.boxes import BoxRID, get_booklet_metadata
from briq_api.mesh.briq import BriqData

logger = logging.getLogger(__name__)


@CacheData.memory_cache(lambda rid: f"{rid.chain_id},{rid.token_id}", timeout=5 * 60)
def cached_set_metadata(rid: SetRID):
    return file_storage.load_set_metadata(rid)


async def get_metadata(rid: SetRID):
    data = cached_set_metadata(rid)
    data['created_at'] = await mongo_storage.get_mint_date(rid.chain_id, 'set', int(rid.token_id, 16))
    data['attributes'] = [{
        "trait_type": "Number of briqs",
        "value": len(data['briqs'])
    }]
    if data['created_at'] != -1:
        data['attributes'].append({
            "display_type": "date",
            "trait_type": "Creation Date",
            "value": datetime.fromtimestamp(data['created_at']).strftime('%Y-%m-%d'),
        })
    data['properties'] = {
        "nb_briqs": {
            "name": "Number of briqs",
            "value": len(data['briqs'])
        }
    }
    # Collection hints for POAPs
    # TODO: make this more general
    if 'collection_hint' in data and data['collection_hint'] == 'poaps':
        data['attributes'].append({
            "trait_type": "Collections",
            "value": ["briq POAPs"],
        })
        data['attributes'].append({
            "trait_type": "briq POAPs",
            "value": True,
        })
        data['properties']['collections'] = {
            "name": "Collections",
            "value": ["briq POAPs"]
        }
        data.pop('collection_hint')
    elif 'collection_hint' in data and data['collection_hint'] == 'unframed':
        data['attributes'].append({
            "trait_type": "Collections",
            "value": ["Ducks Everywhere x Unframed"],
        })
        data['attributes'].append({
            "trait_type": "Ducks Everywhere x Unframed",
            "value": True,
        })
        data['properties']['collections'] = {
            "name": "Collections",
            "value": ["Ducks Everywhere x Unframed"]
        }
        data.pop('collection_hint')
    else:
        booklets = await mongo_storage.get_user_nfts(rid.chain_id, rid.token_id, 'booklet')
        if len(booklets.nfts):
            data['booklet_id'] = theme_storage.get_booklet_id_from_token_id(rid.chain_id, booklets.nfts[0])
            booklet_meta = get_booklet_metadata(BoxRID(rid.chain_id, data['booklet_id'].split("/")[0], data['booklet_id'].split("/")[1]))
            data['attributes'] += booklet_meta['attributes']
            for prop in booklet_meta['properties']:
                if not (prop in data['properties']):
                    data['properties'][prop] = booklet_meta['properties'][prop]
    return data


def get_preview(rid: SetRID):
    try:
        return file_storage.load_set_preview(rid)
    except Exception:
        pass
    # Try to generate a default image, and if that fails store something anyways to avoid DOS.
    try:
        data = file_storage.load_set_metadata(rid)
        image_data_stream = io.BytesIO()
        BriqData().load(data).to_png().save(image_data_stream, format='PNG')
        image_data = image_data_stream.getvalue()
        file_storage.store_set_preview(rid, image_data)
        return image_data
    except Exception:
        image_data = open(pathlib.Path(__file__).parent.resolve() / "No_Preview_image_2.png", 'rb').read()
        file_storage.store_set_preview(rid, image_data)
        return image_data


in_mem_thumbnails: dict[str, bytes] = {}


def get_small_preview(rid: SetRID):
    global in_mem_thumbnails
    if f'{rid.chain_id}_{rid.token_id}' in in_mem_thumbnails:
        return in_mem_thumbnails[f'{rid.chain_id}_{rid.token_id}']
    try:
        image = file_storage.load_set_preview(rid)
        # Load the image
        loaded_image = Image.open(io.BytesIO(image))
        # Resize the image
        resized_image = loaded_image.resize((375, 375)).convert('RGB')
        # Save as JPG byte stream
        image_data_stream = io.BytesIO()
        resized_image.save(image_data_stream, format='jpeg', quality=80)
        image_data = image_data_stream.getvalue()
        # Save in memory
        in_mem_thumbnails[f'{rid.chain_id}_{rid.token_id}'] = image_data
        return image_data
    except Exception as e:
        logger.error(e)
        pass
    # Return default image, don't store anything.
    image_data = open(pathlib.Path(__file__).parent.resolve() / "No_Preview_image_2.png", 'rb').read()
    return image_data


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
    # This is intended to prevent hostile replacement of data.
    if file_storage.has_set_metadata(rid):
        return
    if len(image_base64) > 0:
        store_preview_image(rid, image_base64)
    file_storage.store_set_metadata(rid, setData)


async def get_user_bids(chain_id: str, user_id: str):
    try:
        encoded_user_id = int(user_id)
    except:
        encoded_user_id = int(user_id, 16)
    data = mongo_storage.get_backend(chain_id).async_db["bids"].find({"bidder": encoded_user_id.to_bytes(32, "big"), "valid_to": None})
    bids = [
        {
            "box_token_id": hex(int.from_bytes(item['box_token_id'], "big")),
            "box_id": theme_storage.get_box_id(chain_id, hex(int.from_bytes(item['box_token_id'], "big"))),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "bid_id": hex(int.from_bytes(item['_tx_hash'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        async for item in data
    ]
    return bids


async def get_bids_for_box(chain_id: str, box_id: str):
    box_token_id = genesis_storage.get_box_token_id(chain_id, box_id)
    data = mongo_storage.get_backend(chain_id).async_db["bids"].find({"box_token_id": box_token_id.to_bytes(32, "big"), "valid_to": None})
    bids = [
        {
            "bidder": hex(int.from_bytes(item['bidder'], "big")),
            "bid_amount": str(int.from_bytes(item['bid_amount'], "big")),
            "bid_id": hex(int.from_bytes(item['_tx_hash'], "big")),
            "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
            "block": item['_block'],
            "timestamp": item['_timestamp'],
        }
        async for item in data
    ]
    return bids


async def get_item_activity(item_type: str, chain_id: str, item: str):
    if item_type == 'box':
        token_id = int(genesis_storage.get_box_token_id(chain_id, item))
        data = mongo_storage.get_backend(chain_id).async_db["box_transfers"].find({"token_id": token_id.to_bytes(32, "big")})
        return [
            {
                "from": hex(int.from_bytes(item['from'], "big")),
                "to": hex(int.from_bytes(item['to'], "big")),
                "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
                "block": item['_block'],
                "timestamp": item['_timestamp'],
            }
            async for item in data
        ]
    if item_type == 'booklet':
        token_id = int(theme_storage.get_booklet_token_id_from_id(chain_id, item), 16)
        data = mongo_storage.get_backend(chain_id).async_db["booklet_transfers"].find({"token_id": token_id.to_bytes(32, "big")})
        return [
            {
                "from": hex(int.from_bytes(item['from'], "big")),
                "to": hex(int.from_bytes(item['to'], "big")),
                "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
                "block": item['_block'],
                "timestamp": item['_timestamp'],
            }
            async for item in data
        ]
    if item_type == 'set':
        token_id = int(item, 16)
        data = mongo_storage.get_backend(chain_id).async_db["set_transfers"].find({"token_id": token_id.to_bytes(32, "big")})
        return [
            {
                "from": hex(int.from_bytes(item['from'], "big")),
                "to": hex(int.from_bytes(item['to'], "big")),
                "tx_hash": hex(int.from_bytes(item['_tx_hash'], "big")),
                "block": item['_block'],
                "timestamp": item['_timestamp'],
            }
            async for item in data
        ]
