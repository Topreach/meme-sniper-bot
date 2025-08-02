import os
import yaml
from web3 import Web3
from src.utils.logger import get_logger
from src.core.profit_tracker import ProfitTracker
from config import settings

logger = get_logger('capital_manager')

class CapitalManager:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.profit_tracker = ProfitTracker()
        with open('config/capital.yaml') as f:
            self.config = yaml.safe_load(f)
            
    def get_balance(self, wallet_name):
        address = self.config['wallets'][wallet_name]['address']
        return self.w3.fromWei(self.w3.eth.get_balance(address), 'ether')
        
    def transfer_eth(self, from_wallet, to_address, amount_eth):
        # Get wallet details
        wallet_cfg = self.config['wallets'][from_wallet]
        private_key = os.getenv(wallet_cfg['private_key_env'])
        from_address = wallet_cfg['address']
        
        # Build transaction
        tx = {
            'to': to_address,
            'value': self.w3.toWei(amount_eth, 'ether'),
            'gas': 21000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(from_address),
            'chainId': settings.CHAIN_ID
        }
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
        
    def transfer_from_sniper(self, amount_eth):
        return self.transfer_eth(
            'sniper_wallet',
            self.config['wallets']['reserve_wallet']['address'],
            amount_eth
        )
        
    def withdraw_profits(self, amount_eth=None):
        reserve_address = self.config['wallets']['reserve_wallet']['address']
        if amount_eth is None:
            amount_eth = self.get_balance('reserve_wallet') * 0.9  # Withdraw 90%
        
        return self.transfer_eth(
            'reserve_wallet',
            self.config['withdrawal_address'],
            amount_eth
        )
        
    def should_withdraw_profits(self):
        cumulative_profit = self.profit_tracker.get_cumulative_profit()
        return cumulative_profit > self.config['min_profit_threshold']
