import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import importlib.util
import sys

from ...core.trading.exchange import Exchange
from ...database.manager import UserDB
from ...bots.base_strategy import BaseStrategy

def load_strategy_template() -> str:
    """Load the strategy template code."""
    return """from decimal import Decimal
from typing import Optional

from src.bots.base_strategy import BaseStrategy

class CustomStrategy(BaseStrategy):
    def __init__(self, username: str):
        super().__init__(username)
        # Add any custom initialization here
        
    def should_buy(self, stock: str) -> tuple[bool, Optional[Decimal], Optional[Decimal]]:
        \"\"\"
        Determine if we should buy the stock.
        Returns:
            tuple[bool, Optional[Decimal], Optional[Decimal]]: 
                (should_buy, price_to_buy_at, quantity_to_buy)
        \"\"\"
        # Get current portfolio
        portfolio = self.get_portfolio()
        
        # Get latest stock price
        stock_price = self.get_stock_price(stock)
        if not stock_price:
            return False, None, None
            
        # Add your buy logic here
        # Example: Buy if price is below 100
        if stock_price.last_trade_price < Decimal('100'):
            return True, stock_price.last_trade_price, Decimal('1')
            
        return False, None, None
        
    def should_sell(self, stock: str) -> tuple[bool, Optional[Decimal], Optional[Decimal]]:
        \"\"\"
        Determine if we should sell the stock.
        Returns:
            tuple[bool, Optional[Decimal], Optional[Decimal]]: 
                (should_sell, price_to_sell_at, quantity_to_sell)
        \"\"\"
        # Get current portfolio
        portfolio = self.get_portfolio()
        
        # Get latest stock price
        stock_price = self.get_stock_price(stock)
        if not stock_price:
            return False, None, None
            
        # Add your sell logic here
        # Example: Sell if price is above 110
        if stock_price.last_trade_price > Decimal('110'):
            # Find how much of this stock we own
            for position in portfolio:
                if position.stock == stock:
                    return True, stock_price.last_trade_price, position.quantity
                    
        return False, None, None
"""

def save_strategy(username: str, strategy_name: str, strategy_code: str) -> bool:
    """Save a new trading strategy."""
    try:
        # Create user's strategy directory if it doesn't exist
        strategy_dir = Path("data/users") / username / "strategies"
        strategy_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the strategy
        strategy_file = strategy_dir / f"{strategy_name}.py"
        strategy_file.write_text(strategy_code)
        return True
    except Exception as e:
        st.error(f"Error saving strategy: {e}")
        return False

def load_user_strategies(username: str) -> Dict[str, str]:
    """Load all strategies for a user."""
    strategies = {}
    strategy_dir = Path("data/users") / username / "strategies"
    
    if strategy_dir.exists():
        for strategy_file in strategy_dir.glob("*.py"):
            strategies[strategy_file.stem] = strategy_file.read_text()
            
    return strategies

def load_strategy_class(strategy_code: str, module_name: str = "temp_strategy"):
    """Load a strategy class from code string."""
    try:
        # Create a new module
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        if spec is None:
            raise ImportError(f"Could not create module spec for {module_name}")
            
        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise ImportError(f"Could not create module for {module_name}")
            
        # Add the module to sys.modules
        sys.modules[module_name] = module
        
        # Execute the strategy code in the module's namespace
        exec(strategy_code, module.__dict__)
        
        # Get the CustomStrategy class
        if not hasattr(module, 'CustomStrategy'):
            raise AttributeError("Strategy code must define a CustomStrategy class")
            
        return module.CustomStrategy
    except Exception as e:
        raise ImportError(f"Error loading strategy: {e}")

def render_new_strategy():
    """Render the new strategy page."""
    st.header("Trading Strategy Manager")
    
    # Load existing strategies
    strategies = load_user_strategies(st.session_state.user)
    
    # Strategy selection/creation
    st.subheader("Create or Edit Strategy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy_name = st.text_input("Strategy Name")
        
    with col2:
        if strategies:
            load_existing = st.selectbox(
                "Load Existing Strategy",
                ["New Strategy"] + list(strategies.keys())
            )
        else:
            load_existing = "New Strategy"
    
    # Code editor
    if load_existing != "New Strategy" and load_existing in strategies:
        strategy_code = st.text_area(
            "Strategy Code",
            value=strategies[load_existing],
            height=500
        )
    else:
        strategy_code = st.text_area(
            "Strategy Code",
            value=load_strategy_template(),
            height=500
        )
    
    # Save button
    if st.button("Save Strategy"):
        if not strategy_name:
            st.error("Please enter a strategy name")
        elif not strategy_code:
            st.error("Please enter strategy code")
        else:
            if save_strategy(st.session_state.user, strategy_name, strategy_code):
                st.success(f"Strategy '{strategy_name}' saved successfully!")
                st.experimental_rerun()
    
    # Strategy testing section
    if strategies:
        st.subheader("Test Strategy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_strategy = st.selectbox(
                "Select Strategy to Test",
                list(strategies.keys())
            )
            
        with col2:
            test_stock = st.selectbox(
                "Select Stock",
                ["AAPL", "GOOGL", "MSFT"]  # Add your stock list here
            )
        
        if st.button("Test Strategy"):
            try:
                # Load strategy class
                strategy_code = strategies[test_strategy]
                StrategyClass = load_strategy_class(strategy_code, f"strategy_{test_strategy}")
                
                # Create strategy instance
                strategy = StrategyClass(st.session_state.user)
                
                # Test buy signal
                should_buy, buy_price, buy_qty = strategy.should_buy(test_stock)
                st.write("Buy Signal:")
                st.write({
                    "Should Buy": should_buy,
                    "Price": buy_price,
                    "Quantity": buy_qty
                })
                
                # Test sell signal
                should_sell, sell_price, sell_qty = strategy.should_sell(test_stock)
                st.write("Sell Signal:")
                st.write({
                    "Should Sell": should_sell,
                    "Price": sell_price,
                    "Quantity": sell_qty
                })
                
            except Exception as e:
                st.error(f"Error testing strategy: {e}")
    
    # Strategy documentation
    with st.expander("Strategy Documentation"):
        st.markdown("""
        ## Creating a Trading Strategy
        
        Your trading strategy should inherit from `BaseStrategy` and implement two main methods:
        
        1. `should_buy(stock: str) -> tuple[bool, Optional[Decimal], Optional[Decimal]]`
           - Returns whether to buy, at what price, and what quantity
           
        2. `should_sell(stock: str) -> tuple[bool, Optional[Decimal], Optional[Decimal]]`
           - Returns whether to sell, at what price, and what quantity
           
        ### Available Methods
        
        - `get_portfolio()`: Get current portfolio positions
        - `get_stock_price(stock)`: Get latest stock price
        - `place_order(stock, order_type, price, quantity)`: Place a new order
        
        ### Example Strategy
        
        ```python
        def should_buy(self, stock: str):
            price = self.get_stock_price(stock)
            if price < Decimal('100'):
                return True, price, Decimal('1')
            return False, None, None
        ```
        """) 