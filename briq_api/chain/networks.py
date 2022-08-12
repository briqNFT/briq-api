

from dataclasses import dataclass


@dataclass
class NetworkMetadata:
    id: str
    auction_address: str = ''
    box_address: str = ''
    briq_address: str = ''
    booklet_address: str = ''
    erc20_address: str = ''


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
    auction_address="0x04a97166c6718f85162f05270274ccede8e20e6aaa47a389f478d9df71ee6a95",
    box_address="0x07f4c8f5d2e70955bf9b4275abb48781049839dc0a45a3f7d0761c61d61811cc",
    briq_address="0x009c80aaf74330a0b56dddefc4e6bab33d03415e67a0092cc048b0d6fb2cc3dd",
    booklet_address="0x048580b27b4cb0ac15069ba2bf9a8586cb072f65dbcd4659a220a747f57f89e6",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
    }[network]
