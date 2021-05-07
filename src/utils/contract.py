from base64 import b64decode, b64encode
from typing import Tuple
from utils.utils import dhash
from fastecdsa import keys, curve
from utils.encode_keys import encode_public_key


def address_format_to_int(address: str) -> int:
    return int.from_bytes(b64decode(address.encode("ascii")), "big")


def int_to_address_format(priv_key: int) -> str:
    return b64encode(int.to_bytes(priv_key, 256, "big")).decode("ascii")[-124:]


def is_valid_contract_address_format(addr: str) -> bool:
    return addr[:64] == "A" * 64


def gen_contract_address(contract_code: str) -> str:
    # String version of a private key, containing 64 A's at the start
    hashed_contract_code = dhash(contract_code)  # len is 64
    priv_key = address_format_to_int(hashed_contract_code)
    return address


def is_valid_contract_address(addr: str) -> bool:
    return addr[:37] == "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA"

def get_contract_keys() -> Tuple(str, str):
    while True:
        priv_key, pub_key_point = keys.gen_keypair(curve.P256)
        pub_key = encode_public_key(pub_key_point)
        if pub_key[:37] == "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA":
            return str(priv_key), pub_key
