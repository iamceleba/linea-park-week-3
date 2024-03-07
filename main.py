import json
import os
import random
import time
from tqdm import tqdm
from web3 import Web3


def check_status_tx(tx_hash, w3):
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        try:
            status_ = w3.eth.get_transaction_receipt(tx_hash)
            status = status_["status"]
            if status in [0, 1]:
                return status
            time.sleep(5)
            attempts += 1
        except Exception as error:
            time.sleep(5)


def sleeping(sleep_from, sleep_to):
    delay = random.randint(sleep_from, sleep_to)
    time.sleep(1)
    with tqdm(
            total=delay,
            desc="💤 Sleep",
            bar_format="{desc}: |{bar:20}| {percentage:.0f}% | {n_fmt}/{total_fmt}",
            colour="green"
    ) as pbar:
        for _ in range(delay):
            time.sleep(1)
            pbar.update(1)


def wallets_reader():
    with open("linea_wallets.txt", "r", encoding="utf-8") as wallets_file:
        wallets = [row.strip() for row in wallets_file]
    return wallets


def load_abi(name):
    with open(f'{os.path.abspath(os.path.dirname(__file__))}\{name}.json') as f:
        abi = json.load(f)
    return abi


wallets = wallets_reader()


def execute_contract_transaction(w3, account, contract_tx):
    try:
        contract_tx['gas'] = int(w3.eth.estimate_gas(contract_tx) * random.uniform(1.02, 1.04))
        signed_tx = account.sign_transaction(contract_tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        status = check_status_tx(tx_hash, w3)
        print(
            f'✅ https://rpc.linea.build/{w3.to_hex(tx_hash)}' if status == 1 else f'❌ https://rpc.linea.build/{w3.to_hex(tx_hash)}')
    except Exception as e:
        print(f"Error executing contract transaction: {e}")


def money_gun(w3, wallet_address):
    contract_tx = {
        'chainId': w3.eth.chain_id,
        'from': wallet_address,
        'to': Web3.to_checksum_address('0xc0deb0445e1c307b168478f38eac7646d198f984'),
        'value': random.randint(1000000000000, 1500000000000),
        'nonce': w3.eth.get_transaction_count(wallet_address),
        'gas': 0,
        'gasPrice': int(w3.eth.gas_price * random.uniform(1.02, 1.03))
    }

    execute_contract_transaction(w3, account, contract_tx)


def dmail(w3, wallet_address):
    contract_address = Web3.to_checksum_address('0xd1a3abf42f9e66be86cfdea8c5c2c74f041c5e14')
    contract = w3.eth.contract(address=contract_address, abi=load_abi('dmail'))

    hex_email = wallet_address.encode('utf-8').hex()
    hex_subject = wallet_address.encode('utf-8').hex()
    contract_tx = contract.functions.send_mail(hex_email, hex_subject).build_transaction({
        'chainId': w3.eth.chain_id,
        'nonce': w3.eth.get_transaction_count(wallet_address),
        'from': wallet_address,
        'gas': 0,
        'gasPrice': int(w3.eth.gas_price * random.uniform(1.02, 1.03))
    })

    execute_contract_transaction(w3, account, contract_tx)


def mint_nft(w3, wallet_address):
    contract_tx = {'chainId': w3.eth.chain_id, 'nonce': w3.eth.get_transaction_count(wallet_address),
                   'from': wallet_address, 'value': w3.to_wei(0.0001, 'ether'),
                   'to': Web3.to_checksum_address('0xc043bce9af87004398181a8de46b26e63b29bf99'),
                   'gas': random.randint(300000, 310000),
                   'gasPrice': int(w3.eth.gas_price * random.uniform(1.02, 1.03)),
                   'data': '0xefef39a10000000000000000000000000000000000000000000000000000000000000001'}

    execute_contract_transaction(w3, account, contract_tx)


def readon(w3, wallet_address):
    contract_tx = {'chainId': w3.eth.chain_id, 'nonce': w3.eth.get_transaction_count(wallet_address),
                   'from': wallet_address, 'value': 0,
                   'to': Web3.to_checksum_address('0x8286d601a0ed6cf75e067e0614f73a5b9f024151'),
                   'gas': random.randint(300000, 310000),
                   'gasPrice': int(w3.eth.gas_price * random.uniform(1.02, 1.03)),
                   'data': '0x7859bb8d00000000000000000000000000000000000000000000000017ba714eef548f32'}

    execute_contract_transaction(w3, account, contract_tx)


def checkin(w3, wallet_address):
    contract_tx = {'chainId': w3.eth.chain_id, 'nonce': w3.eth.get_transaction_count(wallet_address),
                   'from': wallet_address, 'value': 0,
                   'to': Web3.to_checksum_address('0x37d4bfc8c583d297a0740d734b271eac9a88ade4'),
                   'gas': random.randint(300000, 310000),
                   'gasPrice': int(w3.eth.gas_price * random.uniform(1.02, 1.03)), 'data': '0x183ff085'}

    execute_contract_transaction(w3, account, contract_tx)


if __name__ == "__main__":
    try:
        RANDOM_SHUFFLE = True  # Мешать ли кошельки? True/False (Да/Нет)
        DELAY_BETWEEN_TASKS = [15, 60] # Задержка между задачами (в секундах)
        DELAY_BETWEEN_WALLETS = [60, 180] # Задержка между аккаутами (в секундах)
        if RANDOM_SHUFFLE:
            random.shuffle(wallets)

        functions_list = [money_gun, dmail, mint_nft, readon, checkin]

        for i in range(len(wallets)):
            try:
                private_key = wallets[i]
                w3 = Web3(Web3.HTTPProvider('https://rpc.linea.build'))
                account = w3.eth.account.from_key(private_key)
                wallet_address = account.address
                random.shuffle(functions_list)
                for idx, func in enumerate(functions_list):
                    print(f'{i + 1}/{len(wallets)} {wallet_address} {idx + 1}/{len(functions_list)} {func}')
                    func(w3, wallet_address)
                    if idx + 1 < len(functions_list) or i + 1 != len(wallets):
                        sleeping(DELAY_BETWEEN_TASKS[0], DELAY_BETWEEN_TASKS[1])

                if i + 1 != len(wallets):
                    sleeping(DELAY_BETWEEN_WALLETS[0], DELAY_BETWEEN_WALLETS[1])
            except Exception as e:
                print(f"Error occurred in iteration {i + 1}: {e}")

    except Exception as e:
        print(f"Outer exception occurred: {e}")
