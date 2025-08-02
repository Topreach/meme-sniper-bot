# Meme Sniper Bot

Professional, high-frequency trading bot for meme coins on Ethereum.

## Features
- Real-time mempool monitoring
- Flashbots integration for MEV protection
- Honeypot detection system
- AI-powered sentiment analysis
- Capital management system
- Java dashboard for monitoring
- Telegram alerts

## Requirements
- Python 3.10+
- Java 11+ (for dashboard)
- Web3.py
- PostgreSQL (for dashboard)

## Installation
```bash
git clone https://github.com/yourusername/meme-sniper-bot.git
cd meme-sniper-bot

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env  # Add your keys

# Build Java dashboard
cd dashboard-java
./mvnw clean package
