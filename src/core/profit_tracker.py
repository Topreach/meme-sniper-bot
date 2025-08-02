import sqlite3
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger('profit_tracker')

class ProfitTracker:
    def __init__(self, db_path='trades.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        
    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            token_address TEXT NOT NULL,
            buy_tx TEXT NOT NULL,
            sell_tx TEXT,
            amount_eth REAL NOT NULL,
            buy_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sell_timestamp DATETIME,
            profit_eth REAL
        )
        ''')
        self.conn.commit()
        
    def record_buy(self, token_address, buy_tx, amount_eth):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO trades (token_address, buy_tx, amount_eth)
        VALUES (?, ?, ?)
        ''', (token_address, buy_tx, amount_eth))
        self.conn.commit()
        return cursor.lastrowid
        
    def record_sell(self, trade_id, sell_tx, profit_eth):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE trades 
        SET sell_tx = ?, sell_timestamp = CURRENT_TIMESTAMP, profit_eth = ?
        WHERE id = ?
        ''', (sell_tx, profit_eth, trade_id))
        self.conn.commit()
        
    def get_daily_profit(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT DATE(sell_timestamp) AS day, SUM(profit_eth) 
        FROM trades 
        WHERE sell_timestamp IS NOT NULL
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
        ''')
        return dict(cursor.fetchall())
        
    def get_cumulative_profit(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(profit_eth) FROM trades WHERE profit_eth > 0')
        return cursor.fetchone()[0] or 0.0
