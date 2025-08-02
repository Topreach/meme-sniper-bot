from src.utils.logger import get_logger
from src.core.price_monitor import PriceMonitor
import numpy as np

logger = get_logger('slippage_control')

class SlippageManager:
    def __init__(self, price_monitor, base_slippage=0.5, volatility_factor=0.1):
        self.price_monitor = price_monitor
        self.base_slippage = base_slippage
        self.volatility_factor = volatility_factor
        self.price_history = {}
        
    def update_price_history(self, token_address, price):
        if token_address not in self.price_history:
            self.price_history[token_address] = []
        self.price_history[token_address].append(price)
        
        # Keep only last 100 prices
        if len(self.price_history[token_address]) > 100:
            self.price_history[token_address] = self.price_history[token_address][-100:]
            
    def calculate_volatility(self, token_address):
        prices = self.price_history.get(token_address, [])
        if len(prices) < 10:
            return 0.0
            
        returns = np.diff(prices) / prices[:-1]
        return np.std(returns)
        
    def get_dynamic_slippage(self, token_address, amount_eth, liquidity):
        volatility = self.calculate_volatility(token_address)
        slippage = self.base_slippage + (volatility * self.volatility_factor * 100)
        
        # Adjust for liquidity
        liquidity_factor = max(1.0, amount_eth / (liquidity * 0.1))  # More slippage if trade > 10% of liquidity
        slippage *= liquidity_factor
        
        # Apply min/max bounds
        return min(max(slippage, self.base_slippage), 10.0)  # Between base and 10%
