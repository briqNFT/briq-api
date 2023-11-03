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

    briq_address="0x67e44efc5d1868fde5ff9604b44c3cef2d77dc00e785f6d2c4519c248c8bdf2",
    factory_address="0x651a5b09f83dd7645c406763c4c32f0a369ad4f14729ee3cfd02b4a99fc8363",

    box_addresses=[
        "0xd9bfa6936fdd84593a3920937fc556c67c16da8d3d3663f6af299365cc3b10",  # box_nft_sp
        "0x6baff254582bd7750600b762729bd44b7dea781b17804fb5a529874e3f6d5fb",  # box_nft_briqmas
    ],

    booklet_addresses=[
        "0x53a545137759dc4d969b9816e809a7f9d89f0e86ad96d7277b33c724b466fa9",  # booklet_ducks
        "0x4104a0f65e62cce969e9adf103277c2b2681a731bca790f7d04c921488d2ec1",  # booklet_starknet_planet
        "0x5cce2521148759a6f605e7c7661c9d0441162bbe076cdef8385b3718e6c9afb",  # booklet_briqmas
        "0x1f582e9ee9f862caccaee12c181740e6f1fe8800df30c8b0c5ca14ef4651c59",  # booklet_lil_ducks
        "0x55afbd1c3b5e29891cffed94edd86fc60e044e89d9b329a1d31035e160058cb",  # booklet_fren_ducks
    ],

    sets_addresses=[
        "0x16a1e2799d18948eeb8d153180169d3ebbd964958ff338d9446fd5834f18836",  # set_nft
        "0x112c60e1c47f74e3328f9ca0678519de2f962de678bafb3f37c5d5a2e05a58e",  # set_nft_ducks
        "0x49fbdb572e1b1bc24db67bb9205329227daa838039e344dd33ae91af76812e7",  # set_nft_sp
        "0x69710c8ee4465f4ea29636bc741224a2ec9456191c88ca52d1a04bc413efafb",  # set_nft_briqmas
    ],

    sets_1155_addresses=[
        "0x4499ce1604e2432e26779b97ca6e56250bb612103e3f13233f25dbecabf13f7",  # set_nft_1155_lil_ducks
        "0x7645accafb7d12f07dcc7abca241f3afbaefc9300aca5ca90b85ea6db50cfe3",  # set_nft_1155_fren_ducks
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
