import os
from web3 import Web3
from src.utils.logger import get_logger
from src.utils.tokens import TokenUtils
from config import settings

logger = get_logger('wallet_manager')

class WalletManager:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.wallets = {}
        
    def add_wallet(self, name, address, private_key_env):
        self.wallets[name] = {
            'address': address,
            'private_key': os.getenv(private_key_env)
        }
        logger.info(f"Added wallet: {name}")
        
    def get_balance(self, wallet_name, token_address=None):
        wallet = self.wallets.get(wallet_name)
        if not wallet:
            raise ValueError(f"Wallet {wallet_name} not found")
            
        if token_address is None:
            # Native balance
            return self.w3.fromWei(
                self.w3.eth.get_balance(wallet['address']),
                'ether'
            )
        else:
            # Token balance
            contract = TokenUtils.get_token_contract(self.w3, token_address)
            balance = contract.functions.balanceOf(wallet['address']).call()
            decimals = contract.functions.decimals().call()
            return balance / (10 ** decimals)
            
    def transfer_token(self, from_wallet, to_address, token_address, amount):
        wallet = self.wallets.get(from_wallet)
        if not wallet:
            raise ValueError(f"Wallet {from_wallet} not found")
            
        contract = TokenUtils.get_token_contract(self.w3, token_address)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        tx = contract.functions.transfer(
            to_address,
            amount_wei
        ).buildTransaction({
            'from': wallet['address'],
            'nonce': self.w3.eth.get_transaction_count(wallet['address']),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, wallet['private_key'])
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
