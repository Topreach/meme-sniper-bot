#!/usr/bin/env python3
import argparse
from web3 import Web3
from src.core.trade_executor import TradeExecutor
from config import settings
from src.utils.logger import setup_logging

setup_logging(settings.LOG_LEVEL)

def main():
    parser = argparse.ArgumentParser(description='Manual Token Investment')
    parser.add_argument('token', type=str, help='Token contract address')
    parser.add_argument('amount', type=float, help='ETH amount to invest')
    parser.add_argument('--slippage', type=float, default=settings.MAX_SLIPPAGE, 
                       help='Max slippage percentage')
    args = parser.parse_args()

    w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
    if not w3.isConnected():
        raise ConnectionError("Failed to connect to Ethereum node")
    
    executor = TradeExecutor(w3, os.getenv('SNIPER_PK'))
    tx_hash = executor.buy_token(
        args.token,
        args.amount,
        max_slippage=args.slippage
    )
    
    print(f"Investment executed: {tx_hash}")

if __name__ == "__main__":
    main()
