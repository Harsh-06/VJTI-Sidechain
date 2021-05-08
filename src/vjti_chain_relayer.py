from typing import List
import time
import json

from core import BlockHeader, Block, Chain
from wallet import Wallet
import requests
from utils.logger import logger

class VJTIChainRelayer:
    def __init__(self, wallet: Wallet) -> None:
        self.wallet = wallet

        # Side Chain Block Headers are written to VJTI chain after these many blocks
        self.side_chain_to_main_chain_ratio = 5  # should be > 1
        self.main_chain_mining_interval = 30
        # self.side_chain_mining_interval = constants.MINING_INTERVAL_THRESHOLD  # should be > main_chain_mining_interval
        self.main_chain_url = 'http://localhost:9000'
        self.main_chain_max_message_size = 128
        self.record_account_public_key = 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEQdVp4AtzeMCty3w7x/s0HFejuv2KbiEn3KEEc9wd4RC6iVdjgSuHwbp1trJJBjqdgk6gyp7lg8vtmP17Dbce4Q=='
        # The public key of the account, to which all transactions will be sent

    def chain_is_ok(self, chain: Chain) -> bool:
        header_list = chain.header_list

        for header in reversed(header_list):
            if header.height == 0:  # 0th block should be skipped
                continue
            if self.__should_exist(header):
                waiting_time_secs = self.main_chain_mining_interval + 2  # 2 second extra
                now_time_secs = int(time.time())
                if header.timestamp + waiting_time_secs < now_time_secs:
                    exists = self.__exists(header)
                    logger.debug(f"Relayer: Header {header} should have existed. It exists and hence chain is trusted? {exists}")
                    return exists
                else:
                    logger.debug(f"Relayer: Header {header} should exist, but we will have to wait for some time.")
        logger.debug(f"Relayer: No need to check for any headers. Chain is too small and hence automatically trusted")
        return True

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
        block_header = block.header
        if not self.__should_exist(block_header):
            logger.debug(f"Relayer: No need to send block: {block_header} ({block_header.height})")
            return
        logger.debug(f"Relayer: Need to send block: {block_header} ({block_header.height})")
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

        data = {'transaction': transaction, 'signature': signed_string}
        r = requests.post(self.main_chain_url + '/sendTransaction', json=data)
        logger.debug(f"Relayer: Send Transaction returned: {r.text}")
        return r.text == "Done"

    def __exists(self, block_header: BlockHeader) -> bool:
        message_for_block = self.__get_message_for_block(block_header)
        data = {'public_key': self.record_account_public_key}
        r = requests.post(self.main_chain_url + '/transactionHistory', json=data)
        tx_history: List[str] = r.json()
        exists = False
        for tx in tx_history:
            tx = json.loads(tx)
            if tx['message'] == message_for_block:
                exists = True
                break
        return exists

    def __should_exist(self, block_header: BlockHeader) -> bool:
        return block_header.height % self.side_chain_to_main_chain_ratio == 0

    def __get_message_for_block(self, block_header: BlockHeader) -> str:
        return block_header.merkle_root[-self.main_chain_max_message_size:]
