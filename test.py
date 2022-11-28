import asyncio
import os
from typing import Optional

from dotenv import load_dotenv

from py_sui_async.client import Client
from py_sui_async.models import Nft


class Test:
    @staticmethod
    async def print_balance(balance):
        print(f'''Balance instance:
{balance}

Coin:
{balance.coin}''')

        if balance.tokens:
            print(f'\nTokens ({len(balance.tokens)}):')
            for obj_id, value in balance.tokens.items():
                print(obj_id, value)

        if balance.nfts:
            print(f'\nNFTs ({len(balance.nfts)}):')
            for obj_id, value in balance.nfts.items():
                print(obj_id, value)

        if balance.misc:
            print(f'\nMiscellaneous ({len(balance.misc)}):')
            for obj_id, value in balance.misc.items():
                print(obj_id, value)

    @staticmethod
    async def balance(address: str):
        """Show balance."""
        client = Client('')

        balance = await client.wallet.balance(address)

        await Test.print_balance(balance)
        print('----------------------------------------------------------------------------')

    @staticmethod
    async def generate_wallet():
        client = Client()
        print(client.account)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def request_sui_coins():
        client = Client(mnemonic, proxy)
        print(client.account)

        print(await client.wallet.request_coins_from_faucet())
        await Test.my_balance()

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def my_balance():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        await Test.print_balance(balance)
        print('----------------------------------------------------------------------------')

    @staticmethod
    async def mint_example_nft():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print()

        print(await client.nfts.mint_example_nft())
        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def mint_wizard_nft():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print()

        nft = Nft(arguments=["Wizard Land", "Expanding The Magic Land",
                             "https://gateway.pinata.cloud/ipfs/QmYfw8RbtdjPAF3LrC6S3wGVwWgn6QKq4LGS4HFS55adU2?w=800&h=450&c=crop"])
        await client.nfts.mint(nft=nft)
        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def mint_bluemove_nft():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print()
        arguments = ['0x081e876200a657e173397f722aba3b6628c6d270', 1]
        await client.transactions.move_call(package_object_id='0x3c2468cdc0288983f099a52fc6f5b43e4ed0c959',
                                            module='bluemove_launchpad', function='mint_with_quantity',
                                            type_arguments=[],
                                            arguments=arguments, gas_budget=50_000)

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def send_coin():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        print(balance.coin)

        print(await client.transactions.send_coin(client.account.address, 100_000))

        balance = await client.wallet.balance()
        print(balance.coin)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def send_token(token: str):
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        print(balance.tokens[token])

        print(await client.transactions.send_token(balance.tokens[token], client.account.address, 10_000))

        balance = await client.wallet.balance()
        print(balance.coin)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def send_nft(nft: str):
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print(await client.transactions.send_nft(balance.nfts[nft], client.account.address))

        balance = await client.wallet.balance()
        for obj_id, value in balance.nfts.items():
            print(obj_id, value)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def merge_coin():
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        print(balance.coin)

        print(await client.transactions.merge_coin(balance.coin))

        balance = await client.wallet.balance()
        print(balance.coin)

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def merge_token(token: str):
        client = Client(mnemonic, proxy)
        print(client.account)

        balance = await client.wallet.balance()
        print(balance.tokens[token])

        print(await client.transactions.merge_coin(balance.tokens[token]))

        balance = await client.wallet.balance()
        print(balance.tokens[token])

        print('----------------------------------------------------------------------------')

    @staticmethod
    async def history(address: Optional[str] = None):
        if address:
            client = Client('')

        else:
            client = Client(mnemonic, proxy)
            print(client.account)

        history = await client.transactions.history(address)
        print(f'Incoming ({len(history.incoming)}):')
        for tx in history.incoming:
            print(tx)

        print()

        print(f'Outgoing ({len(history.outgoing)}):')
        for tx in history.outgoing:
            print(tx)

        print('----------------------------------------------------------------------------')


if __name__ == '__main__':
    load_dotenv()
    mnemonic = str(os.getenv('MNEMONIC'))
    proxy = str(os.getenv('PROXY'))
    test = Test()
    asyncio.run(test.balance('0xc4173a804406a365e69dfb297d4eaaf002546ebd'))
    asyncio.run(test.generate_wallet())
    asyncio.run(test.request_sui_coins())
    asyncio.run(test.my_balance())
    asyncio.run(test.mint_example_nft())
    asyncio.run(test.mint_wizard_nft())
    asyncio.run(test.mint_bluemove_nft())
    asyncio.run(test.send_coin())
    asyncio.run(test.send_token('usdt'))
    asyncio.run(test.send_nft('0x1c47664b9b12fca8ede96726b6d90c854ae512a7'))
    asyncio.run(test.merge_coin())
    asyncio.run(test.merge_token('usdt'))
    asyncio.run(test.history())
    asyncio.run(test.history('0x0f2df809112256ec9068c2663bc4901c8a1b3ce7'))
