from pydantic import BaseModel


class SetRID(BaseModel):
    """
    Though we can expect token IDs to be relatively unique,
    for easier handling we'll store chain information.
    """
    chain_id: str  # NB: this is not the same as the 'chain ID', since we'll plan ahead for cross-chain support.
    token_id: str
