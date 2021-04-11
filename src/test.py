from wallet import Wallet
import requests

wallets = [
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE17svSZyUgdjXGeJxR/fDysgMmND4vlb4x+r7oSl22BNfj2F8DzyAK6IpWUbCkwq4QOu2Ivs4fZebovayd986Mw==", 103313668451301764459145471332474352996000252906135338649165244022817255159652),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOs9nZhvCnySWEmu9MvwVW+t3nM5T2QEsgcekpb1nQoO4au2XTGPMJf4xI2sBKEF1ToreBK6amX6z35CFQVO+gw==", 81708545448566365192215824424812292395914953522816889332540536969877076629810),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeAK405KpwnEaD9fPzdHpX9QU6I26ZbG7hOSwwJhyygyqxAYYPWpspGf+fVQvzPBEOMLLwPAdoTrGS4/f9Crl7Q==", 34542016620224333152874129924862569325547307593247243388499607616364786967537),
]
genesis_receiver = wallets[0]

r = requests.post("http://localhost:9000/makeTransaction", json={
    'bounty': 1,
    'sender_public_key': genesis_receiver.public_key,
    'receiver_public_key': wallets[1].public_key,
    'message': "Test transfer"
})
tx_data = r.json()
send_this = tx_data['send_this']
sign_this = tx_data['sign_this']
signed_string = genesis_receiver.sign(sign_this)
data = {
    'transaction': send_this,
    'signature': signed_string
}
r = requests.post('http://localhost:9000/sendTransaction', json=data)
print(r.text)
