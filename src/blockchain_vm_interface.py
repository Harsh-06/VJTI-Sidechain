from typing import Optional, List, Any
from utils.logger import logger
from utils.contract import is_valid_contract_address
import requests
from wallet import Wallet
import utils.constants as consts
from core import Transaction
from utils.utils import compress
from functools import lru_cache
from vvm.VM import VM

@lru_cache(maxsize=16)
def get_tx_by_contract_id(contract_id: str) -> Optional[Transaction]:
    r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/get_tx", data=compress(contract_id))
    if r.text is None:
        return None
    else:
        return Transaction.from_json(r.text)

class BlockchainVMInterface:
    def __init__(self) -> None:
        self.vm = VM(self.read_contract_output, self.call_contract_function, self.send_amount)
        self.current_contract_address: Optional[str] = None

    def read_contract_output(self, contract_id: str) -> Optional[str]:
        tx = get_tx_by_contract_id(contract_id)
        if tx is None:
            return None
        else:
            return tx.contract_output

    def call_contract_function(self, contract_id: str, function_name: str, params: List[Any]) -> Optional[str]:
        tx = get_tx_by_contract_id(contract_id)
        if tx is None:
            return None
        else:
            contract_address = tx.vout[0].address
            if not is_valid_contract_address(contract_address, tx.contract_code):
                raise Exception("Tx {tx} receiver address is invalid contract address")
            return self.__run_function(tx.contract_code, function_name, params, contract_address)

    def send_amount(self, receiver_address: str, amount: int, message: Optional[str]) -> bool:
        contract_public_key = self.current_contract_address
        data = {
            'bounty': amount,
            'sender_public_key': contract_public_key,
            'receiver_public_key': receiver_address,
            'message': message
        }
        r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/makeTransaction", json=data)
        tx_data = r.json()
        logger.debug(f"BlockchainVmInterface: Make Transaction returned: {tx_data}")
        transaction = tx_data['send_this']
        sign_this = tx_data['sign_this']
        
        contract_wallet = Wallet(pub_key=asdf, priv_key=)
        signed_string = self.wallet.sign(sign_this)

        data = {'transaction': transaction, 'signature': signed_string}
        r = requests.post(self.main_chain_url + '/sendTransaction', json=data)
        logger.debug(f"BlockchainVmInterface: Send Transaction returned: {r.text}")
        return r.text == "Done"



    def __run_function(self, code: str, function_name: str, params: List[Any], contract_address: str) -> Optional[str]:
        old_current_contract_address = self.current_contract_address
        self.current_contract_address = contract_address
        output = self.vm.run_function(code, function_name, params)
        self.current_contract_address = old_current_contract_address
        return output

    def run_contract_code(self, contract_code: str, contract_address: str) -> Optional[str]:
        return self.__run_function(contract_code, "main", [], contract_address)
