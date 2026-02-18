from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
import uuid

from ...database.manager import ExchangeDB, UserDB
from ...database.models import Order, OrderType, Trade

class Exchange:
    def __init__(self):
        self.exchange_db = ExchangeDB()
        
    def place_order(
        self, 
        username: str, 
        stock: str, 
        order_type: OrderType, 
        price: Decimal, 
        quantity: Decimal
    ) -> str:
        """Place a new order in the exchange."""
        order_number = str(uuid.uuid4())
        
        with self.exchange_db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO active_orders (
                    order_number, username, stock, buy_or_sell,
                    ask_bid_price_per_share, quantity
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_number, username, stock, order_type.value,
                price, quantity
            ))
            
        # Try to match the order immediately
        self._match_orders(stock)
        
        return order_number
        
    def cancel_order(self, order_number: str) -> bool:
        """Cancel an active order."""
        with self.exchange_db.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM active_orders 
                WHERE order_number = ?
            """, (order_number,))
            return cursor.rowcount > 0
            
    def _match_orders(self, stock: str) -> List[Trade]:
        """Match buy and sell orders for a given stock."""
        trades: List[Trade] = []
        
        with self.exchange_db.get_cursor() as cursor:
            # Get all buy orders sorted by price (highest first) and time
            buy_orders = cursor.execute("""
                SELECT * FROM active_orders 
                WHERE stock = ? AND buy_or_sell = ?
                ORDER BY ask_bid_price_per_share DESC, time_of_execution ASC
            """, (stock, OrderType.BUY.value)).fetchall()
            
            # Get all sell orders sorted by price (lowest first) and time
            sell_orders = cursor.execute("""
                SELECT * FROM active_orders 
                WHERE stock = ? AND buy_or_sell = ?
                ORDER BY ask_bid_price_per_share ASC, time_of_execution ASC
            """, (stock, OrderType.SELL.value)).fetchall()
            
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    if buy_order['ask_bid_price_per_share'] >= sell_order['ask_bid_price_per_share']:
                        trade = self._execute_trade(buy_order, sell_order)
                        if trade:
                            trades.append(trade)
                            
        return trades
        
    def _execute_trade(
        self, 
        buy_order: Order, 
        sell_order: Order
    ) -> Optional[Trade]:
        """Execute a trade between matching orders."""
        # Determine trade quantity
        quantity = min(buy_order['quantity'], sell_order['quantity'])
        if quantity <= 0:
            return None
            
        # Create trade record
        receipt_number = str(uuid.uuid4())
        trade = Trade(
            receipt_number=receipt_number,
            stock=buy_order['stock'],
            buyer_id=buy_order['username'],
            seller_id=sell_order['username'],
            price_per_share=sell_order['ask_bid_price_per_share'],
            quantity=quantity,
            timestamp=datetime.now()
        )
        
        with self.exchange_db.get_cursor() as cursor:
            # Record the trade
            cursor.execute("""
                INSERT INTO past_orders (
                    receipt_number, stock, buyer_username, seller_username,
                    bid_pps, ask_pps, quantity
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.receipt_number, trade.stock,
                trade.buyer_id, trade.seller_id,
                buy_order['ask_bid_price_per_share'],
                sell_order['ask_bid_price_per_share'],
                trade.quantity
            ))
            
            # Update or remove the orders
            remaining_buy = buy_order['quantity'] - quantity
            remaining_sell = sell_order['quantity'] - quantity
            
            if remaining_buy > 0:
                cursor.execute("""
                    UPDATE active_orders 
                    SET quantity = ? 
                    WHERE order_number = ?
                """, (remaining_buy, buy_order['order_number']))
            else:
                cursor.execute("""
                    DELETE FROM active_orders 
                    WHERE order_number = ?
                """, (buy_order['order_number'],))
                
            if remaining_sell > 0:
                cursor.execute("""
                    UPDATE active_orders 
                    SET quantity = ? 
                    WHERE order_number = ?
                """, (remaining_sell, sell_order['order_number']))
            else:
                cursor.execute("""
                    DELETE FROM active_orders 
                    WHERE order_number = ?
                """, (sell_order['order_number'],))
                
            # Update user portfolios
            self._update_portfolios(trade)
            
        return trade
        
    def _update_portfolios(self, trade: Trade) -> None:
        """Update user portfolios after a trade."""
        buyer_db = UserDB(trade.buyer_id)
        seller_db = UserDB(trade.seller_id)
        
        with buyer_db.get_cursor() as cursor:
            # Update or insert buyer's position
            cursor.execute("""
                INSERT INTO portfolio (stock, quantity, initial_price_per_share, long_or_short)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(stock) DO UPDATE SET
                    quantity = quantity + ?,
                    initial_price_per_share = (initial_price_per_share * quantity + ? * ?) / (quantity + ?)
            """, (
                trade.stock, trade.quantity, trade.price_per_share, "long",
                trade.quantity, trade.price_per_share, trade.quantity, trade.quantity
            ))
            
            # Update buyer's cash
            cursor.execute("""
                UPDATE portfolio 
                SET quantity = quantity - ? 
                WHERE stock = 'cash'
            """, (trade.price_per_share * trade.quantity,))
            
        with seller_db.get_cursor() as cursor:
            # Update seller's position
            cursor.execute("""
                UPDATE portfolio 
                SET quantity = quantity - ? 
                WHERE stock = ?
            """, (trade.quantity, trade.stock))
            
            # Update seller's cash
            cursor.execute("""
                UPDATE portfolio 
                SET quantity = quantity + ? 
                WHERE stock = 'cash'
            """, (trade.price_per_share * trade.quantity,)) 