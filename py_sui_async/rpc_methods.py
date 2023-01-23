import uuid
from typing import Optional, List, Union

import aiohttp

from py_sui_async import exceptions
from py_sui_async.models import Types, ObjectType


class RPC:
    @staticmethod
    async def make_json(method: str, params: Optional[list] = None, request_id: Optional[str] = None):
        return {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": request_id or str(uuid.uuid4()),
        }

    @staticmethod
    async def async_post(client, json_data: Union[dict, list]) -> Optional[dict]:
        async with aiohttp.ClientSession(headers=client.headers) as session:
            async with session.post(client.network.rpc, proxy=client.proxy, json=json_data) as response:
                if response.status <= 201:
                    json_dict = await response.json()
                    if 'error' in json_dict:
                        error = json_dict['error']
                        raise exceptions.RPCException(response=response, code=error['code'], message=error['message'])

                    return json_dict

                raise exceptions.RPCException(response=response)

    @staticmethod
    async def batchTransaction(client, signer: Types.SuiAddress,
                               single_transaction_params: List[Types.RPCTransactionRequestParams],
                               gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                               get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, single_transaction_params, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_batchTransaction', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def dryRunTransaction(client, tx_bytes: Types.Base64, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [tx_bytes]
        json_data = await RPC.make_json(method='sui_dryRunTransaction', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def executeTransaction(client, tx_bytes: Types.Base64, sig_scheme: Types.SignatureScheme,
                                 signature: Types.Base64, pub_key: Types.Base64,
                                 request_type: Types.ExecuteTransactionRequestType,
                                 get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [tx_bytes, sig_scheme, signature, pub_key, request_type]
        json_data = await RPC.make_json(method='sui_executeTransaction', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def executeTransactionSerializedSig(client, tx_bytes: Types.Base64, signature: Types.Base64,
                                              request_type: Types.ExecuteTransactionRequestType,
                                              get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [tx_bytes, signature, request_type]
        json_data = await RPC.make_json(method='sui_executeTransactionSerializedSig', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getAllBalances(client, owner: Types.SuiAddress, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [owner]
        json_data = await RPC.make_json(method='sui_getAllBalances', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getAllCoins(client, owner: Types.SuiAddress, cursor: Types.ObjectID,
                          limit: Optional[int], get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [owner, cursor, limit]
        json_data = await RPC.make_json(method='sui_getAllCoins', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getBalance(client, owner: Types.SuiAddress, coin_type: Union[str, ObjectType],
                         get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [owner, coin_type.raw_type if isinstance(coin_type, ObjectType) else coin_type]
        json_data = await RPC.make_json(method='sui_getBalance', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getCoinMetadata(client, coin_type: Union[str, ObjectType],
                              get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [coin_type.raw_type if isinstance(coin_type, ObjectType) else coin_type]
        json_data = await RPC.make_json(method='sui_getCoinMetadata', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getCoins(client, owner: Types.SuiAddress, coin_type: Union[str, ObjectType], cursor: Types.ObjectID,
                       limit: Optional[int], get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [owner, coin_type.raw_type if isinstance(coin_type, ObjectType) else coin_type, cursor, limit]
        json_data = await RPC.make_json(method='sui_getCoins', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getCommitteeInfo(client, epoch: int, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [epoch]
        json_data = await RPC.make_json(method='sui_getCommitteeInfo', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getDynamicFieldObject(client, parent_object_id: Types.ObjectID, name: str,
                                    get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [parent_object_id, name]
        json_data = await RPC.make_json(method='sui_getDynamicFieldObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getDynamicFields(client, parent_object_id: Types.ObjectID, cursor: Types.ObjectID,
                               limit: Optional[int], get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [parent_object_id, cursor, limit]
        json_data = await RPC.make_json(method='sui_getDynamicFields', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getEvents(client, query: Types.EventQuery, cursor: Types.EventID, limit: int,
                        descending_order: bool = False, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [query, cursor, limit, descending_order]
        json_data = await RPC.make_json(method='sui_getEvents', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getMoveFunctionArgTypes(client, package: Types.ObjectID, module: str, function: str,
                                      get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [package, module, function]
        json_data = await RPC.make_json(method='sui_getMoveFunctionArgTypes', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getNormalizedMoveFunction(client, package: Types.ObjectID, module: str, function: str,
                                        get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [package, module, function]
        json_data = await RPC.make_json(method='sui_getNormalizedMoveFunction', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getNormalizedMoveModule(client, package: Types.ObjectID, module_name: str,
                                      get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [package, module_name]
        json_data = await RPC.make_json(method='sui_getNormalizedMoveModule', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getNormalizedMoveModulesByPackage(client, package: Types.ObjectID,
                                                get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [package]
        json_data = await RPC.make_json(method='sui_getNormalizedMoveModulesByPackage', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getNormalizedMoveStruct(client, package: Types.ObjectID, module_name: str,
                                      struct_name: str, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [package, module_name, struct_name]
        json_data = await RPC.make_json(method='sui_getNormalizedMoveStruct', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getObject(client, object_id: Types.ObjectID, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [object_id]
        json_data = await RPC.make_json(method='sui_getObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getObjectsOwnedByAddress(client, address: Types.SuiAddress,
                                       get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [address]
        json_data = await RPC.make_json(method='sui_getObjectsOwnedByAddress', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getObjectsOwnedByObject(client, object_id: Types.ObjectID,
                                      get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [object_id]
        json_data = await RPC.make_json(method='sui_getObjectsOwnedByObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getRawObject(client, object_id: Types.ObjectID, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [object_id]
        json_data = await RPC.make_json(method='sui_getRawObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getSuiSystemState(client, get_json: bool = False) -> Optional[Union[dict, list]]:
        json_data = await RPC.make_json(method='sui_getSuiSystemState')
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTotalSupply(client, coin_type: Union[str, ObjectType],
                             get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [coin_type.raw_type if isinstance(coin_type, ObjectType) else coin_type]
        json_data = await RPC.make_json(method='sui_getTotalSupply', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTotalTransactionNumber(client, get_json: bool = False) -> Optional[Union[dict, list]]:
        json_data = await RPC.make_json(method='sui_getTotalTransactionNumber')
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTransaction(client, digest: Types.TransactionDigest,
                             get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [digest]
        json_data = await RPC.make_json(method='sui_getTransaction', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTransactionAuthSigners(client, digest: Types.TransactionDigest,
                                        get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [digest]
        json_data = await RPC.make_json(method='sui_getTransactionAuthSigners', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTransactions(client, query: Types.TransactionQuery, cursor: Optional[Types.TransactionDigest],
                              limit: Optional[int], descending_order: bool = False,
                              get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [query, cursor, limit, descending_order]
        json_data = await RPC.make_json(method='sui_getTransactions', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def getTransactionsInRange(client, start: int, end: int,
                                     get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [start, end]
        json_data = await RPC.make_json(method='sui_getTransactionsInRange', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def mergeCoins(client, signer: Types.SuiAddress, primary_coin: Types.ObjectID,
                         coin_to_merge: Types.ObjectID, gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                         get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, primary_coin, coin_to_merge, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_mergeCoins', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def moveCall(client, signer: Types.SuiAddress, package_object_id: Types.ObjectID, module: str,
                       function: str, type_arguments: Optional[List[Types.TypeTag]],
                       arguments: List[Types.SuiJsonValue],
                       gas: Optional[Types.ObjectID] = None, gas_budget: int = 10_000,
                       get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, package_object_id, module, function, type_arguments, arguments, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_moveCall', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def pay(client, signer: Types.SuiAddress, input_coins: List[Types.ObjectID],
                  recipients: List[Types.SuiAddress], amounts: List[int], gas: Optional[Types.ObjectID] = None,
                  gas_budget: int = 1_000, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, input_coins, recipients, amounts, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_pay', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def payAllSui(client, signer: Types.SuiAddress, input_coins: List[Types.ObjectID],
                        recipient: Types.SuiAddress, gas_budget: int = 1_000,
                        get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, input_coins, recipient, gas_budget]
        json_data = await RPC.make_json(method='sui_payAllSui', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def paySui(client, signer: Types.SuiAddress, input_coins: List[Types.ObjectID],
                     recipients: List[Types.SuiAddress], amounts: List[int], gas_budget: int = 1_000,
                     get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, input_coins, recipients, amounts, gas_budget]
        json_data = await RPC.make_json(method='sui_paySui', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def publish(client, sender: Types.SuiAddress, compiled_modules: List[Types.Base64],
                      gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                      get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [sender, compiled_modules, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_publish', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def splitCoin(client, signer: Types.SuiAddress, coin_object_id: Types.ObjectID,
                        split_amounts: List[int], gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                        get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, coin_object_id, split_amounts, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_splitCoin', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def splitCoinEqual(client, signer: Types.SuiAddress, coin_object_id: Types.ObjectID,
                             split_count: int, gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                             get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, coin_object_id, split_count, gas, gas_budget]
        json_data = await RPC.make_json(method='sui_splitCoinEqual', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def subscribeEvent(client, filter: Types.EventFilter, get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [filter]
        json_data = await RPC.make_json(method='sui_subscribeEvent', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def transferObject(client, signer: Types.SuiAddress, object_id: Types.ObjectID, recipient: Types.SuiAddress,
                             gas: Optional[Types.ObjectID] = None, gas_budget: int = 1_000,
                             get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, object_id, gas, gas_budget, recipient]
        json_data = await RPC.make_json(method='sui_transferObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def transferSui(client, signer: Types.SuiAddress, sui_object_id: Types.ObjectID, gas_budget: int,
                          recipient: Types.SuiAddress, amount: int,
                          get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [signer, sui_object_id, gas_budget, recipient, amount]
        json_data = await RPC.make_json(method='sui_transferSui', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)

    @staticmethod
    async def tryGetPastObject(client, object_id: Types.ObjectID, version: Types.SequenceNumber,
                               get_json: bool = False) -> Optional[Union[dict, list]]:
        params = [object_id, version]
        json_data = await RPC.make_json(method='sui_tryGetPastObject', params=params)
        if get_json:
            return json_data

        return await RPC.async_post(client=client, json_data=json_data)
