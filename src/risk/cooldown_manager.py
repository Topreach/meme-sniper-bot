import time
from src.utils.logger import get_logger

logger = get_logger('cooldown_manager')

class CooldownManager:
    def __init__(self):
        self.last_trade_time = {}
        self.cooldown_periods = {}
        
    def set_cooldown(self, token_address, seconds):
        self.cooldown_periods[token_address] = seconds
        logger.info(f"Set cooldown for {token_address}: {seconds}s")
        
    def is_in_cooldown(self, token_address):
        last_time = self.last_trade_time.get(token_address, 0)
        cooldown = self.cooldown_periods.get(token_address, 30)  # Default 30s
        
        if time.time() - last_time < cooldown:
            return True
        return False
        
    def record_trade(self, token_address):
        self.last_trade_time[token_address] = time.time()
        logger.info(f"Recorded trade for {token_address}, cooldown started")
