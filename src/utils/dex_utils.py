from web3 import Web3
from src.utils.tokens import TokenUtils
from src.utils.logger import get_logger

logger = get_logger('dex_utils')

def get_token_price(w3, token_address, base_token='WETH'):
    token_address = Web3.toChecksumAddress(token_address)
    base_token = Web3.toChecksumAddress(base_token)
    
    # Get pair contract
    factory = TokenUtils.get_factory_contract(w3)
    pair_address = factory.functions.getPair(token_address, base_token).call()
    
    if pair_address == '0x' + '0'*40:
        logger.warning(f"No pair found for {token_address}/{base_token}")
        return 0.0
        
    pair_contract = w3.eth.contract(
        address=pair_address,
        abi=TokenUtils.load_abi('pair_factory')
    )
    
    # Get reserves
    reserves = pair_contract.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1 = reserves[1]
    
    # Determine token order
    token0 = pair_contract.functions.token0().call()
    if token0.lower() == token_address.lower():
        token_reserve = reserve0
        base_reserve = reserve1
    else:
        token_reserve = reserve1
        base_reserve = reserve0
        
    # Get decimals
    token_contract = TokenUtils.get_token_contract(w3, token_address)
    base_contract = TokenUtils.get_token_contract(w3, base_token)
    
    token_decimals = token_contract.functions.decimals().call()
    base_decimals = base_contract.functions.decimals().call()
    
    # Calculate price
    if token_reserve == 0:
        return 0.0
        
    return (base_reserve / (10 ** base_decimals)) / (token_reserve / (10 ** token_decimals))
