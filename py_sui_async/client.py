import base64
import hashlib
from typing import Optional

import bip_utils
import requests
from fake_useragent import UserAgent
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey

from py_sui_async import exceptions
from py_sui_async.models import Network, Networks, WalletInfo, SignatureScheme, ExecuteType, StringAndBytes
from py_sui_async.nfts import NFT
from py_sui_async.rpc_methods import RPC
from py_sui_async.transactions import Transaction
from py_sui_async.wallet import Wallet


class Client:
    def __init__(self, mnemonic: Optional[str] = None, network: Network = Networks.Testnet,
                 derivation_path: str = "m/44'/784'/0'/0'/0'", proxy: Optional[str] = None,
                 check_proxy: bool = True) -> None:
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
                    your_ip = requests.get(
                        'http://eth0.me/', proxies={'http': self.proxy, 'https': self.proxy}, timeout=10
                    ).text.rstrip()
                    if your_ip not in proxy:
                        raise exceptions.InvalidProxy(f"Proxy doesn't work! Your IP is {your_ip}.")

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
            pub_key_bytes = public_key.bytes_
            address = "0x" + hashlib.blake2b(
                pub_key_bytes[0:33] if pub_key_bytes[0] == 0 else pub_key_bytes[0:34], digest_size=32
            ).hexdigest()

            self.account = WalletInfo(
                mnemonic=mnemonic, private_key=private_key, public_key=public_key, address=address
            )

        self.nfts = NFT(self)
        self.transactions = Transaction(self)
        self.wallet = Wallet(self)

    async def sign(self, tx_data: bytes) -> Optional[bytes]:
        indata = bytearray([0, 0, 0])
        indata.extend(tx_data)

        compound = bytearray([SignatureScheme.ED25519])
        signed = SigningKey(self.account.private_key.bytes_).sign(bytes(indata), encoder=Base64Encoder).signature
        compound.extend(base64.b64decode(signed))
        compound.extend(self.account.public_key.bytes_[1:])
        return base64.b64encode(bytes(compound))

    async def sign_and_execute(self, tx_bytes: StringAndBytes) -> Optional[dict]:
        signature = (await self.sign(tx_bytes.bytes_)).decode()
        request_type = ExecuteType.WaitForLocalExecution
        return await RPC.executeTransactionSerializedSig(
            client=self, tx_bytes=tx_bytes.str_, signature=signature, request_type=request_type
        )
