#!/usr/bin/env python3
import time
from web3 import Web3
from src.core.mempool_monitor import MempoolMonitor
from src.core.sniper_engine import SniperEngine
from config import settings
from src.utils.logger import setup_logging

setup_logging(settings.LOG_LEVEL)

def main():
    w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    if not w3.isConnected():
        raise ConnectionError("Failed to connect to Ethereum node")
    
    monitor = MempoolMonitor(w3)
    sniper = SniperEngine(w3, settings)
    
    def handle_new_tx(tx_hash):
        lp_data = monitor.process_new_tx(tx_hash)
        if lp_data and sniper.evaluate_opportunity(lp_data):
            sniper.execute_snipe(
                lp_data['token'],
                settings.MAX_TRADE_ETH
            )
    
    # Subscribe to new pending transactions
    new_tx_filter = w3.eth.filter('pending')
    while True:
        for tx_hash in new_tx_filter.get_new_entries():
            handle_new_tx(tx_hash)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
