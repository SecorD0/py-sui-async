from dataclasses import dataclass
from typing import Optional, List, Dict, Union

from pretty_utils.type_functions.classes import AutoRepr


class SignatureScheme:
    ED25519 = 0
    Secp256k1 = 1


class ExecuteType:
    ImmediateReturn = 'ImmediateReturn'
    WaitForTxCert = 'WaitForTxCert'
    WaitForEffectsCert = 'WaitForEffectsCert'
    WaitForLocalExecution = 'WaitForLocalExecution'


@dataclass
class Network:
    rpc: str
    explorer: Optional[str] = None
    faucet: Optional[str] = None


class Networks:
    Devnet = Network(rpc='https://fullnode.devnet.sui.io/', explorer='https://explorer.sui.io/{}?network=devnet',
                     faucet='https://faucet.devnet.sui.io/gas')
    Staging = Network(rpc='https://fullnode.staging.sui.io/', faucet='https://faucet.staging.sui.io/gas')
    Testnet = Network(rpc='https://fullnode.testnet.sui.io/', explorer='https://explorer.sui.io/{}?network=testnet',
                      faucet='https://faucet.testnet.sui.io/gas')


@dataclass
class StringAndBytes:
    str_: str
    bytes_: bytes


@dataclass
class WalletInfo:
    mnemonic: str
    private_key: StringAndBytes
    public_key: StringAndBytes
    address: str


@dataclass
class Tx:
    digest: str
    status: str
    timestamp: int
    sender: str
    recipients: Optional[List[str]]
    transactions: List[dict]
    raw_dict: dict


@dataclass
class History:
    incoming: List[Tx]
    outgoing: List[Tx]


class ObjectID(AutoRepr):
    def __init__(self, id: str, amount: Union[int, str]) -> None:
        self.id: str = id
        self.amount: int = int(amount)


class Coin(AutoRepr):
    def __init__(self, name: str, symbol: str, package_id: str, balance: Optional[float] = 0.0,
                 object_ids: Optional[List[ObjectID]] = None) -> None:
        self.name: str = name
        self.symbol: str = symbol
        self.package_id: str = package_id
        self.balance: Optional[float] = balance
        self.object_ids: Optional[List[ObjectID]] = object_ids or []


@dataclass
class ObjectType:
    raw_type: str
    package_id: Optional[str] = None
    module: Optional[str] = None
    structure: Optional[Union[str, Coin]] = None


class Nft(AutoRepr):
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None, image_url: Optional[str] = None,
                 arguments: Optional[list] = None, object_id: Optional[str] = None) -> None:
        if arguments:
            self.name: Optional[str] = arguments[0]
            self.description: Optional[str] = arguments[1]
            self.image_url: Optional[str] = arguments[2]
            self.arguments: Optional[list] = arguments

        else:
            self.name: Optional[str] = name
            self.description: Optional[str] = description
            self.image_url: Optional[str] = image_url
            self.arguments: Optional[list] = [self.name, self.description, self.image_url]
        self.object_id: Optional[str] = object_id


@dataclass
class Balance:
    coin: Optional[Coin] = None
    tokens: Optional[Dict[str, Coin]] = None
    nfts: Optional[Dict[str, Nft]] = None
    misc: Optional[Dict[str, dict]] = None
