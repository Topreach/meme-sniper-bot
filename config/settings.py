import os
from dotenv import load_dotenv

load_dotenv()

# Blockchain Configuration
RPC_URL = os.getenv('RPC_URL', 'https://mainnet.infura.io/v3/your_infura_id')
CHAIN_ID = int(os.getenv('CHAIN_ID', 1))
FLASHBOTS_ENABLED = os.getenv('FLASHBOTS_ENABLED', 'True') == 'True'
L2_NETWORK = os.getenv('L2_NETWORK', 'arbitrum')  # Options: arbitrum, optimism, polygon, base
L2_RPC_URL = os.getenv('L2_RPC_URL', 'https://arb1.arbitrum.io/rpc')

# Bot Behavior
SNIPE_DELAY = float(os.getenv('SNIPE_DELAY', 0.2))  # Seconds
MAX_SLIPPAGE = float(os.getenv('MAX_SLIPPAGE', 5))  # Percentage
GAS_MULTIPLIER = float(os.getenv('GAS_MULTIPLIER', 1.2))

# System
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
API_PORT = int(os.getenv('API_PORT', 8080))

# Add to DEX configuration
L2_DEX = os.getenv('L2_DEX', 'sushiswap')  # Options: sushiswap, uniswap_v3, camelot
