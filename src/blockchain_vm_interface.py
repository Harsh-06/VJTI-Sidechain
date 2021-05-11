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
    print('DATAAA', contract_address, data)
    return data.get('cc', ''), data.get('co', ''), data.get('cp', '')

class BlockchainVMInterface:
    def __init__(self, add_contract_tx_to_mempool) -> None:
        self.vm = VM(self.read_contract_output, self.call_contract_function, self.send_amount)
        self.add_contract_tx_to_mempool = add_contract_tx_to_mempool
        self.current_contract_id: Optional[str] = None

    def read_contract_output(self, contract_address: str) -> Optional[str]:
        if not is_valid_contract_address(contract_address):
            raise Exception(f"Contract Address {contract_address} is invalid contract address")
        _, co, _ = get_cc_co_cp_by_contract_address(contract_address)
        return co if co != '' else None

    def call_contract_function(self, contract_address: str, function_name: str, params: List[Any]) -> Optional[str]:
        if not is_valid_contract_address(contract_address):
            raise Exception(f"Contract Address {contract_address} is invalid contract address")
        cc, _, cp = get_cc_co_cp_by_contract_address(contract_address)
        if cc == '':
            return None
        else:
            return self.__run_function(cc, function_name, params, cp)

    def send_amount(self, receiver_address: str, amount: int, message: Optional[str]) -> bool:
        contract_private_key = int(self.current_contract_id)
        contract_wallet = Wallet(pub_key=None, priv_key=contract_private_key)
        data = {
            'bounty': amount,
            'sender_public_key': contract_wallet.public_key,
            'receiver_public_key': receiver_address,
            'message': message
        }
        r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/makeTransaction", json=data)
        tx_data = r.json()
        logger.debug(f"BlockchainVmInterface: Make Transaction returned: {tx_data}")

        transaction = Transaction.from_json(tx_data['send_this']).object()
        signed_string = contract_wallet.sign(tx_data['sign_this'])
        transaction.add_sign(signed_string)

        return self.add_contract_tx_to_mempool(transaction)

    def __run_function(self, code: str, function_name: str, params: List[Any], contract_priv_key: str) -> Optional[str]:
        old_current_contract_id = self.current_contract_id
        self.current_contract_id = contract_priv_key
        output = self.vm.run_function(code, function_name, params)
        self.current_contract_id = old_current_contract_id
        return output

    def run_contract_code(self, contract_code: str, contract_priv_key: str) -> Optional[str]:
        return self.__run_function(contract_code, "main", [], contract_priv_key)
