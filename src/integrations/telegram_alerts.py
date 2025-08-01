import requests
from src.utils.logger import get_logger

logger = get_logger('telegram_alerts')

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    def send_alert(self, message):
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Telegram alert failed: {e}")
