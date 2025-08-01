from web3 import Web3
from src.utils.logger import get_logger

logger = get_logger('gas_estimator')

class GasEstimator:
    GAS_STRATEGIES = ['current', 'fast', 'flashbot']

    def __init__(self, w3: Web3):
        self.w3 = w3
        
    def get_optimized_gas(self, strategy='flashbot'):
        try:
            base_fee = self.w3.eth.get_block('latest')['baseFeePerGas']
            
            if strategy == 'flashbot':
                return {
                    'maxFeePerGas': Web3.toWei(base_fee * 1.3, 'gwei'),
                    'maxPriorityFeePerGas': Web3.toWei(2, 'gwei'),
                    'type': 2
                }
            elif strategy == 'fast':
                return {
                    'gasPrice': self.w3.eth.gas_price * 1.2
                }
            else:  # current
                return {
                    'gasPrice': self.w3.eth.gas_price
                }
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            return {'gasPrice': self.w3.toWei('50', 'gwei')}
