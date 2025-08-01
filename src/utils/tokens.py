import json
from pathlib import Path
from web3 import Web3
from web3.contract import Contract

ABI_DIR = Path(__file__).parent.parent.parent / 'abi'

class TokenUtils:
    @staticmethod
    def load_abi(name):
        with open(ABI_DIR / f"{name}.json") as f:
            return json.load(f)
            
    @staticmethod
    def get_token_contract(w3: Web3, address) -> Contract:
        return w3.eth.contract(
            address=address,
            abi=TokenUtils.load_abi('erc20')
        )
        
    @staticmethod
    def get_balance(w3: Web3, token_addr, wallet_addr):
        contract = TokenUtils.get_token_contract(w3, token_addr)
        return contract.functions.balanceOf(wallet_addr).call()
