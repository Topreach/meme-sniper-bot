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
        self.l2_networks = {}
        
    def add_wallet(self, name, address, private_key_env):
        self.wallets[name] = {
            'address': address,
            'private_key': os.getenv(private_key_env)
        }
        logger.info(f"Added wallet: {name}")
        
    def add_l2_wallet(self, name, l2_network):
        """Automatically configure wallet based on L2 network"""
        # Map L2 networks to their environment variables
        l2_config = {
            'arbitrum': {
                'address_env': 'ARB_ADDRESS',
                'private_key_env': 'ARB_PK'
            },
            'optimism': {
                'address_env': 'OPT_ADDRESS',
                'private_key_env': 'OPT_PK'
            },
            'polygon': {
                'address_env': 'POLYGON_ADDRESS',
                'private_key_env': 'POLYGON_PK'
            },
            'base': {
                'address_env': 'BASE_ADDRESS',
                'private_key_env': 'BASE_PK'
            }
        }
        
        if l2_network not in l2_config:
            raise ValueError(f"Unsupported L2 network: {l2_network}")
            
        config = l2_config[l2_network]
        address = os.getenv(config['address_env'])
        private_key_env = config['private_key_env']
        
        if not address or not private_key_env:
            raise EnvironmentError(
                f"Missing environment variables for {l2_network} wallet"
            )
            
        # Store L2 network information separately
        self.l2_networks[name] = l2_network
        
        # Add to wallets using existing method
        self.add_wallet(name, address, private_key_env)
        logger.info(f"Added {l2_network} L2 wallet: {name}")

    def get_balance(self, wallet_name, token_address=None):
        wallet = self.wallets.get(wallet_name)
        if not wallet:
            raise ValueError(f"Wallet {wallet_name} not found")
            
        # Handle L2 networks differently
        if wallet_name in self.l2_networks:
            return self._get_l2_balance(wallet, wallet_name, token_address)
            
        # Mainnet balance handling
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
            
    def _get_l2_balance(self, wallet, wallet_name, token_address=None):
        """Special balance handling for L2 networks"""
        l2_network = self.l2_networks[wallet_name]
        
        if token_address is None:
            # Native balance with L2-specific formatting
            balance_wei = self.w3.eth.get_balance(wallet['address'])
            
            # Different decimals for some L2s
            if l2_network == 'arbitrum':
                return self.w3.fromWei(balance_wei, 'ether')
            else:
                return self.w3.fromWei(balance_wei, 'ether')
        else:
            # Token balance with L2-specific handling
            contract = TokenUtils.get_token_contract(self.w3, token_address)
            balance = contract.functions.balanceOf(wallet['address']).call()
            
            # Special decimals handling for known networks
            if l2_network == 'optimism':
                # Optimism uses standard decimals
                decimals = contract.functions.decimals().call()
                return balance / (10 ** decimals)
            else:
                # Default handling
                decimals = contract.functions.decimals().call()
                return balance / (10 ** decimals)
            
    def transfer_token(self, from_wallet, to_address, token_address, amount):
        wallet = self.wallets.get(from_wallet)
        if not wallet:
            raise ValueError(f"Wallet {from_wallet} not found")
            
        # L2-specific transfer handling
        if from_wallet in self.l2_networks:
            return self._l2_transfer(
                from_wallet,
                to_address,
                token_address,
                amount
            )
            
        # Mainnet transfer logic
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
        
    def _l2_transfer(self, from_wallet, to_address, token_address, amount):
        """L2-specific token transfer implementation"""
        wallet = self.wallets[from_wallet]
        l2_network = self.l2_networks[from_wallet]
        contract = TokenUtils.get_token_contract(self.w3, token_address)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * (10 ** decimals))
        
        # L2-specific transaction parameters
        tx_params = {
            'from': wallet['address'],
            'nonce': self.w3.eth.get_transaction_count(wallet['address']),
        }
        
        # Network-specific gas handling
        if l2_network == 'arbitrum':
            # Arbitrum uses EIP-1559
            tx_params.update({
                'maxFeePerGas': self.w3.eth.gas_price,
                'maxPriorityFeePerGas': self.w3.eth.gas_price // 10,
                'type': 2
            })
        elif l2_network == 'optimism':
            # Optimism uses simple gasPrice with buffer
            tx_params['gasPrice'] = self.w3.eth.gas_price * 110 // 100
        else:
            # Default to current gas price
            tx_params['gasPrice'] = self.w3.eth.gas_price
            
        # Build and send transaction
        tx = contract.functions.transfer(to_address, amount_wei).buildTransaction(tx_params)
        signed_tx = self.w3.eth.account.sign_transaction(tx, wallet['private_key'])
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()
