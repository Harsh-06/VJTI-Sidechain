import json
from typing import List
from core import BlockHeader
from wallet import Wallet
import requests
from utils.logger import logger

class VJTIChainRelayer:
    def __init__(self, wallet: Wallet) -> None:
        self.wallet = wallet
        # TODO
        self.record_account_public_key = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE0tmjDG6v51ELMieRGuTfOgmfTe7BzNBsHQseqygX58+MQjNyjoOPkphghhYFpIFPzVORAI6Qief9lrncuWsOMg==' # The public key of the account, to which all transactions will be sent
        self.main_chain_url = 'http://localhost:9000'

    def write(self, block_header: BlockHeader) -> None:
        data = {
            'bounty': 1,
            'sender_public_key': self.wallet.public_key,
            'receiver_public_key': self.record_account_public_key,
            'message': VJTIChainRelayer.__get_message_for_block(block_header)
        }
        r = requests.post(self.main_chain_url + '/makeTransaction', json=data)
        tx_data = r.json()
        logger.debug(f"Relayer: Make Transaction returned {tx_data}")
        send_this = tx_data['send_this']
        sign_this = tx_data['sign_this']
        signed_string = self.wallet.sign(sign_this)
        self.__send_transaction(send_this, signed_string)

    def exists(self, block_header: BlockHeader) -> bool:
        message_for_block = VJTIChainRelayer.__get_message_for_block(block_header)
        data = {
            'public_key': self.record_account_public_key
        }
        r = requests.post(self.main_chain_url + '/transactionHistory', json=data)
        tx_history: List[str] = r.json()
        exists = False
        for tx in tx_history:
            tx = json.loads(tx)
            if tx['message'] == message_for_block:
                exists = True
                break
        return exists

    def __send_transaction(self, transaction, signature) -> None:
        data = {
            'transaction': transaction,
            'signature': signature
        }
        r = requests.post(self.main_chain_url + '/sendTransaction', json=data)
        logger.debug(f"Relayer: Send Transaction returned {r.text}")

    @staticmethod
    def __get_message_for_block(block_header: BlockHeader) -> str:
        return block_header.merkle_root
