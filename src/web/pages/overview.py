import streamlit as st
import pandas as pd
import numpy as np
from decimal import Decimal
from typing import Dict, List, Optional, cast

from ...core.trading.exchange import Exchange
from ...database.manager import UserDB, StockPricesDB
from ...core.utils.helpers import (
    calculate_portfolio_value,
    calculate_pnl,
    format_money,
    format_quantity
)

def get_stock_list() -> List[str]:
    """Get list of available stocks."""
    stock_db = StockPricesDB()
    with stock_db.get_cursor() as cursor:
        stocks = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return [row[0] for row in stocks]

def get_stock_price_data(stock: str) -> Dict[str, List]:
    """Get price data for a stock."""
    stock_db = StockPricesDB()
    with stock_db.get_cursor() as cursor:
        data = cursor.execute(f"""
            SELECT last_trade_price, time 
            FROM [{stock}] 
            ORDER BY time DESC 
            LIMIT 100
        """).fetchall()
        
    return {
        "last_trade_price": [row[0] for row in data],
        "time": [row[1] for row in data]
    }

def get_portfolio_data(username: str) -> pd.DataFrame:
    """Get user's portfolio data."""
    user_db = UserDB(username)
    with user_db.get_cursor() as cursor:
        data = cursor.execute("SELECT * FROM portfolio").fetchall()
        
    if not data:
        return pd.DataFrame(columns=['stock', 'quantity', 'initial_price', 'position_type'])
        
    df = pd.DataFrame({
        'stock': [row[0] for row in data],
        'quantity': [row[1] for row in data],
        'initial_price': [row[2] for row in data],
        'position_type': [row[3] for row in data],
    })
    return cast(pd.DataFrame, df)

def get_active_orders(username: str) -> pd.DataFrame:
    """Get user's active orders."""
    exchange = Exchange()
    with exchange.exchange_db.get_cursor() as cursor:
        data = cursor.execute("""
            SELECT order_number, stock, buy_or_sell, 
                   ask_bid_price_per_share, quantity, time_of_execution 
            FROM active_orders 
            WHERE username = ?
            ORDER BY time_of_execution DESC
        """, (username,)).fetchall()
        
    if not data:
        return pd.DataFrame(columns=[
            'Order #', 'Stock', 'Type', 'Price', 'Quantity', 'Time'
        ])
        
    df = pd.DataFrame({
        'Order #': [str(row[0]) for row in data],  # Convert to string here
        'Stock': [row[1] for row in data],
        'Type': [row[2] for row in data],
        'Price': [row[3] for row in data],
        'Quantity': [row[4] for row in data],
        'Time': [row[5] for row in data],
    })
    return cast(pd.DataFrame, df)

def get_order_history(username: str) -> pd.DataFrame:
    """Get user's order history."""
    exchange = Exchange()
    with exchange.exchange_db.get_cursor() as cursor:
        # Get buy orders
        buys = cursor.execute("""
            SELECT receipt_number, stock, bid_pps, quantity, time_of_execution 
            FROM past_orders 
            WHERE buyer_username = ?
            ORDER BY time_of_execution DESC
        """, (username,)).fetchall()
        
        # Get sell orders
        sells = cursor.execute("""
            SELECT receipt_number, stock, ask_pps, quantity, time_of_execution 
            FROM past_orders 
            WHERE seller_username = ?
            ORDER BY time_of_execution DESC
        """, (username,)).fetchall()
        
    if not buys and not sells:
        return pd.DataFrame(columns=[
            'Receipt #', 'Stock', 'Type', 'Price', 'Quantity', 'Time'
        ])
        
    orders = []
    for row in buys:
        orders.append({
            'Receipt #': row[0],
            'Stock': row[1],
            'Type': 'BUY',
            'Price': row[2],
            'Quantity': row[3],
            'Time': row[4]
        })
        
    for row in sells:
        orders.append({
            'Receipt #': row[0],
            'Stock': row[1],
            'Type': 'SELL',
            'Price': row[2],
            'Quantity': row[3],
            'Time': row[4]
        })
        
    df = pd.DataFrame(orders)
    if not df.empty:
        df = df.sort_values('Time', ascending=False)
    return cast(pd.DataFrame, df)

def render_overview():
    """Render the overview page."""
    st.header("Trading Overview")
    
    # Stock selection and chart
    stocks = get_stock_list()
    if not stocks:
        st.warning("No stocks available for trading")
        return
        
    selected_stock = st.selectbox("Select Stock", stocks)
    
    if selected_stock:
        data = get_stock_price_data(selected_stock)
        if data["time"]:  # Check if we have any data
            chart_data = pd.DataFrame(data)
            chart_data.set_index('time', inplace=True)
            st.line_chart(chart_data)
        else:
            st.warning("No price data available for this stock")
        
        # Trading interface
        with st.form("trade_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                order_type = st.selectbox("Order Type", ["BUY", "SELL"])
            with col2:
                quantity = st.number_input("Quantity", min_value=0.0001, step=0.0001)
            with col3:
                price = st.number_input("Price", min_value=0.0001, step=0.0001)
                
            if st.form_submit_button("Place Order"):
                exchange = Exchange()
                try:
                    order_number = exchange.place_order(
                        username=st.session_state.user,
                        stock=selected_stock,
                        order_type=order_type.lower(),
                        price=Decimal(str(price)),
                        quantity=Decimal(str(quantity))
                    )
                    st.success(f"Order placed successfully! Order #{order_number}")
                except Exception as e:
                    st.error(f"Error placing order: {e}")
    
    # Portfolio section
    st.header("Portfolio")
    portfolio_df = get_portfolio_data(st.session_state.user)
    st.dataframe(portfolio_df)
    
    # Active orders
    st.header("Active Orders")
    active_orders_df = get_active_orders(st.session_state.user)
    st.dataframe(active_orders_df)
    
    # Only show cancel button if we have orders
    if isinstance(active_orders_df, pd.DataFrame) and not active_orders_df.empty and 'Order #' in active_orders_df.columns:
        try:
            # Get order numbers directly from the DataFrame
            order_numbers = []
            for idx in range(len(active_orders_df)):
                order_numbers.append(active_orders_df.iloc[idx]['Order #'])
            
            if order_numbers:
                order_to_cancel = st.selectbox("Select order to cancel", order_numbers)
                if st.button("Cancel Order"):
                    exchange = Exchange()
                    if exchange.cancel_order(order_to_cancel):
                        st.success("Order cancelled successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to cancel order")
        except Exception:
            st.error("Error loading order numbers")
    else:
        st.info("No active orders")
    
    # Order history
    st.header("Order History")
    history_df = get_order_history(st.session_state.user)
    if not history_df.empty:
        st.dataframe(history_df)
    else:
        st.info("No order history") 