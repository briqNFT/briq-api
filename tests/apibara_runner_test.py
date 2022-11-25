import base64
import pytest

from apibara.indexer.handler import Info, MessageHandler, UserContext
from apibara.indexer.storage import IndexerStorage
from apibara.model import EventFilter, NewBlock, NewEvents

from briq_api.indexer import config

from briq_api.indexer.runner import (
    handle_events, handle_block, handle_pending_events,
    bid_filter, box_filters, booklet_filters, briq_filters, set_filters
)

@pytest.fixture(scope="function")
def storage():
    connection_url = "mongodb://apibara:apibara@localhost:27017"
    storage = IndexerStorage(connection_url, "python-sdk-test-db")
    yield storage
    # cleanup database
    storage.drop_database()

@pytest.mark.asyncio
async def test_invalidate_after_data(storage: IndexerStorage):
    context = dict()

    handler = MessageHandler(
        data_handler=handle_events,
        block_handler=handle_block,
        reorg_handler=lambda _: None,
        pending_handler=handle_pending_events,
        context=context,
        storage=storage,
        starting_filters=bid_filter + box_filters + booklet_filters + briq_filters + set_filters,
    )

    with storage.create_storage_for_block(11000) as s:
        await handler.handle_data({
            "timestamp": "2022-11-23T13:33:11Z",
            "parent_block_hash": {
                "hash": "tata"
            },
            "@type": "type.googleapis.com/apibara.starknet.v1alpha1.Block",
            "block_hash": {
                "hash": "toto"
            },
            "block_number": "11000",
            "transaction_receipts": [
                {
                    "transaction_hash": "A5hUpv6U4SBrm2Ioi7eDsZTcpdrXwBWX8SEqBNa+QsM=",
                    "actual_fee": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACchjG9Xuk=",
                    "execution_resources": {
                        "n_steps": "6873",
                        "n_memory_holes": "284",
                        "builtin_instance_counter": {
                            "pedersen_builtin": "106",
                            "range_check_builtin": "159",
                            "ecdsa_builtin": "1"
                        }
                    },
                    "events": [
                        {
                            "from_address": base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                            "keys": [
                                base64.b64encode(0x182d859c0807ba9db63baf8b9d9fdbfeb885d820be6e206b9dab626d995c433.to_bytes(32, "big"))
                            ],
                            "data": [
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                #base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                                #base64.b64encode((123456).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                            ]
                        },
                    ]
                },
            ],
            "transactions": [
                {
                    "invoke": {
                        "common": {
                            "hash": base64.b64encode(b'toto')
                        }
                    }
                }
            ]
        })

    assert len(list(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    }))) == 0

    assert len(list(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    }))) == 0

    with storage.create_storage_for_block(11001) as s:
        await handler.handle_data({
            "timestamp": "2022-11-23T13:33:11Z",
            "parent_block_hash": {
                "hash": "tata"
            },
            "@type": "type.googleapis.com/apibara.starknet.v1alpha1.Block",
            "block_hash": {
                "hash": "toto"
            },
            "block_number": "11001",
            "transaction_receipts": [
                {
                    "transaction_hash": "A5hUpv6U4SBrm2Ioi7eDsZTcpdrXwBWX8SEqBNa+QsM=",
                    "actual_fee": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACchjG9Xuk=",
                    "execution_resources": {
                        "n_steps": "6873",
                        "n_memory_holes": "284",
                        "builtin_instance_counter": {
                            "pedersen_builtin": "106",
                            "range_check_builtin": "159",
                            "ecdsa_builtin": "1"
                        }
                    },
                    "events": [
                        {
                            "from_address": base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                            "keys": [
                                base64.b64encode(0x182d859c0807ba9db63baf8b9d9fdbfeb885d820be6e206b9dab626d995c433.to_bytes(32, "big"))
                            ],
                            "data": [
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode((123456).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode((2).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                            ]
                        },
                    ]
                },
            ],
            "transactions": [
                {
                    "invoke": {
                        "common": {
                            "hash": base64.b64encode(b'toto')
                        }
                    }
                }
            ]
        })

    assert int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 2
    assert int.from_bytes(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 2

    with storage.create_storage_for_block(11002) as s:
        await handler.handle_pending({
            "timestamp": "2022-11-23T13:33:11Z",
            "parent_block_hash": {
                "hash": "tata"
            },
            "@type": "type.googleapis.com/apibara.starknet.v1alpha1.Block",
            "block_hash": {
                "hash": "toto"
            },
            "block_number": "11002",
            "transaction_receipts": [
                {
                    "transaction_hash": "A5hUpv6U4SBrm2Ioi7eDsZTcpdrXwBWX8SEqBNa+QsM=",
                    "actual_fee": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACchjG9Xuk=",
                    "execution_resources": {
                        "n_steps": "6873",
                        "n_memory_holes": "284",
                        "builtin_instance_counter": {
                            "pedersen_builtin": "106",
                            "range_check_builtin": "159",
                            "ecdsa_builtin": "1"
                        }
                    },
                    "events": [
                        {
                            "from_address": base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                            "keys": [
                                base64.b64encode(0x182d859c0807ba9db63baf8b9d9fdbfeb885d820be6e206b9dab626d995c433.to_bytes(32, "big"))
                            ],
                            "data": [
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode((123456).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode((1).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                            ]
                        },
                    ]
                },
            ],
            "transactions": [
                {
                    "invoke": {
                        "common": {
                            "hash": base64.b64encode(b'toto')
                        }
                    }
                }
            ]
        })

    print("QUANTITY", int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big"))

    assert int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 3
    assert int.from_bytes(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 2

    with storage.create_storage_for_block(11002) as s:
        await handler.handle_pending({
            "timestamp": "2022-11-23T13:33:11Z",
            "parent_block_hash": {
                "hash": "tata"
            },
            "@type": "type.googleapis.com/apibara.starknet.v1alpha1.Block",
            "block_hash": {
                "hash": "toto"
            },
            "block_number": "11002",
            "transaction_receipts": [
                {
                    "transaction_hash": "A5hUpv6U4SBrm2Ioi7eDsZTcpdrXwBWX8SEqBNa+QsM=",
                    "actual_fee": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACchjG9Xuk=",
                    "execution_resources": {
                        "n_steps": "6873",
                        "n_memory_holes": "284",
                        "builtin_instance_counter": {
                            "pedersen_builtin": "106",
                            "range_check_builtin": "159",
                            "ecdsa_builtin": "1"
                        }
                    },
                    "events": [
                        {
                            "from_address": base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                            "keys": [
                                base64.b64encode(0x182d859c0807ba9db63baf8b9d9fdbfeb885d820be6e206b9dab626d995c433.to_bytes(32, "big"))
                            ],
                            "data": [
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode((123456).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode((3).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                            ]
                        },
                    ]
                },
            ],
            "transactions": [
                {
                    "invoke": {
                        "common": {
                            "hash": base64.b64encode(b'toto')
                        }
                    }
                }
            ]
        })

    print("QUANTITY", int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big"))

    assert int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 5
    assert int.from_bytes(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 2

    with storage.create_storage_for_block(11002) as s:
        await handler.handle_data({
            "timestamp": "2022-11-23T13:33:11Z",
            "parent_block_hash": {
                "hash": "tata"
            },
            "@type": "type.googleapis.com/apibara.starknet.v1alpha1.Block",
            "block_hash": {
                "hash": "toto"
            },
            "block_number": "11002",
            "transaction_receipts": [
                {
                    "transaction_hash": "A5hUpv6U4SBrm2Ioi7eDsZTcpdrXwBWX8SEqBNa+QsM=",
                    "actual_fee": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACchjG9Xuk=",
                    "execution_resources": {
                        "n_steps": "6873",
                        "n_memory_holes": "284",
                        "builtin_instance_counter": {
                            "pedersen_builtin": "106",
                            "range_check_builtin": "159",
                            "ecdsa_builtin": "1"
                        }
                    },
                    "events": [
                        {
                            "from_address": base64.b64encode(int(config.NETWORK.box_address, 16).to_bytes(32, "big")),
                            "keys": [
                                base64.b64encode(0x182d859c0807ba9db63baf8b9d9fdbfeb885d820be6e206b9dab626d995c433.to_bytes(32, "big"))
                            ],
                            "data": [
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode(int(config.NETWORK.auction_address, 16).to_bytes(32, "big")),
                                base64.b64encode((123456).to_bytes(32, "big")),
                                base64.b64encode((5).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                                base64.b64encode((2).to_bytes(32, "big")),
                                base64.b64encode((0).to_bytes(32, "big")),
                            ]
                        },
                    ]
                },
            ],
            "transactions": [
                {
                    "invoke": {
                        "common": {
                            "hash": base64.b64encode(b'toto')
                        }
                    }
                }
            ]
        })

    assert int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 4
    assert int.from_bytes(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big") == 4

    print("QUANTITY", int.from_bytes(storage.db['box_pending_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big"))

    print("QUANTITY", int.from_bytes(storage.db['box_tokens'].find({
        "owner": (123456).to_bytes(32, "big"),
        "_chain.valid_to": None
    })[0]['quantity'], "big"))
