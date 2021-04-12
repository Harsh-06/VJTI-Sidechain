from wallet import Wallet
import requests

wallets = [
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE17svSZyUgdjXGeJxR/fDysgMmND4vlb4x+r7oSl22BNfj2F8DzyAK6IpWUbCkwq4QOu2Ivs4fZebovayd986Mw==", 103313668451301764459145471332474352996000252906135338649165244022817255159652),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOs9nZhvCnySWEmu9MvwVW+t3nM5T2QEsgcekpb1nQoO4au2XTGPMJf4xI2sBKEF1ToreBK6amX6z35CFQVO+gw==", 81708545448566365192215824424812292395914953522816889332540536969877076629810),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeAK405KpwnEaD9fPzdHpX9QU6I26ZbG7hOSwwJhyygyqxAYYPWpspGf+fVQvzPBEOMLLwPAdoTrGS4/f9Crl7Q==", 34542016620224333152874129924862569325547307593247243388499607616364786967537),
]
genesis_receiver = wallets[0]

contract_code = """
function a(n) do
  b := n + 1;
  return b
end;
function main() do
  val := a(5);
  return val
end
"""
contract_code = """
function main() do
  val := read_contract_output('18154c0c-bb62-4fcc-9369-1f10118d2d5e');
  return val
end
"""
contract_code = """
function main() do
    params := [50];
    val := call_contract_function('18154c0c-bb62-4fcc-9369-1f10118d2d5e', 'a', params);
    return val
end
"""
contract_code = """
function a(n) do
  return n
end;
function main() do
  val := a('abcd');
  return val
end
"""
contract_code = """
function main() do
    params := ['def'];
    val := call_contract_function('e4032ece-9b7f-4813-b2c4-df9836837c19', 'a', params);
    return val
end
"""
contract_code = """
function main() do
    params := [5.5];
    val := call_contract_function('e4032ece-9b7f-4813-b2c4-df9836837c19', 'a', params);
    return val
end
"""
r = requests.post("http://localhost:9000/makeTransaction", json={
    'bounty': 1,
    'sender_public_key': wallets[1].public_key,
    'receiver_public_key': wallets[2].public_key,
    'contract_code': contract_code
})
tx_data = r.json()
send_this = tx_data['send_this']
sign_this = tx_data['sign_this']
signed_string = wallets[1].sign(sign_this)
data = {
    'transaction': send_this,
    'signature': signed_string
}
r = requests.post('http://localhost:9000/sendTransaction', json=data)
print(r.text)
