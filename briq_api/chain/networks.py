

from dataclasses import dataclass


@dataclass
class NetworkMetadata:
    id: str
    storage_bucket: str = ''
    auction_address: str = ''
    box_address: str = ''
    briq_address: str = ''
    booklet_address: str = ''
    set_address: str = ''
    erc20_address: str = ''
    attributes_registry_address: str = ''


DEVNET = NetworkMetadata(
    id="localhost",
    auction_address="0x00c126cf6a2deda8af86deefb15ed85967f12e2deae0848e90918be0caa9ecce",
    box_address="0x0386dfa3727b66bc2c10bee1941b47d247cf24a06b89f087dc9e6072ccfdd559",
    briq_address="0x001fd19cbb5df0d12db9050f0ab86a55866ee4ce3d5cf3f897587b9513d8a134",
    booklet_address="0x03203d30b47a3c659e936cd44971a3d1ff522c138488a26250b191eef8199abb",
    erc20_address="0x62230ea046a9a5fbc261ac77d03c8d41e5d442db2284587570ab46455fd2488",
)

TESTNET = NetworkMetadata(
    id="starknet-testnet",
    auction_address="0x033f840d4f7bfa20aaa128e5a69157355478d33182bea6039d55aae3ffb861e2",
    box_address="0x003b51e657e236e7085d1006e8ae6f955f09793b7f6dbdfad7a1a8abadad464a",
    briq_address="0x06f18ebcc76b6bd3560da141aeae53f9af3d80c2001415c963ecddbba4e8ba12",
    booklet_address="0x05646ae11383a9994f958ee9cb29b3cf720b994733100ef7b8a00d6adcbe1c42",
    attributes_registry_address="0x05d660cb7354bbce7d6ce3861136098eb2ebf8af629f4ea0cc450ca546002d40",
    set_address="0x05f9e1c4975b0f71f0b1af2b837166d321af1cdba5c30c09b0d4822b493f1347",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_2 = NetworkMetadata(
    id="starknet-testnet2",
    storage_bucket="briq-bucket-test-1",
    auction_address="0x006fbea980d2acb5c63ad97637f6d7f3fa18887e3ad987abbd9eb594a58c0291",
    box_address="0x0799b964cd6a32611fbd589ebae040ad18715ae5cd9b1a42226bb0b1db48c631",
    briq_address="0x029e1fb93825a116daf88902c8bbf1a386890e6a5cf7906b584a1e70e7023e28",
    booklet_address="0x048891a90426d468603732453afa919f280a3bc61a9ef246519eec87760aad76",
    attributes_registry_address="0x0504b76a068732bf5791a826fb37d3de5ebcafbbcecce27532b27245cc8e7563",
    set_address="0x065ee60db9e38ecdf4afb9e070466b81984ffbcd06bc8650b1a21133310255c8",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

MAINNET = NetworkMetadata(
    id="starknet-mainnet",
    storage_bucket="briq-bucket-prod-1",
    auction_address="0x01712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620",
    box_address="0x01e1f972637ad02e0eed03b69304344c4253804e528e1a5dd5c26bb2f23a8139",
    briq_address="0x00247444a11a98ee7896f9dec18020808249e8aad21662f2fa00402933dce402",
    booklet_address="0x05faa82e2aec811d3a3b14c1f32e9bbb6c9b4fd0cd6b29a823c98c7360019aa4",
    attributes_registry_address="0x008d4f5b0830bd49a88730133a538ccaca3048ccf2b557114b1076feeff13c11",
    set_address="0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy", storage_bucket="briq-bucket-prod-1")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
        'starknet-mainnet': MAINNET,
    }[network]
