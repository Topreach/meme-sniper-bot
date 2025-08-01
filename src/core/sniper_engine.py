import time
from src.utils.logger import get_logger
from src.core.honeypot_detector import HoneypotDetector
from src.core.trade_executor import TradeExecutor
from src.core.liquidity_guard import LiquidityGuard
from src.utils.gas_estimator import GasEstimator

logger = get_logger('sniper_engine')

class SniperEngine:
    def __init__(self, w3, config):
        self.w3 = w3
        self.config = config
        self.honeypot_detector = HoneypotDetector(w3)
        self.trade_executor = TradeExecutor(w3)
        self.liquidity_guard = LiquidityGuard(w3)
        self.gas_estimator = GasEstimator(w3)

    def evaluate_opportunity(self, lp_data):
        # Honeypot check
        if not self.honeypot_detector.analyze_token(lp_data['token']):
            logger.warning(f"Honeypot detected for {lp_data['token']}")
            return False
            
        # Liquidity check
        liquidity_ok = self.liquidity_guard.check_liquidity(
            lp_data['token'],
            min_eth=self.config['min_liquidity_eth']
        )
        if not liquidity_ok:
            logger.warning(f"Insufficient liquidity for {lp_data['token']}")
            return False
            
        return True

    def execute_snipe(self, token_addr, amount_eth):
        gas_params = self.gas_estimator.get_optimized_gas()
        
        try:
            tx_hash = self.trade_executor.buy_token(
                token_addr,
                amount_eth,
                gas_params=gas_params
            )
            logger.success(f"Buy executed: {tx_hash}")
            return tx_hash
        except Exception as e:
            logger.critical(f"Trade failed: {e}")
            return None
