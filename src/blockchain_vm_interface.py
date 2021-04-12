from typing import Optional, List, Any
import requests
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
            return self.run_function(tx.contract_code, function_name, params)

    def send_amount(self, receiver_address: str, amount: int, message: Optional[str]) -> bool:
        sender_address = "contract_address"
        # TODO
        pass

    def run_function(self, code: str, function_name: str, params: List[Any]) -> Optional[str]:
        return self.vm.run_function(code, function_name, params)
