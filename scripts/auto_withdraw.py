#!/usr/bin/env python3
import time
from web3 import Web3
from src.utils.logger import get_logger
from src.core.capital_manager import CapitalManager
from config import settings

logger = get_logger('auto_withdraw')

def main():
    w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    if not w3.isConnected():
        raise ConnectionError("Failed to connect to Ethereum node")
    
    manager = CapitalManager(w3)
    min_balance_eth = settings.MIN_RESERVE_BALANCE
    
    while True:
        try:
            # Check reserve wallet balance
            reserve_balance = manager.get_balance(settings.RESERVE_WALLET)
            if reserve_balance < min_balance_eth:
                logger.info("Reserve balance low, initiating transfer")
                
                # Calculate amount to transfer
                amount = min_balance_eth - reserve_balance
                tx_hash = manager.transfer_from_sniper(amount)
                
                if tx_hash:
                    logger.success(f"Transferred {amount} ETH to reserve: {tx_hash}")
                else:
                    logger.error("Transfer failed")
            
            # Check profit withdrawal condition
            if manager.should_withdraw_profits():
                logger.info("Profit threshold reached, withdrawing")
                tx_hash = manager.withdraw_profits()
                logger.success(f"Profits withdrawn: {tx_hash}")
                
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.critical(f"Auto-withdrawal failed: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
