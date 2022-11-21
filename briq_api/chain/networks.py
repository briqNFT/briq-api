

from dataclasses import dataclass


@dataclass
class NetworkMetadata:
    id: str
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

TESTNET_NORMAL = NetworkMetadata(
    id="starknet-testnet",
    auction_address="0x0435c3be3e2a583c6d9c85f5d751b11acb8230f997b3c7b7ab11bbd97beda220",
    box_address="0x0324642cf2a18e0873d80ea91e1426b3a776806ba31fc0a694014567ac1018cd",
    briq_address="0x02165e8c1dd9bd5dd6583da76d08b3c306fda013a6c621bee403c280ead9aaa7",
    booklet_address="0x053c894cd8ba4d953540dc7056c811289ad631bc1dcea07bc323f6f9c9f1f31f",
    attributes_registry_address="0x078cf4ac0d91c0e418bdd8ccd08122583daac33a2ba3dfecca66e8953402e2eb",
    set_address="0x04172804038f94b8ebeec4cb74992e9a6d436ecafd3b018767c7d107550cda90",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET = NetworkMetadata(
    id="starknet-testnet",
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
    auction_address="0x01712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620",
    box_address="0x01e1f972637ad02e0eed03b69304344c4253804e528e1a5dd5c26bb2f23a8139",
    briq_address="0x00247444a11a98ee7896f9dec18020808249e8aad21662f2fa00402933dce402",
    booklet_address="0x05faa82e2aec811d3a3b14c1f32e9bbb6c9b4fd0cd6b29a823c98c7360019aa4",
    attributes_registry_address="0x008d4f5b0830bd49a88730133a538ccaca3048ccf2b557114b1076feeff13c11",
    set_address="0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
        'starknet-mainnet': MAINNET,
    }[network]
