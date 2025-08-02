#!/usr/bin/env python3
import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from src.core.profit_tracker import ProfitTracker
from src.core.capital_manager import CapitalManager
from src.utils.logger import setup_logging
from config import settings

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger('telegram_bot')

# Initialize components
w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
profit_tracker = ProfitTracker()
capital_manager = CapitalManager(w3)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        '🚀 Meme Sniper Bot Active\n\n'
        '/status - Bot status\n'
        '/profit - Current profit\n'
        '/balance - Wallet balances\n'
        '/trades - Recent trades'
    )

def status(update: Update, context: CallbackContext):
    sniper_balance = capital_manager.get_balance('sniper_wallet')
    reserve_balance = capital_manager.get_balance('reserve_wallet')
    profit = profit_tracker.get_cumulative_profit()
    
    update.message.reply_text(
        f'✅ Bot Status: Active\n'
        f'💰 Sniper Wallet: {sniper_balance:.4f} ETH\n'
        f'📦 Reserve Wallet: {reserve_balance:.4f} ETH\n'
        f'📈 Cumulative Profit: {profit:.4f} ETH\n'
        f'🔁 Last Trade: 5 mins ago'
    )

def profit_report(update: Update, context: CallbackContext):
    daily_profit = profit_tracker.get_daily_profit()
    response = "📊 Daily Profit:\n"
    for date, amount in daily_profit.items():
        response += f"{date}: {amount:.4f} ETH\n"
    
    cumulative = profit_tracker.get_cumulative_profit()
    response += f"\n📈 Total Profit: {cumulative:.4f} ETH"
    update.message.reply_text(response)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment")
        return
        
    updater = Updater(token)
    dp = updater.dispatcher
    
    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("profit", profit_report))
    
    # Start bot
    updater.start_polling()
    logger.info("Telegram bot started")
    updater.idle()

if __name__ == "__main__":
    main()
