from typing import Optional, List, Any, Tuple
import requests
import utils.constants as consts
from core import Transaction
from utils.utils import compress
from functools import lru_cache
from vvm.VM import VM

@lru_cache(maxsize=16)
def get_cc_co_by_contract_address(contract_address: str) -> Tuple[str, str]:
    r = requests.post("http://0.0.0.0:" + str(consts.MINER_SERVER_PORT) + "/get_cc_co", data=compress(contract_address))
    data = r.json()
    return data.get('cc', ''), data.get('co', '')

class BlockchainVMInterface:
    def __init__(self) -> None:
        self.vm = VM(self.read_contract_output, self.call_contract_function, self.send_amount)

    def read_contract_output(self, contract_address: str) -> Optional[str]:
        _, co = get_cc_co_by_contract_address(contract_address)
        return co if co != '' else None

    def call_contract_function(self, contract_address: str, function_name: str, params: List[Any]) -> Optional[str]:
        cc, _ = get_cc_co_by_contract_address(contract_address)
        if cc == '':
            return None
        else:
            return self.run_function(cc, function_name, params)

    def send_amount(self, receiver_address: str, amount: int, message: Optional[str]) -> bool:
        sender_address = "contract_address"
        # TODO
        pass

    def run_function(self, code: str, function_name: str, params: List[Any]) -> Optional[str]:
        return self.vm.run_function(code, function_name, params)
