import math
from typing import List

from requests.api import head
from core import BlockHeader, Block, Chain, Transaction
from wallet import Wallet
import requests
from utils.logger import logger
from utils import constants

class VJTIChainRelayer:
    def __init__(self, wallet: Wallet) -> None:
        self.wallet = wallet
        
        # Side Chain Block Headers are written to VJTI chain after these many blocks
        self.side_chain_to_main_chain_ratio = 5 # should be > 1
        self.main_chain_mining_interval = 30
        self.side_chain_mining_interval = constants.MINING_INTERVAL_THRESHOLD # should be > main_chain_mining_interval
        self.main_chain_url = 'http://localhost:9001'
        self.main_chain_max_message_size = 128
        # TODO
        self.record_account_public_key = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAENvU/ThGGxgw++yDdyYq4FBCKJMcIYcaUp+Vbpzib0hwCSOTiTwu2/rhJReZv5S/PuTiuaGAeFnpOdCXXT2X1TQ==' # The public key of the account, to which all transactions will be sent

        send_ratio = self.side_chain_to_main_chain_ratio # > 1, always
        # as side chain will not send all blocks, but only periodically = side_chain_to_main_chain_ratio
        mine_ratio = self.main_chain_mining_interval / self.side_chain_mining_interval # > 1, always
        # as side chain will mine faster than main chain
        X = math.ceil(send_ratio / mine_ratio) # our side chain will write on every X main chain block on average

        self.num_blocks_to_check_for = math.ceil((X + 1) * mine_ratio)

    def chain_is_ok(self, chain: Chain) -> bool:
        header_list = chain.header_list

        if len(header_list) < self.num_blocks_to_check_for:
            # it is possible that there may have been no writes
            return True
        
        else:
            for header in header_list[-self.num_blocks_to_check_for:]:
                if self.__should_exist(header):
                    return self.__exists(header)
        return False

    def chain_is_trusted_upto_block(self, chain: Chain) -> BlockHeader:
        for header in reversed(chain.header_list):
            if self.__should_exist(header):
                if self.__exists(header):
                    return header

    def num_untrusted_blocks(self, chain: Chain) -> BlockHeader:
        latest_trusted_block = self.chain_is_trusted_upto_block(chain)
        header_list = chain.header_list
        l = len(header_list)
        return l - header_list.index(latest_trusted_block) - 1

    def new_block(self, block: Block) -> bool:
        # return True
        block_header = block.header
        if self.__should_exist(block_header):
            data = {
                'bounty': 1,
                'sender_public_key': self.wallet.public_key,
                'receiver_public_key': self.record_account_public_key,
                'message': self.__get_message_for_block(block_header)
            }
            r = requests.post(self.main_chain_url + '/makeTransaction', json=data)
            tx_data = r.json()
            logger.debug(f"Relayer: Make Transaction returned: {tx_data}")
            transaction = tx_data['send_this']
            sign_this = tx_data['sign_this']
            signed_string = self.wallet.sign(sign_this)
            
            data = {
                'transaction': transaction,
                'signature': signed_string
            }
            r = requests.post(self.main_chain_url + '/sendTransaction', json=data)
            logger.debug(f"Relayer: Send Transaction returned: {r.text}")
            return r.text == "Done"

    def __exists(self, block_header: BlockHeader) -> bool:
        # return True
        message_for_block = self.__get_message_for_block(block_header)
        data = {
            'public_key': self.record_account_public_key
        }
        r = requests.post(self.main_chain_url + '/transactionHistory', json=data)
        tx_history: List[str] = r.json()
        exists = False
        for tx in tx_history:
            tx = Transaction.from_json(tx).object()
            if tx.message == message_for_block:
                exists = True
                break
        return exists

    def __should_exist(self, block_header: BlockHeader) -> bool:
        return block_header.height % self.side_chain_to_main_chain_ratio == 0

    def __get_message_for_block(self, block_header: BlockHeader) -> str:
        return block_header.merkle_root[-self.main_chain_max_message_size:]
