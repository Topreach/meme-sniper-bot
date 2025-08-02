import json
from web3 import Web3
from src.utils.logger import get_logger
from src.utils.helpers import decode_tx_input

logger = get_logger('mempool_monitor')

class MempoolMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.pending_txs = {}
        
    def process_new_tx(self, tx_hash):
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            if not tx or not tx.get('input'):
                return None
                
            # Decode transaction input
            decoded = decode_tx_input(tx['input'])
            if decoded and 'function' in decoded:
                if decoded['function'] == 'addLiquidityETH':
                    logger.info(f"New LP created: {tx_hash}")
                    return self._process_lp_creation(tx, decoded)
        except Exception as e:
            logger.error(f"Error processing tx {tx_hash}: {e}")
        return None

    def _process_lp_creation(self, tx, decoded):
    # Handle L2-specific LP creation patterns
    if settings.IS_L2:
        if settings.L2_NETWORK == 'arbitrum':
            token_addr = decoded['params']['token']
        elif settings.L2_NETWORK == 'optimism':
            token_addr = decoded['params']['tokenA']  # Might be different
        else:
            token_addr = decoded['params']['token']
    else:
        token_addr = decoded['params']['token']
    
    return {
        'tx_hash': tx.hash.hex(),
        'token': token_addr,
        'amount_eth': decoded['params']['amountETHDesired'],
        'block_number': tx.blockNumber,
        'origin': tx['from']
    }
