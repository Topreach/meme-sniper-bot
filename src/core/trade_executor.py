import time
from web3 import Web3, exceptions
from flashbots import flashbot
from eth_account import Account
from src.utils.logger import get_logger
from src.utils.gas_estimator import GasEstimator
from config import settings

logger = get_logger('trade_executor')

class TradeExecutor:
    def __init__(self, w3: Web3, private_key: str):
        self.w3 = w3
        self.account = Account.from_key(private_key)
        self.signer_key = settings.FLASHBOTS_SIGNER_KEY
        self.router_address = Web3.toChecksumAddress(settings.ROUTER_ADDRESS)
        
        # Initialize router contract if on L2
        if settings.IS_L2:
            self.router_contract = self.w3.eth.contract(
                address=self.router_address,
                abi=settings.ROUTER_ABI
            )
        
        # Setup Flashbots if enabled
        if settings.FLASHBOTS_ENABLED:
            flashbot(w3, self.signer_key)

    def build_buy_tx(self, token_address: str, amount_eth: float):
        # Simplified transaction building
        return {
            'to': self.router_address,
            'value': self.w3.toWei(amount_eth, 'ether'),
            'data': self._encode_buy_data(token_address),
            'chainId': settings.CHAIN_ID,
            'nonce': self.w3.eth.getTransactionCount(self.account.address),
        }

    def execute_trade(self, tx_params, gas_params):
        try:
            # Add gas parameters
            full_tx = {**tx_params, **gas_params}
            
            # Sign and send transaction
            signed_tx = self.account.signTransaction(full_tx)
            tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return self._wait_for_receipt(tx_hash)
        except exceptions.ContractLogicError as e:
            logger.error(f"Contract error: {e}")
        except ValueError as e:
            logger.error(f"Transaction failed: {e}")
        return None

    def execute_flashbot_trade(self, tx_params, gas_params, target_block):
        if not settings.FLASHBOTS_ENABLED:
            logger.warning("Flashbots not enabled!")
            return None
            
        # Create bundle
        signed_tx = self.account.signTransaction({**tx_params, **gas_params})
        bundle = [{'signed_transaction': signed_tx.rawTransaction}]
        
        # Send bundle targeting specific block
        return flashbot(self.w3, self.signer_key).send_bundle(
            bundle,
            target_block_number=target_block
        )

    def _encode_buy_data(self, token_address: str):
        """Encodes transaction data based on network and DEX"""
        if settings.IS_L2:
            # L2-specific trade encoding
            if settings.L2_DEX == 'sushiswap':
                return self._encode_sushiswap_buy(token_address)
            elif settings.L2_DEX == 'uniswap_v3':
                return self._encode_uniswap_v3_buy(token_address)
            else:
                return self._encode_generic_l2_buy(token_address)
        else:
            # Original Ethereum encoding
            return bytes.fromhex(f"0xabc123{token_address[2:]}000000000000000000000000")
    
    def _encode_sushiswap_buy(self, token_address):
        """SushiSwap specific encoding for L2"""
        path = [settings.WETH_ADDRESS, token_address]
        deadline = int(time.time()) + 600  # 10 minutes
        
        return self.router_contract.encodeABI(
            fn_name='swapExactETHForTokens',
            args=[0, path, self.account.address, deadline]
        )
    
    def _encode_uniswap_v3_buy(self, token_address):
        """Uniswap V3 specific encoding for L2"""
        path = bytes.fromhex(f"{settings.WETH_ADDRESS[2:]}{token_address[2:]}")
        deadline = int(time.time()) + 600  # 10 minutes
        
        return self.router_contract.encodeABI(
            fn_name='exactInput',
            args=[{
                'path': path,
                'recipient': self.account.address,
                'deadline': deadline,
                'amountIn': tx_params['value'],  # From build_buy_tx
                'amountOutMinimum': 0
            }]
        )
    
    def _encode_generic_l2_buy(self, token_address):
        """Generic L2 encoding fallback"""
        logger.info("Using generic L2 encoding")
        return bytes.fromhex(f"0xdef456{token_address[2:]}000000000000000000000000")
    
    def _wait_for_receipt(self, tx_hash, timeout=120):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                receipt = self.w3.eth.getTransactionReceipt(tx_hash)
                if receipt is not None:
                    status = "Success" if receipt.status == 1 else "Failed"
                    logger.info(f"Tx {tx_hash.hex()} mined: {status}")
                    return receipt
            except exceptions.TransactionNotFound:
                pass
            time.sleep(1)
        logger.warning(f"Transaction not mined: {tx_hash.hex()}")
        return None
