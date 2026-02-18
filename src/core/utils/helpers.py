from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
import hashlib
import uuid

def generate_order_number() -> str:
    """Generate a unique order number."""
    return str(uuid.uuid4())

def generate_receipt_number() -> str:
    """Generate a unique receipt number."""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_portfolio_value(
    positions: List[Tuple[str, Decimal, Decimal]], 
    prices: dict[str, Decimal]
) -> Decimal:
    """Calculate total portfolio value."""
    total = Decimal('0')
    for stock, quantity, _ in positions:
        if stock == 'cash':
            total += quantity
        elif stock in prices:
            total += quantity * prices[stock]
    return total

def calculate_pnl(
    positions: List[Tuple[str, Decimal, Decimal]], 
    prices: dict[str, Decimal]
) -> Tuple[Decimal, Decimal]:
    """Calculate realized and unrealized PnL."""
    realized = Decimal('0')
    unrealized = Decimal('0')
    
    for stock, quantity, initial_price in positions:
        if stock == 'cash':
            continue
        if stock in prices:
            current_price = prices[stock]
            unrealized += quantity * (current_price - initial_price)
            
    return realized, unrealized

def format_money(amount: Decimal) -> str:
    """Format a monetary amount."""
    return f"${amount:,.2f}"

def format_quantity(quantity: Decimal) -> str:
    """Format a quantity amount."""
    return f"{quantity:,.4f}"

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse a datetime string."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None

def get_time_range(
    period: str
) -> Tuple[datetime, datetime]:
    """Get start and end times for a given period."""
    end = datetime.now()
    
    if period == '1d':
        start = end - timedelta(days=1)
    elif period == '1w':
        start = end - timedelta(weeks=1)
    elif period == '1m':
        start = end - timedelta(days=30)
    elif period == '3m':
        start = end - timedelta(days=90)
    elif period == '1y':
        start = end - timedelta(days=365)
    else:
        start = end - timedelta(days=1)
        
    return start, end 