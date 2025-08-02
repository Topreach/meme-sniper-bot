import time
from web3 import Web3
from src.utils.dex_utils import get_token_price
from src.utils.logger import get_logger
from threading import Thread, Event

logger = get_logger('price_monitor')

class PriceMonitor:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.price_cache = {}
        self.monitoring_threads = {}
        
    def get_token_price(self, token_address, base_token='WETH'):
        # Check cache first
        cache_key = f"{token_address}-{base_token}"
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
            
        # Fetch from DEX
        price = get_token_price(self.w3, token_address, base_token)
        self.price_cache[cache_key] = price
        return price
        
    def start_monitoring(self, token_address, callback, interval=10):
        """Start monitoring token price in a background thread"""
        if token_address in self.monitoring_threads:
            logger.warning(f"Already monitoring {token_address}")
            return
            
        stop_event = Event()
        def monitor_loop():
            while not stop_event.is_set():
                try:
                    price = self.get_token_price(token_address)
                    callback(price)
                except Exception as e:
                    logger.error(f"Price monitoring error: {e}")
                stop_event.wait(interval)
                
        thread = Thread(target=monitor_loop, daemon=True)
        self.monitoring_threads[token_address] = (thread, stop_event)
        thread.start()
        logger.info(f"Started price monitoring for {token_address}")
        
    def stop_monitoring(self, token_address):
        """Stop monitoring a token"""
        if token_address in self.monitoring_threads:
            _, stop_event = self.monitoring_threads[token_address]
            stop_event.set()
            del self.monitoring_threads[token_address]
            logger.info(f"Stopped price monitoring for {token_address}")
