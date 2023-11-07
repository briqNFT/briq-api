import json
from briq_api.indexer.events.common import encode_int_as_bytes, decode_bytes
from briq_api.indexer.storage import MongoBackend
from briq_api.storage.file.backends.file_storage import FileStorage
from briq_api.theme_storage import ThemeStorage

#mongo = MongoBackend(db_name="localtest-0")
mongo = MongoBackend(db_name="dojo_0")

theme_storage = ThemeStorage()
theme_storage.connect(FileStorage())


validity_condition_now = { "_chain.valid_to": None, "quantity": { "$ne": encode_int_as_bytes(0) } }

boxes = list(mongo.db['box_tokens'].find({
    **validity_condition_now
}))

all_booklets = list(mongo.db['booklet_tokens'].find({
    **validity_condition_now
}))

sets = list(mongo.db['set_tokens'].find({
    "token_id": { "$in": [x['owner'] for x in all_booklets] },
    **validity_condition_now,
}))

free_booklets = list(mongo.db['booklet_tokens'].find({
    "owner": { "$nin": [x['token_id'] for x in sets] },
    **validity_condition_now
}))

booklet_by_set = { x['owner']: x['token_id'] for x in all_booklets }

box_json_output = [{
    "owner": hex(decode_bytes(x['owner'])),
    "box_id": decode_bytes(x['token_id'])
} for x in boxes]

booklet_json_output = [{
    "owner": hex(decode_bytes(x['owner'])),
    "old_token_id": hex(decode_bytes(x['token_id']))
} for x in free_booklets]

sets_json_output = [{
    "owner": hex(decode_bytes(x['owner'])),
    "old_token_id": hex(decode_bytes(x['token_id'])),
    "matching_booklet_name": theme_storage.get_booklet_id_from_token_id('starknet-testnet-dojo', hex(decode_bytes(booklet_by_set[x['token_id']]))),
} for x in sets]

print(f"Sets: {len(sets)}")
print(f"Boxes: {len(boxes)}")
print(f"Booklets: {len(free_booklets)}")

print(json.dumps({
    "boxes": box_json_output,
    "booklets": booklet_json_output,
    "sets": sets_json_output,
}, indent=4))