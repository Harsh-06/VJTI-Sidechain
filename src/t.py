from fastecdsa import keys, curve, ecdsa
from utils.encode_keys import encode_public_key, decode_public_key
import time

maxi = 100
for i in range(100):
    s = time.time()
    while True:
        priv_key, pub_key_point = keys.gen_keypair(curve.P256)
        pub_key = encode_public_key(pub_key_point)
        # print(pub_key)
        if pub_key[:37] == "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA":
            print(priv_key)
            print(pub_key)
            break

    d = time.time() - s
    print(d)
    maxi = max(d, maxi)
print()
print(maxi)