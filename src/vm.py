from typing import Callable, Optional


class VM:
    def __init__(self, read_contract_output: Callable[[str], Optional[str]],
                 call_contract_function: Callable[[str, str, Optional[str]], Optional[str]],
                 send_amount: Callable[[str, int, Optional[str]], bool]) -> None:
        self.read_contract_output = read_contract_output
        self.call_contract_function = call_contract_function
        self.send_amount = send_amount

    def run_function(self, code: str, function_name: str, params: Optional[str]) -> Optional[str]:
        pass
