from typing import List
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from dataclasses import dataclass, field


@dataclass
class NetworkMetadata:
    id: str
    chain_id: int = 0
    storage_bucket: str = ''
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
    auction_address="0x033f840d4f7bfa20aaa128e5a69157355478d33182bea6039d55aae3ffb861e2",
    auction_ducks="0x04ef0bd475fb101cc1b5dc2c4fc9d11b4fa233cfa1876924ec84b2f3dcf32f75",
    box_address="0x043bafcb15f12c137229406f96735eba51018fe75e5330058479556bc77dfd94",
    briq_address="0x0068eb19445f96b3c3775fba757de89ee8f44fda42dc08173a501acacd97853f",
    booklet_address="0x018734a90e5df97235c0ff83f92174cf6f16ad3ec572e38e2e146e47c8878839",
    attributes_registry_address="0x06a780187cfd58ad6ce1279cb4291bcf4f8acb2806dc1dccc9aee8183a9c1c40",
    set_address="0x038bf557306ab58c7e2099036b00538b51b37bdad3b8abc31220001fb5139365",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_DOJO = NetworkMetadata(
    id="starknet-testnet-dojo",
    storage_bucket="briq-bucket-test-1",

    briq_address="0x3fc9bfbf5e373f5bf52b1c895885c85de76863772511c467df882ca44826962",
    factory_address="0x24081ab73c27537806ce23d93b40befd8946bdede1f031298a032ccb2b74d96",

    # briqmas
    box_address="0x10fda9480706cef65c9d7eb90a2ce32751ac80898fc826cc74e6331b781992a",
    # briqmas
    booklet_address="0x761a05da11813527b02f503000b74c0e83743e1f836111ca987772a19fca3bb",

    box_addresses=[
        "0x6e10789a603f768da43d9797dc97fc53ad4c3b52db504ff102be232aa8eb527",  # starknet_planet
        "0x10fda9480706cef65c9d7eb90a2ce32751ac80898fc826cc74e6331b781992a",  # briqmas
    ],

    booklet_addresses=[
        "0x748f4162442c60a6e228503e078ff8b003f331695bffda99c74e5a7bc235656",  # booklet_ducks
        "0x4e549e6a2e8401909ab03d20c9a6fbef4613a1354b74b0e52cf80fc4cdcc2e6",  # booklet_starknet_planet
        "0x761a05da11813527b02f503000b74c0e83743e1f836111ca987772a19fca3bb",  # booklet_briqmas
        "0x34b7c0de8199f5acc07fe3b95e009750ee32de6f341251e46a448210d4e700a",  # booklet_lil_ducks
        "0x22a626c03cb1320e31ed4deaa174088419697bf44f4e1fe2d7e1ecc61e1d607",  # booklet_frens_ducks
    ],

    sets_addresses=[
        "0x34fcb874cbc85d0a6f8c473d433e9ebd0bccfa76ad75232945a1f0115b62ba1",  # set_nft
        "0x765fca82c4690a15c8c33985b7045ec8f8fdd1a7cba231a1c5f3a9c9767adc8",  # set_nft_ducks
        "0x30e11394a3c0e2fd712b0bd161027c49d96df1a010693c3f2794428b0b03df9",  # set_nft_sp
        "0x774c404feeb97675c47145140a0f8d92c70f02d52a4aa640c11064f1d9380a3",  # set_nft_briqmas
    ],

    sets_1155_addresses=[
        "0x2f888a745a97123db6265a1db9f09a47d59f47e223dd272a3223e652bde806a",  # set_nft_1155_lil_ducks
        "0x4f72b6668def25e048f8877e4d200602dd90d10cb1bedfba5758a67e3c7da13",  # set_nft_1155_frens_ducks
    ],

    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)


MAINNET = NetworkMetadata(
    id="starknet-mainnet",
    chain_id=StarknetChainId.MAINNET.value,
    storage_bucket="briq-bucket-prod-1",
    auction_address="0x01712e3e3f133b26d65a3c5aaae78e7405dfca0a3cfe725dd57c4941d9474620",
    auction_ducks="0x00b9bb7650a88f7e375ae8d31d48b4d4f13c6c34344839837d7dae7ffcdd3df0",
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
