from web3 import Web3
from src.utils.logger import get_logger
from src.utils import settings  # Import settings for L2 configuration

logger = get_logger('gas_estimator')

class GasEstimator:
    GAS_STRATEGIES = ['current', 'fast', 'flashbot']

    def __init__(self, w3: Web3):
        self.w3 = w3
        
    def get_optimized_gas(self, strategy='current'):
        if settings.IS_L2:
            # L2 networks have simpler gas models
            try:
                gas_price = self.w3.eth.gas_price
                
                # Special handling for different L2s
                if settings.L2_NETWORK == 'arbitrum':
                    return {
                        'maxFeePerGas': gas_price,
                        'maxPriorityFeePerGas': gas_price // 10,
                        'type': 2
                    }
                elif settings.L2_NETWORK == 'optimism':
                    return {
                        'gasPrice': gas_price * 110 // 100  # Add 10% buffer
                    }
                else:  # Polygon, Base, etc.
                    return {
                        'gasPrice': gas_price
                    }
            except Exception as e:
                logger.error(f"L2 gas estimation failed: {e}")
                return {'gasPrice': self.w3.toWei('0.1', 'gwei')}
        else:
            # Original Ethereum mainnet logic
            try:
                base_fee = self.w3.eth.get_block('latest')['baseFeePerGas']
                
                if strategy == 'flashbot':
                    return {
                        'maxFeePerGas': (base_fee * 13) // 10,  # 1.3x base fee (using integer math)
                        'maxPriorityFeePerGas': Web3.toWei(2, 'gwei'),
                        'type': 2
                    }
                elif strategy == 'fast':
                    return {
                        'gasPrice': self.w3.eth.gas_price * 12 // 10  # 1.2x current gas price
                    }
                else:  # current strategy
                    return {
                        'gasPrice': self.w3.eth.gas_price
                    }
            except Exception as e:
                logger.error(f"Gas estimation failed: {e}")
                return {'gasPrice': self.w3.toWei('50', 'gwei')}
