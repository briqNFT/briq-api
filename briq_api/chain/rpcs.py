import os

alchemy_endpoint = {
    'starknet-testnet': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-testnet-dojo': "https://starknet-goerli.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_TESTNET") or ""),
    'starknet-mainnet': "https://starknet-mainnet.g.alchemy.com/v2/" + (os.getenv("ALCHEMY_API_KEY_MAINNET") or "")
}
