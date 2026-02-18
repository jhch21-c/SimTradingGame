from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

class PositionType(Enum):
    LONG = "long"
    SHORT = "short"

@dataclass
class User:
    username: str
    password_hash: str
    created_at: datetime

@dataclass
class Portfolio:
    user_id: str
    stock: str
    quantity: Decimal
    initial_price: Decimal
    position_type: PositionType

@dataclass
class Order:
    order_number: str
    user_id: str
    stock: str
    order_type: OrderType
    price_per_share: Decimal
    quantity: Decimal
    time_of_execution: datetime
    status: str

@dataclass
class Trade:
    receipt_number: str
    stock: str
    buyer_id: str
    seller_id: str
    price_per_share: Decimal
    quantity: Decimal
    timestamp: datetime

@dataclass
class Strategy:
    name: str
    user_id: str
    file_location: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class StockPrice:
    stock: str
    timestamp: datetime
    last_price: Decimal
    bid_price: Optional[Decimal]
    ask_price: Optional[Decimal]
    volume: int 