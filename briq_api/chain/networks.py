

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
    auction_address="0x0344c97a38c9b5f632e0f1de386402ff0e3ebcf6878a65f588aa4375f9750c00",
    box_address="0x041b4b40491788813ba1c830c8e0e7e97b10a604d9dce25259f50352e7ad8b09",
    briq_address="0x0206a3d41d18e634f1492621dc42144c7dce52530bc90150fe8bcddef7011b4d",
    booklet_address="0x010c5fc9e7ebafe1bb260aa28f23ab93295b59ca5e1e7875c35338968c5a4233",
    attributes_registry_address="0x0389f0a5146eef8d67ee90998eb7b0d51744074a5b7526a9a6c477185c5f93b6",
    set_address="0x074fe9c7050d647cb80b5a993c6f532c0150734a69ebe1973c75916a6d808e54",
    erc20_address="0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
)

TESTNET_LEGACY = NetworkMetadata(id="starknet-testnet-legacy")


def get_network_metadata(network: str):
    return {
        'localhost': DEVNET,
        'starknet-testnet': TESTNET,
    }[network]
