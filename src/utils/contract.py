from typing import Tuple
from fastecdsa import keys, curve
from utils.encode_keys import encode_public_key

def is_valid_contract_address(addr: str) -> bool:
    return addr[:37] == "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA"

def get_contract_keys() -> Tuple[str, str]:
    while True:
        priv_key, pub_key_point = keys.gen_keypair(curve.P256)
        pub_key = encode_public_key(pub_key_point)
        if pub_key[:37] == "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA":
            return str(priv_key), pub_key
