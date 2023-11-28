from typing import List
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from dataclasses import dataclass, field


@dataclass
class NetworkMetadata:
    id: str
    chain_id: int = 0
    storage_bucket: str = ''
    base_domain: str = 'briq.construction'
    auction_address: str = '0'
    auction_ducks: str = '0'
    box_address: str = '0'
    briq_address: str = '0'
    booklet_address: str = '0'
    set_address: str = '0'
    erc20_address: str = '0'
    attributes_registry_address: str = '0'
    factory_address: str = '0'
    box_addresses: List[str] = field(default_factory=list)
    booklet_addresses: List[str] = field(default_factory=list)
    sets_addresses: List[str] = field(default_factory=list)
    sets_1155_addresses: List[str] = field(default_factory=list)


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
    chain_id=StarknetChainId.TESTNET.value,
    base_domain='test.sltech.company',
    auction_address="0x033f840d4f7bfa20aaa128e5a69157355478d33182bea6039d55aae3ffb861e2",
    auction_ducks="0x04ef0bd475fb101cc1b5dc2c4fc9d11b4fa233cfa1876924ec84b2f3dcf32f75",
    box_address="0x043bafcb15f12c137229406f96735eba51018fe75e5330058479556bc77dfd94",
    briq_address="0x0068eb19445f96b3c3775fba757de89ee8f44fda42dc08173a501acacd97853f",
    booklet_address="0x018734a90e5df97235c0ff83f92174cf6f16ad3ec572e38e2e146e47c8878839",
    attributes_registry_address="0x06a780187cfd58ad6ce1279cb4291bcf4f8acb2806dc1dccc9aee8183a9c1c40",
    set_address="0x038bf557306ab58c7e2099036b00538b51b37bdad3b8abc31220001fb5139365",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",

    box_addresses=["0x043bafcb15f12c137229406f96735eba51018fe75e5330058479556bc77dfd94"],
    booklet_addresses=["0x018734a90e5df97235c0ff83f92174cf6f16ad3ec572e38e2e146e47c8878839"],
    sets_addresses=["0x038bf557306ab58c7e2099036b00538b51b37bdad3b8abc31220001fb5139365"],
)

TESTNET_DOJO = NetworkMetadata(
    id="starknet-testnet-dojo",
    storage_bucket="briq-bucket-test-1",
    base_domain='test.sltech.company',

    briq_address="0x62d33afa007607ff0eaf008280f72c1033f5a1fda176f20fc36521c80f7a1ba",
    factory_address="0x227a1cc8dfb791628ef60e73d2676b9a1da43b878e8d14a920ba96cec63c79c",

    box_addresses=[
        "0x1d23f59c358da797256a3ff346dcce909f4be05342ef5a4e184132945117ef",  # box_nft_sp
        "0x76fb0333408c9f4de5d898b1fd349b80077e8a22b2608710c1652e090f92a11",  # box_nft_briqmas
    ],

    booklet_addresses=[
        "0x235aae7d603648452f9bb7ee71b18a9d83e1dbc9f4ed693fb4ab9409962b57a",  # booklet_ducks
        "0x5ce6ca596712b54cfc04b9a8d74b41b2158dcaad73f456035dbdae1b019fcb9",  # booklet_starknet_planet
        "0x5c1330e30b7e08cc552baff0c9d76a68d15527671bab44936ad95bdc6c4262e",  # booklet_briqmas
        "0x7294576a17089d0f8d9920ccda875ab1b60567f3009f6e2b2a598f42bef5036",  # booklet_lil_ducks
        "0x70970b0319cd1b706a1ad24a158b4b44e536588eebc8972eaf0602a1db523bc",  # booklet_fren_ducks
    ],

    sets_addresses=[
        "0x4b9a60a3acada4322d3348133d6bad63a6309ec40d23d093651e07a6cb28810",  # set_nft
        "0x14f4eea3d6a7627c0d719cad3dbd55452833514afcbe76e299cef7ef00cb20e",  # set_nft_ducks
        "0x58206fa33f9aa43f8c0ee52abf390c18006f3f0d52c7c3e464e619fe2a5cfc5",  # set_nft_sp
        "0x6ebbc1d4a154e7f86957080d19a81a85d2cd1582db03f9d401c42529453f3fa",  # set_nft_briqmas
    ],

    sets_1155_addresses=[
        "0x341e9fb783afbf3d15f6377c5e18ce2fa412e39c853ab46d0c55cff40bf8dac",  # set_nft_1155_lil_ducks
        "0x3eb663fec0a5ee53e88ef8222acfbc39a17e2109cefa79507d6f19e58e2710f",  # set_nft_1155_fren_ducks
    ],

    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)


MAINNET = NetworkMetadata(
    id="starknet-mainnet",
    chain_id=StarknetChainId.MAINNET.value,
    storage_bucket="briq-bucket-prod-1",
    base_domain='briq.construction',

    auction_address="0x01712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620",
    auction_ducks="0x00b9bb7650a88f7e375ae8d31d48b4d4f13c6c34344839837d7dae7ffcdd3df0",
    box_address="0x01e1f972637ad02e0eed03b69304344c4253804e528e1a5dd5c26bb2f23a8139",
    briq_address="0x00247444a11a98ee7896f9dec18020808249e8aad21662f2fa00402933dce402",
    booklet_address="0x05faa82e2aec811d3a3b14c1f32e9bbb6c9b4fd0cd6b29a823c98c7360019aa4",
    attributes_registry_address="0x008d4f5b0830bd49a88730133a538ccaca3048ccf2b557114b1076feeff13c11",
    set_address="0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",

    box_addresses=["0x01e1f972637ad02e0eed03b69304344c4253804e528e1a5dd5c26bb2f23a8139"],
    booklet_addresses=["0x05faa82e2aec811d3a3b14c1f32e9bbb6c9b4fd0cd6b29a823c98c7360019aa4"],
    sets_addresses=["0x01435498bf393da86b4733b9264a86b58a42b31f8d8b8ba309593e5c17847672"],
)


TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy", storage_bucket="briq-bucket-prod-1")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
        'starknet-testnet-dojo': TESTNET_DOJO,
        'starknet-mainnet': MAINNET,
    }[network]


def get_gateway_client(network: str):
    return GatewayClient({
        'localhost': 'http://localhost:8000',
        'starknet-testnet': 'testnet',
        'starknet-testnet-dojo': 'testnet',
        'starknet-mainnet': 'mainnet',
    }[network])
