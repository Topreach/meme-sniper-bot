from web3 import Web3
from src.utils.logger import get_logger
from src.utils.tokens import TokenUtils
from config import settings

logger = get_logger('liquidity_guard')

class LiquidityGuard:
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.factory_contract = TokenUtils.get_factory_contract(w3)
        self.pair_abi = TokenUtils.load_abi('pair_factory')

    def get_liquidity(self, token_address: str):
        try:
            weth_address = Web3.toChecksumAddress(settings.WETH_ADDRESS)
            token_address = Web3.toChecksumAddress(token_address)
            
            # Get pair address
            pair_address = self.factory_contract.functions.getPair(
                token_address,
                weth_address
            ).call()
            
            if pair_address == '0x0000000000000000000000000000000000000000':
                return 0.0
                
            # Get reserves
            pair_contract = self.w3.eth.contract(
                address=pair_address,
                abi=self.pair_abi
            )
            reserves = pair_contract.functions.getReserves().call()
            weth_reserve = self.w3.fromWei(reserves[1], 'ether')
            
            return float(weth_reserve)
        except Exception as e:
            logger.error(f"Liquidity check failed: {e}")
            return 0.0
