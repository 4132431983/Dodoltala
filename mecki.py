import random
import requests
from mnemonic import Mnemonic
from bitcoinlib.wallets import Wallet
from web3 import Web3
from tronpy import Tron
import json

# API Endpoints
BTC_API = 'https://blockchain.info/q/addressbalance/'
ETH_API = 'https://eth-mainnet.alchemyapi.io/v2/qA9FV5BMTFx6p7638jhqx-JDFDByAZAn'  # Replace with your Alchemy API key
TRX_API = 'https://api.trongrid.io/v1/accounts/67c5b8f3-9347-4ab5-a2c9-29d2dec3069f'

# Set up Web3 for ETH using Alchemy
alchemy_url = 'https://eth-mainnet.alchemyapi.io/v2/qA9FV5BMTFx6p7638jhqx-JDFDByAZAn'  # Replace with your Alchemy API key
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# Set up Tron (Tronpy)
tron = Tron()

# Generate valid mnemonic
def generate_mnemonic():
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)  # 128 bits entropy for a 12-word mnemonic
    return mnemonic

# Derive Bitcoin address from mnemonic
def derive_btc_address(mnemonic):
    wallet = Wallet.create('temp_wallet', keys=mnemonic, network='bitcoin')
    return wallet.get_key().address

# Derive Ethereum address from mnemonic
def derive_eth_address(mnemonic):
    account = w3.eth.account.from_mnemonic(mnemonic)
    return account.address

# Derive Tron address from mnemonic
def derive_trx_address(mnemonic):
    account = tron.generate_address()
    return account['base58']

# Check Bitcoin balance
def check_btc_balance(address):
    try:
        response = requests.get(f"{BTC_API}{address}?confirmations=0")
        return int(response.text) / 1e8  # Satoshis to BTC
    except:
        return 0

# Check Ethereum balance using Alchemy
def check_eth_balance(address):
    try:
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'apikey': 'YOUR_ALCHEMY_API_KEY'  # Replace with your Alchemy API key
        }
        response = requests.get(ETH_API, params=params)
        return int(response.json()['result']) / 1e18  # Wei to ETH
    except:
        return 0

# Check Tron balance
def check_trx_balance(address):
    try:
        response = requests.get(f"{TRX_API}{address}")
        return response.json()['data'][0]['balance'] / 1e6  # Sun to TRX
    except:
        return 0

# Save to file if wallet has balance
def save_wallet_info(wallet_info):
    with open('wallet_balances.txt', 'a') as f:
        f.write(json.dumps(wallet_info) + '\n')

# Main function to generate wallets and check balances
def process_wallets(batch_size, target_wallets):
    found_wallets = 0
    while found_wallets < target_wallets:
        mnemonic = generate_mnemonic()
        btc_address = derive_btc_address(mnemonic)
        eth_address = derive_eth_address(mnemonic)
        trx_address = derive_trx_address(mnemonic)

        btc_balance = check_btc_balance(btc_address)
        eth_balance = check_eth_balance(eth_address)
        trx_balance = check_trx_balance(trx_address)

        print(f"Checking wallet {found_wallets + 1}:")
        print(f"Mnemonic: {mnemonic}")
        print(f"BTC Address: {btc_address} - BTC Balance: {btc_balance}")
        print(f"ETH Address: {eth_address} - ETH Balance: {eth_balance}")
        print(f"TRX Address: {trx_address} - TRX Balance: {trx_balance}")

        # If any balance is found, save the wallet info
        if btc_balance > 0 or eth_balance > 0 or trx_balance > 0:
            print("Found wallet with balance!")
            wallet_info = {
                'mnemonic': mnemonic,
                'btcAddress': btc_address,
                'ethAddress': eth_address,
                'trxAddress': trx_address,
                'btcBalance': btc_balance,
                'ethBalance': eth_balance,
                'trxBalance': trx_balance
            }
            save_wallet_info(wallet_info)
            found_wallets += 1

        if found_wallets >= target_wallets:
            break

# This will only run if this script is executed directly
if name == "__main__":
    process_wallets(batch_size=1000, target_wallets=3)  # Adjust as needed