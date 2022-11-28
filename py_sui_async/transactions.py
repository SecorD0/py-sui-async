import base64
import logging
from typing import Optional, List

from py_sui_async import exceptions
from py_sui_async.models import Types, History, Tx, Coin, Nft
from py_sui_async.rpc_methods import RPC


class Transaction:
    def __init__(self, client):
        self.client = client

    async def history(self, address: Optional[str] = None) -> History:
        history = History(incoming=[], outgoing=[])
        try:
            if not address:
                address = self.client.account.address

            json_data = [
                await RPC.getTransactions(client=self.client, query={'ToAddress': address}, cursor=None, limit=None,
                                          descending_order=True, get_json=True),
                await RPC.getTransactions(client=self.client, query={'FromAddress': address}, cursor=None, limit=None,
                                          descending_order=True, get_json=True),
            ]
            response = await RPC.send_request(client=self.client, json_data=json_data)
            try:
                incoming_txs = response[0]['result']['data']
                json_data = [await RPC.getTransaction(client=self.client, digest=tx, get_json=True) for tx in
                             incoming_txs]
                incoming_txs = [incoming_tx['result'] for incoming_tx in
                                await RPC.send_request(client=self.client, json_data=json_data)]
                for incoming_tx in incoming_txs:
                    certificate = incoming_tx['certificate']
                    data = certificate['data']
                    history.incoming.append(Tx(digest=certificate['transactionDigest'],
                                               status=incoming_tx['effects']['status']['status'],
                                               timestamp=int(incoming_tx['timestamp_ms'] / 1000),
                                               transactions=data['transactions'], sender=address, recipients=None,
                                               raw_dict=incoming_tx))
            except:
                pass

            try:
                outgoing_txs = response[1]['result']['data']
                json_data = [await RPC.getTransaction(client=self.client, digest=tx, get_json=True) for tx in
                             outgoing_txs]
                outgoing_txs = [outgoing_tx['result'] for outgoing_tx in
                                await RPC.send_request(client=self.client, json_data=json_data)]
                for outgoing_tx in outgoing_txs:
                    certificate = outgoing_tx['certificate']
                    data = certificate['data']
                    history.outgoing.append(Tx(digest=certificate['transactionDigest'],
                                               status=outgoing_tx['effects']['status']['status'],
                                               timestamp=int(outgoing_tx['timestamp_ms'] / 1000),
                                               transactions=data['transactions'], sender=data['sender'],
                                               recipients=[address], raw_dict=outgoing_tx))

            except:
                pass

        except:
            logging.exception('history')

        finally:
            return history

    async def move_call(self, package_object_id: Types.ObjectID, module: str, function: str,
                        type_arguments: Optional[List[Types.TypeTag]], arguments: List[Types.SuiJsonValue],
                        gas_budget: int = 1_000) -> Optional[dict]:
        gas = await self.client.wallet.find_object_for_gas(gas_budget=gas_budget)
        if not gas:
            raise exceptions.InsufficientGas()

        response = await RPC.moveCall(client=self.client, signer=self.client.account.address,
                                      package_object_id=package_object_id, module=module, function=function,
                                      type_arguments=type_arguments, arguments=arguments, gas=gas,
                                      gas_budget=gas_budget)
        tx_bytes = base64.b64decode(str(response['result']['txBytes']))
        return await self.client.sign_and_execute_transaction(tx_bytes)

    async def merge_coin(self, coin: Coin) -> Optional[List[dict]]:
        responses = []
        try:
            gas_budget = 1_000
            gas = await self.client.wallet.find_object_for_gas(gas_budget=gas_budget)
            if not gas:
                raise exceptions.InsufficientGas()

            if coin.object_ids[0].id == gas:
                primary_coin = coin.object_ids[1].id

            else:
                primary_coin = coin.object_ids[0].id

            objects_to_merge = [object_id.id for object_id in coin.object_ids]
            objects_to_merge.remove(primary_coin)
            if gas in objects_to_merge:
                objects_to_merge.remove(gas)

            for object_id in objects_to_merge:
                response = await RPC.mergeCoins(client=self.client, signer=self.client.account.address,
                                                primary_coin=primary_coin, coin_to_merge=object_id, gas=gas,
                                                gas_budget=gas_budget)
                tx_bytes = base64.b64decode(str(response['result']['txBytes']))
                response = await self.client.sign_and_execute_transaction(tx_bytes)
                responses.append(response)

        except:
            logging.exception('merge_coin')

        finally:
            return responses

    async def send_coin(self, recipient: Types.SuiAddress, amount: int) -> Optional[dict]:
        balance = await self.client.wallet.balance()
        gas_budget = 1_000
        gas = await self.client.wallet.find_object_for_gas(gas_budget=gas_budget, balance=balance)
        if not gas:
            raise exceptions.InsufficientGas()

        input_coins = [object_id.id for object_id in sorted(balance.coin.object_ids, key=lambda obj: obj.amount)]
        input_coins.remove(gas)
        input_coins = [gas] + input_coins
        response = await RPC.paySui(client=self.client, signer=self.client.account.address, input_coins=input_coins,
                                    recipients=[recipient], amounts=[amount], gas_budget=gas_budget)
        tx_bytes = base64.b64decode(str(response['result']['txBytes']))
        return await self.client.sign_and_execute_transaction(tx_bytes)

    async def send_token(self, token: Optional[Coin], recipient: Types.SuiAddress, amount: int) -> Optional[dict]:
        balance = await self.client.wallet.balance()
        if token.name in balance.tokens:
            gas_budget = 1_000
            gas = await self.client.wallet.find_object_for_gas(gas_budget=gas_budget, balance=balance)
            if not gas:
                raise exceptions.InsufficientGas()

            input_coins = [object_id.id for object_id in balance.tokens[token.name].object_ids]
            response = await RPC.pay(client=self.client, signer=self.client.account.address, input_coins=input_coins,
                                     recipients=[recipient], amounts=[amount], gas=gas, gas_budget=gas_budget)
            tx_bytes = base64.b64decode(str(response['result']['txBytes']))
            return await self.client.sign_and_execute_transaction(tx_bytes)

        else:
            raise exceptions.NoSuchToken('There is no such token!')

    async def send_nft(self, nft: Optional[Nft], recipient: Types.SuiAddress) -> Optional[dict]:
        gas_budget = 1_000
        gas = await self.client.wallet.find_object_for_gas(gas_budget=gas_budget)
        if not gas:
            raise exceptions.InsufficientGas()

        response = await RPC.transferObject(client=self.client, signer=self.client.account.address,
                                            object_id=nft.object_id, recipient=recipient, gas=gas,
                                            gas_budget=gas_budget)
        tx_bytes = base64.b64decode(str(response['result']['txBytes']))
        return await self.client.sign_and_execute_transaction(tx_bytes)
