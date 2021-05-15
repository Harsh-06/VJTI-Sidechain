import json
import time
from core import Transaction
from typing import Optional, List, Any, Tuple
import requests
import utils.constants as consts
from utils.logger import logger
from utils.contract import is_valid_contract_address
from wallet import Wallet
from utils.utils import compress
from functools import lru_cache
from vvm.VM import VM

@lru_cache(maxsize=16)
def get_cc_co_cp_by_contract_address(contract_address: str) -> Tuple[str, str, str]:
    r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/get_cc_co_cp", data=compress(contract_address))
    data = r.json()
    return data.get('cc', ''), data.get('co', ''), data.get('cp', '')

class BlockchainVMInterface:
    def __init__(self, add_contract_tx_to_mempool) -> None:
        self.vm = VM(self.read_contract_output, self.call_contract_function, self.send_amount, self.update_contract_output)
        self.add_contract_tx_to_mempool = add_contract_tx_to_mempool
        self.current_contract_priv_key: Optional[str] = None

    def read_contract_output(self, contract_address: str) -> Optional[str]:
        if contract_address.lower() == 'self':
            contract_address = Wallet.gen_public_key(int(self.current_contract_priv_key))
        if not is_valid_contract_address(contract_address):
            raise Exception(f"Contract Address {contract_address} is invalid contract address")
        _, co, _ = get_cc_co_cp_by_contract_address(contract_address)
        co = str(co)
        co = co.replace("'", "\\'") if co != '' else None
        logger.debug(f"Read output of contract {contract_address}: {co}")
        return co

    def call_contract_function(self, contract_address: str, function_name: str, params: List[Any]) -> Optional[str]:
        if not is_valid_contract_address(contract_address):
            raise Exception(f"Contract Address {contract_address} is invalid contract address")
        cc, _, cp = get_cc_co_cp_by_contract_address(contract_address)
        if cc == '':
            return None
        else:
            return self.__run_function(cc, function_name, params, cp)

    def send_amount(self, receiver_address: str, amount: int, message: Optional[str]) -> bool:
        contract_private_key = int(self.current_contract_priv_key)
        contract_wallet = Wallet(pub_key=None, priv_key=contract_private_key)
        data = {
            'bounty': amount,
            'sender_public_key': contract_wallet.public_key,
            'receiver_public_key': receiver_address,
            'message': message
        }
        r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/makeTransaction", json=data)
        tx_data = r.json()
        logger.debug(f"BlockchainVmInterface: send_amount - Make Transaction returned: {tx_data}")

        transaction = Transaction.from_json(tx_data['send_this']).object()
        signed_string = contract_wallet.sign(tx_data['sign_this'])
        transaction.add_sign(signed_string)

        return self.add_contract_tx_to_mempool(transaction)

    def update_contract_output(self, output: str) -> bool:
        contract_private_key = int(self.current_contract_priv_key)
        contract_wallet = Wallet(pub_key=None, priv_key=contract_private_key)
        contract_address = contract_wallet.public_key
        cc, _, cp = get_cc_co_cp_by_contract_address(contract_address)
        if cp != str(contract_private_key):
            # We should panic
            logger.error(f"Contract private keys do not match for address {contract_address}")
            return False
        if cc == '':
            logger.error(f"Contract code is empty for address {contract_address}")
            return False
        cpub = contract_address

        data = {
            'bounty': 1,
            'sender_public_key': contract_wallet.public_key,
            'receiver_public_key': 'AAAAA' + cpub[5:], # Some random address
            'message': "Updated output of the tx", # Possibly add the prev tx_hash here
            'contract_code': cc
        }
        r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/makeTransaction", json=data)
        logger.debug(f"BlockchainVmInterface: update_contract_output - Make Transaction returned: {r.text}")
        res = r.json()['send_this']
        tx_data = json.loads(res)

        tx_data['contract_output'] = output
        tx_data['contract_priv_key'] = cp
        tx_data['data'] = "" # Leaving it empty
        tx_data['timestamp'] = int(time.time())
        for num in tx_data['vout']:
            tx_data['vout'][num]["address"] = cpub

        transaction = Transaction.from_json(json.dumps(tx_data)).object()
        tx_vin = transaction.vin
        transaction.vin = {}
        transaction.contract_output = None
        tx_json_to_sign = transaction.to_json()
        signed_string = contract_wallet.sign(tx_json_to_sign)
        transaction.vin = tx_vin
        transaction.contract_output = output
        transaction.add_sign(signed_string)

        return self.add_contract_tx_to_mempool(transaction)

    def __run_function(self, code: str, function_name: str, params: List[Any], contract_priv_key: str) -> Optional[str]:
        old_current_contract_priv_key = self.current_contract_priv_key
        self.current_contract_priv_key = contract_priv_key
        output = self.vm.run_function(code, function_name, params)
        self.current_contract_priv_key = old_current_contract_priv_key
        return output

    def run_contract_code(self, contract_code: str, contract_priv_key: str) -> Optional[str]:
        return self.__run_function(contract_code, "main", [], contract_priv_key)
