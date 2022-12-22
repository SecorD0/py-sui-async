import base64
import hashlib
from typing import Optional

import bip_utils
import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey
from pretty_utils.type_functions.strings import text_between

from py_sui_async import exceptions
from py_sui_async.models import Network, Networks, WalletInfo, SignatureScheme, ExecuteType, StringAndBytes
from py_sui_async.nfts import NFT
from py_sui_async.rpc_methods import RPC
from py_sui_async.transactions import Transaction
from py_sui_async.wallet import Wallet


class Client:
    def __init__(self, mnemonic: Optional[str] = None, proxy: Optional[str] = None, network: Network = Networks.Testnet,
                 check_proxy: bool = True, derivation_path: str = "m/44'/784'/0'/0'/0'") -> None:
        self.network = network
        self.derivation_path = derivation_path

        self.proxy = proxy
        self.headers = {
            'authority': self.network.rpc.replace('https:', '').replace('/', ''),
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'chrome-extension://opcgpfmipidbgpenhmajoajpbobppdil',
            'user-agent': UserAgent().chrome,
            'Content-type': 'application/json'
        }

        if self.proxy:
            try:
                if 'http' not in self.proxy:
                    self.proxy = f'http://{self.proxy}'

                if check_proxy:
                    response = requests.get('https://whoer.net/', proxies={'http': self.proxy, 'https': self.proxy})
                    if '@' in self.proxy:
                        proxy = text_between(self.proxy, '@', ':')
                    else:
                        proxy = text_between(self.proxy, end=':')

                    if proxy not in response.text:
                        soup = BS(response.text, 'html.parser')
                        your_ip = soup.find('strong', class_='your-ip').get_text(strip=True)
                        raise exceptions.InvalidProxy(f"Proxy doesn't work! Your IP is {your_ip}")

            except Exception as e:
                raise exceptions.InvalidProxy(str(e))

        self.account: Optional[WalletInfo] = None
        if mnemonic or mnemonic is None:
            if mnemonic is None:
                mnemonic = bip_utils.Bip39MnemonicGenerator().FromWordsNumber(
                    bip_utils.Bip39WordsNum.WORDS_NUM_12).ToStr()

            bip39_seed = bip_utils.Bip39SeedGenerator(mnemonic).Generate()
            bip32_ctx = bip_utils.Bip32Slip10Ed25519.FromSeed(bip39_seed)
            bip32_der_ctx = bip32_ctx.DerivePath(self.derivation_path)

            private_key = bip32_der_ctx.PrivateKey().Raw()
            private_key = StringAndBytes(str_="0x" + str(private_key), bytes_=private_key.ToBytes())
            public_key = bip32_der_ctx.PublicKey().RawCompressed()
            public_key = StringAndBytes(str_="0x" + str(public_key), bytes_=public_key.ToBytes())
            address = "0x" + hashlib.sha3_256(public_key.bytes_).digest().hex()[:40]

            self.account = WalletInfo(mnemonic=mnemonic, private_key=private_key, public_key=public_key,
                                      address=address)

        self.nfts = NFT(self)
        self.transactions = Transaction(self)
        self.wallet = Wallet(self)

    async def sign_data(self, tx_data: bytes) -> Optional[bytes]:
        indata = bytearray([0, 0, 0])
        indata.extend(tx_data)

        compound = bytearray([SignatureScheme.ED25519])
        signed = SigningKey(self.account.private_key.bytes_).sign(bytes(indata), encoder=Base64Encoder).signature
        compound.extend(base64.b64decode(signed))
        compound.extend(self.account.public_key.bytes_[1:])
        return base64.b64encode(bytes(compound))

    async def sign_and_execute_transaction(self, tx_bytes: StringAndBytes) -> Optional[dict]:
        signature = (await self.sign_data(tx_bytes.bytes_)).decode()
        request_type = ExecuteType.WaitForLocalExecution
        return await RPC.executeTransactionSerializedSig(client=self, tx_bytes=tx_bytes.str_, signature=signature,
                                                         request_type=request_type)
