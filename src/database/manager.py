import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from config.settings import CREDENTIALS_DB, STOCK_PRICES_DB, EXCHANGE_DB, USER_DATA_DIR

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with automatic closing."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Get a database cursor with automatic commit/rollback."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise

class CredentialsDB(DatabaseManager):
    def __init__(self):
        super().__init__(CREDENTIALS_DB)

    def create_tables(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

class StockPricesDB(DatabaseManager):
    def __init__(self):
        super().__init__(STOCK_PRICES_DB)

    def create_tables(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    stock TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    last_price DECIMAL NOT NULL,
                    bid_price DECIMAL,
                    ask_price DECIMAL,
                    volume INTEGER NOT NULL,
                    PRIMARY KEY (stock, timestamp)
                )
            """)

class ExchangeDB(DatabaseManager):
    def __init__(self):
        super().__init__(EXCHANGE_DB)

    def create_tables(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_orders (
                    order_number TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    stock TEXT NOT NULL,
                    buy_or_sell TEXT NOT NULL,
                    ask_bid_price_per_share DECIMAL NOT NULL,
                    quantity DECIMAL NOT NULL,
                    time_of_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES credentials(username)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS past_orders (
                    receipt_number TEXT PRIMARY KEY,
                    stock TEXT NOT NULL,
                    buyer_username TEXT NOT NULL,
                    seller_username TEXT NOT NULL,
                    bid_pps DECIMAL NOT NULL,
                    ask_pps DECIMAL NOT NULL,
                    quantity DECIMAL NOT NULL,
                    time_of_execution TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (buyer_username) REFERENCES credentials(username),
                    FOREIGN KEY (seller_username) REFERENCES credentials(username)
                )
            """)

class UserDB(DatabaseManager):
    def __init__(self, username: str):
        super().__init__(USER_DATA_DIR / f"{username}.db")

    def create_tables(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    stock TEXT PRIMARY KEY,
                    quantity DECIMAL NOT NULL,
                    initial_price_per_share DECIMAL NOT NULL,
                    long_or_short TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy (
                    strategy_name TEXT PRIMARY KEY,
                    strategy_location TEXT NOT NULL,
                    on_off INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """) 