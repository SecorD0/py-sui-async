from typing import Optional

from py_sui_async.models import Nft


class NFT:
    def __init__(self, client):
        self.client = client

    async def mint(self, nft: Nft) -> Optional[dict]:
        return await self.client.transactions.move_call(package_object_id='0x2', module='devnet_nft', function='mint',
                                                        type_arguments=[],
                                                        arguments=[nft.name, nft.description, nft.image_url],
                                                        gas_budget=10_000)

    async def mint_example_nft(self) -> Optional[dict]:
        nft = Nft(name='Example NFT', description='An NFT created by Sui Wallet',
                  image_url='ipfs://QmZPWWy5Si54R3d26toaqRiqvCH7HkGdXkxwUgCm2oKKM2?filename=img-sq-01.png')
        return await self.mint(nft)
