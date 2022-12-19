from briq_api.indexer.storage import MongoBackend, MongoStorage

mongo = MongoBackend(db_name="kub_mainnet_2")

owners = set()

validity_condition_now = { "$or": [
        { "_chain.valid_to": { "$gte": 8000, "$lte": 10000 } },
        { "_chain.valid_to": None },
    ]
}
# For the purpose of validity, I am running this 'after' the block. Any transaction that is part of the block is counted.
validity_condition_actual = { "$and": [
        { "$or": [
            # Ergo here strictly greater than.
            { "_chain.valid_to": { "$gt": 17135 } },
            { "_chain.valid_to": None },
        ]},
        { "$or": [
            # and here less equal than
            { "_chain.valid_from": { "$lte": 17135 } },
            { "_chain.valid_from": None },
        ]}
    ]
}

tokens = mongo.db['box_tokens'].find({
    "quantity": { "$ne": (0).to_bytes(32, "big") },
    **validity_condition_actual
})

for data in tokens:
    print("box -> ", hex(int.from_bytes(data['owner'], "big")), hex(int.from_bytes(data['token_id'], "big")), data['_chain']['valid_to'], data['_chain']['valid_from'])
    owners.add(int.from_bytes(data['owner'], "big"))

tokens = mongo.db['booklet_tokens'].find({
    "quantity": { "$ne": (0).to_bytes(32, "big") },
    **validity_condition_actual
})

for data in tokens:
    print("booklet -> ", hex(int.from_bytes(data['owner'], "big")), hex(int.from_bytes(data['token_id'], "big")), data['_chain']['valid_to'], data['_chain']['valid_from'])
    owners.add(int.from_bytes(data['owner'], "big"))


tokens = mongo.db['set_tokens'].find({
    "quantity": { "$ne": (0).to_bytes(32, "big") },
    **validity_condition_actual
})

sets = set()
for data in tokens:
    sets.add(int.from_bytes(data['token_id'], "big"))
    booklets = mongo.db['booklet_tokens'].find({ "owner": data['token_id'] })
    if len(list(booklets)) > 0:
        print("set -> ", hex(int.from_bytes(data['owner'], "big")), hex(int.from_bytes(data['token_id'], "big")), data['_chain']['valid_to'], int.from_bytes(data['token_id'], "big"))
        owners.add(int.from_bytes(data['owner'], "big"))
    else:
        print("noneligible set -> ", hex(int.from_bytes(data['owner'], "big")), hex(int.from_bytes(data['token_id'], "big")), data['_chain']['valid_to'], int.from_bytes(data['token_id'], "big"))

airdrop_recipients = owners.difference(sets)
for owner in airdrop_recipients:
    print(hex(owner))
