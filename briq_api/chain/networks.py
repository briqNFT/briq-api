from typing import List
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
    chain_id=StarknetChainId.GOERLI.value,
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
    chain_id=StarknetChainId.GOERLI.value,
    storage_bucket="briq-bucket-test-1",
    base_domain='test.sltech.company',

    briq_address="0x2417eb26d02947416ed0e9d99c7a023e3565fc895ee21a0a0ef88a524a665d6",
    factory_address="0x3374d4a1b4f8dc87bd680ddbd4f1181b3ec3cf5a8ef803bc4351603b063314f",

    box_addresses=[
        "0x73e3b5e6c7924f752a158c2b07f606bd5b885029da0ac1e3cde254985303f50",  # box_nft_sp
        "0x69699ce808b5459a3b652b5378f8c141e1dc79e10f4e7b486439fd989b7dfb1",  # box_nft_briqmas
    ],

    booklet_addresses=[
        "0x3311cdef78f70c1b13568e6dabda043c5e9d2736c0c02a35aa906d91d69836b",  # booklet_ducks
        "0x2fd50e1bdd7400a8fc97eb63aa4f3423a7ec72ebe78d413ce410ec60a35afea",  # booklet_starknet_planet
        "0x4bbb2000c80ff79c2aa3b8aa83ee69c103469181a19d01d7f3ee4313a8031",  # booklet_briqmas
        "0x35d3f5be7b3b06a2d02a539faecd45bf4a04644aee7290359bd595047929a92",  # booklet_fren_ducks
    ],

    sets_addresses=[
        "0x3f96949d14c65ec10e7544d93f298d0cb07c498ecb733774f1d4b2adf3ffb23",  # set_nft
        "0x4fa864a706e3403fd17ac8df307f22eafa21b778b73353abf69a622e47a2003",  # set_nft_ducks
        "0xe9b982bdcbed7fa60e5bbf733249ff58da9fe935067656e8175d694162df3",  # set_nft_sp
        "0x12a6eeb4a3eecaf16667e2b630963a4c215cdf3715fb271370a02ed6e8c1942",  # set_nft_briqmas
    ],

    sets_1155_addresses=[
        "0x433a83c97c083470a1e2f47e24cbc53c4a225f69ffc045580a7279e7f077c79",  # set_nft_1155_fren_ducks
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

MAINNET_DOJO = NetworkMetadata(
    id="starknet-mainnet-dojo",
    chain_id=StarknetChainId.MAINNET.value,
    storage_bucket="briq-bucket-prod-dojo",
    base_domain='briq.construction',

    briq_address="0x2417eb26d02947416ed0e9d99c7a023e3565fc895ee21a0a0ef88a524a665d6",
    factory_address="0x3374d4a1b4f8dc87bd680ddbd4f1181b3ec3cf5a8ef803bc4351603b063314f",

    box_addresses=[
        "0x73e3b5e6c7924f752a158c2b07f606bd5b885029da0ac1e3cde254985303f50",  # box_nft_sp
        "0x69699ce808b5459a3b652b5378f8c141e1dc79e10f4e7b486439fd989b7dfb1",  # box_nft_briqmas
    ],

    booklet_addresses=[
        "0x3311cdef78f70c1b13568e6dabda043c5e9d2736c0c02a35aa906d91d69836b",  # booklet_ducks
        "0x2fd50e1bdd7400a8fc97eb63aa4f3423a7ec72ebe78d413ce410ec60a35afea",  # booklet_starknet_planet
        "0x4bbb2000c80ff79c2aa3b8aa83ee69c103469181a19d01d7f3ee4313a8031",  # booklet_briqmas
        "0x35d3f5be7b3b06a2d02a539faecd45bf4a04644aee7290359bd595047929a92",  # booklet_fren_ducks
    ],

    sets_addresses=[
        "0x3f96949d14c65ec10e7544d93f298d0cb07c498ecb733774f1d4b2adf3ffb23",  # set_nft
        "0x4fa864a706e3403fd17ac8df307f22eafa21b778b73353abf69a622e47a2003",  # set_nft_ducks
        "0xe9b982bdcbed7fa60e5bbf733249ff58da9fe935067656e8175d694162df3",  # set_nft_sp
        "0x12a6eeb4a3eecaf16667e2b630963a4c215cdf3715fb271370a02ed6e8c1942",  # set_nft_briqmas
    ],

    sets_1155_addresses=[
        "0x433a83c97c083470a1e2f47e24cbc53c4a225f69ffc045580a7279e7f077c79",  # set_nft_1155_fren_ducks
    ],

    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy", storage_bucket="briq-bucket-prod-1")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
        'starknet-testnet-dojo': TESTNET_DOJO,
        'starknet-mainnet': MAINNET,
        'starknet-mainnet-dojo': MAINNET_DOJO,
    }[network]

