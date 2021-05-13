from wallet import Wallet
import requests

wallets = [
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE17svSZyUgdjXGeJxR/fDysgMmND4vlb4x+r7oSl22BNfj2F8DzyAK6IpWUbCkwq4QOu2Ivs4fZebovayd986Mw==", 103313668451301764459145471332474352996000252906135338649165244022817255159652),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOs9nZhvCnySWEmu9MvwVW+t3nM5T2QEsgcekpb1nQoO4au2XTGPMJf4xI2sBKEF1ToreBK6amX6z35CFQVO+gw==", 81708545448566365192215824424812292395914953522816889332540536969877076629810),
    Wallet("MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeAK405KpwnEaD9fPzdHpX9QU6I26ZbG7hOSwwJhyygyqxAYYPWpspGf+fVQvzPBEOMLLwPAdoTrGS4/f9Crl7Q==", 34542016620224333152874129924862569325547307593247243388499607616364786967537),
]

contract_code = """
function increment(n) do
    b := n + 1;
    return b
end;
function main() do
    val := increment(5);
    return val
end
"""
contract_code = """
function main() do
    contract_address := 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA6DNFDFe95t5kSf2yv3BT1I0jatbW/BsH8cQbEQnhcKNGvjQwvWj9ctcrhHjatJn9iB5eBYqrRutrlwB417xbA==';
    val := read_contract_output(contract_address);
    return val
end
"""
contract_code = """
function main() do
    params := [50];
    contract_address := 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEA6DNFDFe95t5kSf2yv3BT1I0jatbW/BsH8cQbEQnhcKNGvjQwvWj9ctcrhHjatJn9iB5eBYqrRutrlwB417xbA==';
    val := call_contract_function(contract_address, 'increment', params);
    return val
end
"""
contract_code1 = """
function pay(n) do
    receiving_account_pub_key := 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEOs9nZhvCnySWEmu9MvwVW+t3nM5T2QEsgcekpb1nQoO4au2XTGPMJf4xI2sBKEF1ToreBK6amX6z35CFQVO+gw==';
    ok := send_amount(receiving_account_pub_key, n, 'Transfer From Contract');
    return ok
end;
function main() do
  return 1
end
"""
contract_code2 = """
function main() do
    params := [11];
    send_amount_contract_address := 'MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEAmv36krj5R9YpHjh2Z/wV7CnIFQMbHsYS1Hbu70PIoapFVzQcq2wloHsL2Z3W7ar1X43mwFCPAo4xUA1pV+KwQ==';
    val := call_contract_function(send_amount_contract_address, 'pay', params);
    return val
end
"""
sender_wallet = wallets[0]
receiver_wallet = wallets[1]

r = requests.post("http://localhost:9001/makeTransaction", json={
    'bounty': 1,
    'sender_public_key': sender_wallet.public_key,
    'receiver_public_key': receiver_wallet.public_key,
    'contract_code': contract_code,
    # 'message': 'Amount Transfer',
    # 'message': 'Simple Contract',
    # 'message': 'Contract Reading Another Contract\'s Output',
    # 'message': 'Contract Calling Another Contract\'s Function',
    # 'message': 'Contract Having send_amount',
    # 'message': 'Amount Transfer To Contract',
    'message': 'Data Transaction',
    # 'data': 'Hello, this is some test data' * 100
})
tx_data = r.json()
send_this = tx_data['send_this']
sign_this = tx_data['sign_this']
signed_string = sender_wallet.sign(sign_this)
data = {
    'transaction': send_this,
    'signature': signed_string
}
r = requests.post('http://localhost:9001/sendTransaction', json=data)
print(r.text)
