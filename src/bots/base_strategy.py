from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, NamedTuple, Literal
from pathlib import Path

from ..core.trading.exchange import Exchange
from ..database.manager import UserDB, StockPricesDB

OrderType = Literal["buy", "sell"]

class Position(NamedTuple):
    """A position in a stock."""
    stock: str
    quantity: Decimal
    initial_price: Decimal
    position_type: str

class StockPrice(NamedTuple):
    """A stock's current price data."""
    last_trade_price: Decimal
    time: str

class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, username: str):
        """Initialize the strategy."""
        self.username = username
        self.exchange = Exchange()
        self.user_db = UserDB(username)
        self.stock_db = StockPricesDB()
        
    def get_portfolio(self) -> List[Position]:
        """Get current portfolio positions."""
        with self.user_db.get_cursor() as cursor:
            data = cursor.execute("SELECT * FROM portfolio").fetchall()
            
        return [
            Position(
                stock=row[0],
                quantity=Decimal(str(row[1])),
                initial_price=Decimal(str(row[2])),
                position_type=row[3]
            )
            for row in data
        ]
        
    def get_stock_price(self, stock: str) -> Optional[StockPrice]:
        """Get latest stock price."""
        with self.stock_db.get_cursor() as cursor:
            data = cursor.execute(f"""
                SELECT last_trade_price, time 
                FROM [{stock}] 
                ORDER BY time DESC 
                LIMIT 1
            """).fetchone()
            
        if data:
            return StockPrice(
                last_trade_price=Decimal(str(data[0])),
                time=data[1]
            )
        return None
        
    def get_historical_prices(
        self, 
        stock: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[StockPrice]:
        """Get historical stock prices."""
        with self.stock_db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM stock_prices 
                WHERE stock = ? 
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (stock, start_time, end_time))
            return [StockPrice(*row) for row in cursor.fetchall()]
    
    @abstractmethod
    def analyze_market(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Analyze market conditions and return trading signals.
        Returns dict: {stock: {'signal': 1.0}} where 1.0 is strong buy, -1.0 is strong sell
        """
        pass
        
    @abstractmethod
    def generate_orders(self) -> List[Tuple[str, OrderType, Decimal, Decimal]]:
        """
        Generate orders based on analysis.
        Returns list of tuples: (stock, order_type, price, quantity)
        """
        pass
        
    def execute(self) -> None:
        """Execute one iteration of the trading strategy."""
        # Analyze market
        signals = self.analyze_market()
        
        # Generate orders
        orders = self.generate_orders()
        
        # Place orders
        for stock, order_type, price, quantity in orders:
            self.place_order(stock, order_type, price, quantity)
            
    def place_order(
        self,
        stock: str,
        order_type: OrderType,
        price: Decimal,
        quantity: Decimal
    ) -> Optional[str]:
        """
        Place a new order.
        
        Args:
            stock: Stock symbol
            order_type: Either 'buy' or 'sell'
            price: Price per share
            quantity: Number of shares
            
        Returns:
            Optional[str]: Order number if successful, None if failed
        """
        try:
            return self.exchange.place_order(
                username=self.username,
                stock=stock,
                order_type=order_type,
                price=price,
                quantity=quantity
            )
        except Exception:
            return None
            
    def should_buy(self, stock: str) -> Tuple[bool, Optional[Decimal], Optional[Decimal]]:
        """
        Determine if we should buy the stock.
        
        Args:
            stock: Stock symbol
            
        Returns:
            tuple[bool, Optional[Decimal], Optional[Decimal]]: 
                (should_buy, price_to_buy_at, quantity_to_buy)
        """
        raise NotImplementedError("Subclasses must implement should_buy()")
        
    def should_sell(self, stock: str) -> Tuple[bool, Optional[Decimal], Optional[Decimal]]:
        """
        Determine if we should sell the stock.
        
        Args:
            stock: Stock symbol
            
        Returns:
            tuple[bool, Optional[Decimal], Optional[Decimal]]: 
                (should_sell, price_to_sell_at, quantity_to_sell)
        """
        raise NotImplementedError("Subclasses must implement should_sell()")
        
    def run(self, stock: str) -> None:
        """
        Run one iteration of the strategy.
        
        Args:
            stock: Stock symbol to trade
        """
        # Check if we should buy
        should_buy, buy_price, buy_qty = self.should_buy(stock)
        if should_buy and buy_price and buy_qty:
            self.place_order(stock, "buy", buy_price, buy_qty)
            
        # Check if we should sell
        should_sell, sell_price, sell_qty = self.should_sell(stock)
        if should_sell and sell_price and sell_qty:
            self.place_order(stock, "sell", sell_price, sell_qty) 