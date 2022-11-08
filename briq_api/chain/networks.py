

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
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
        'starknet-mainnet': MAINNET,
    }[network]
