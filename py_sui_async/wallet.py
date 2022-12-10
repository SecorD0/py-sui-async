import logging
from typing import Optional

import aiohttp
from pretty_utils.type_functions.lists import split_list

from py_sui_async import exceptions
from py_sui_async.models import Balance, Coin, Nft, ObjectID
from py_sui_async.rpc_methods import RPC
from py_sui_async.utils import parse_type


class Wallet:
    def __init__(self, client):
        self.client = client

    async def balance(self, address: Optional[str] = None) -> Balance:
        balance = Balance(tokens={}, nfts={}, misc={})
        try:
            if not address:
                address = self.client.account.address

            response = await RPC.getObjectsOwnedByAddress(client=self.client, address=address)
            queries = [await RPC.getObject(client=self.client, object_id=obj['objectId'], get_json=True) for obj in
                       response['result']]
            query_list = split_list(queries, 200)
            objs = []
            for json_data in query_list:
                objs += await RPC.async_get(client=self.client, json_data=json_data)

            for obj in objs:
                obj_id = obj['result']['details']['reference']['objectId']
                obj_data = obj['result']['details']['data']
                obj_type = await parse_type(obj_data['type'])
                obj_fields = obj_data['fields']

                if obj_type.type == 'coin':
                    obj_id = ObjectID(id=obj_id, amount=obj_fields['balance'])
                    if obj_type.name == 'sui':
                        if balance.coin:
                            balance.coin.balance += obj_fields['balance']
                            balance.coin.object_ids.append(obj_id)

                        else:
                            balance.coin = Coin(name=obj_type.name, symbol=obj_type.symbol,
                                                package_id=obj_type.package_id,
                                                balance=obj_fields['balance'], object_ids=[obj_id])

                    else:
                        if obj_type.name in balance.tokens:
                            coin = balance.tokens[obj_type.name]
                            coin.balance += obj_fields['balance']
                            coin.object_ids.append(obj_id)

                        else:
                            balance.tokens[obj_type.name] = Coin(name=obj_type.name, symbol=obj_type.symbol,
                                                                 package_id=obj_type.package_id,
                                                                 balance=obj_fields['balance'], object_ids=[obj_id])

                elif 'nft' in obj_type.raw_type.lower():
                    balance.nfts[obj_id] = Nft(name=obj_fields['name'], description=obj_fields['description'],
                                               image_url=obj_fields['url'], object_id=obj_id)

                else:
                    balance.misc[obj_id] = obj_data

        except:
            logging.exception('balance')

        finally:
            return balance

    async def find_object_for_gas(self, gas_budget: int = 10_000, balance: Optional[Balance] = None) -> Optional[str]:
        if not balance:
            coin = None
            response = await RPC.getObjectsOwnedByAddress(client=self.client, address=self.client.account.address)
            queries = [await RPC.getObject(client=self.client, object_id=obj['objectId'], get_json=True) for obj in
                       response['result']]
            query_list = split_list(queries, 200)
            objs = []
            for json_data in query_list:
                objs += await RPC.async_get(client=self.client, json_data=json_data)

            for obj in objs:
                obj_id = obj['result']['details']['reference']['objectId']
                obj_data = obj['result']['details']['data']
                obj_type = await parse_type(obj_data['type'])
                obj_fields = obj_data['fields']
                if obj_type.type == 'coin' and obj_type.name == 'sui':
                    obj_id = ObjectID(id=obj_id, amount=obj_fields['balance'])
                    if coin:
                        coin.balance += obj_fields['balance']
                        coin.object_ids.append(obj_id)

                    else:
                        coin = Coin(name=obj_type.name, symbol=obj_type.symbol, package_id=obj_type.package_id,
                                    balance=obj_fields['balance'], object_ids=[obj_id])

        else:
            coin = balance.coin

        sorted_objects = sorted(coin.object_ids, key=lambda obj: obj.amount)
        for object_id in sorted_objects:
            if object_id.amount >= gas_budget:
                return object_id.id

    async def request_coins_from_faucet(self) -> Optional[dict]:
        if self.client.network.faucet:
            json_data = {
                "FixedAmountRequest": {"recipient": self.client.account.address}
            }

            async with aiohttp.ClientSession(trust_env=True, headers=self.client.headers) as session:
                async with session.post(self.client.network.faucet, proxy=self.client.proxy,
                                        json=json_data) as response:
                    if response.status <= 201:
                        return await response.json()

                    else:
                        raise exceptions.RPCException(response)

        else:
            raise exceptions.FaucetException("You didn't specify the faucet URL!")
