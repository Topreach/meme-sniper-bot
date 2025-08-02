from web3 import Web3
from src.utils.logger import get_logger
from src.utils.tokens import TokenUtils
import yaml

logger = get_logger('anti_rug')

class AntiRug:
    def __init__(self, w3: Web3):
        self.w3 = w3
        with open('config/honeypot_rules.yaml') as f:
            self.rules = yaml.safe_load(f)
            
    def check_token(self, token_address: str):
        try:
            token_contract = TokenUtils.get_token_contract(self.w3, token_address)
            
            # Check if owner can change fees
            owner = token_contract.functions.owner().call()
            if owner != '0x0000000000000000000000000000000000000000':
                if self._can_change_fees(token_contract, owner):
                    return False
                    
            # Check max transaction amount
            max_tx = token_contract.functions.maxTransactionAmount().call()
            if max_tx > 0 and max_tx < self.rules['max_tx_threshold']:
                return False
                
            # Check if liquidity is locked
            if not self._check_lp_lock(token_address):
                return False
                
            return True
        except Exception as e:
            logger.error(f"Anti-rug check failed: {e}")
            return False
            
    def _can_change_fees(self, contract, owner):
        try:
            # Check if owner can change fees
            contract.functions.taxFee().call(sender=owner)
            return True
        except:
            return False
            
    def _check_lp_lock(self, token_address):
        # Placeholder for actual LP lock check
        return True
