import streamlit as st
from pathlib import Path
import time
from typing import Literal

from ..core.utils.helpers import hash_password
from ..database.manager import CredentialsDB
from .pages.overview import render_overview
from .pages.new_strategy import render_new_strategy

# Try to import admin page, but don't fail if it doesn't exist
try:
    from .pages.admin import render_admin
    HAS_ADMIN = True
except ImportError:
    HAS_ADMIN = False
    def render_admin():
        st.error("Admin page not available")

# Configure Streamlit page
st.set_page_config(
    page_title="SimTrading Game",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
credentials_db = CredentialsDB()

def init_session_state():
    """Initialize session state variables."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"

def add_credentials(username: str, password: str) -> bool:
    """Add new user credentials."""
    try:
        with credentials_db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO Credentials (Username, Password) VALUES (?, ?)",
                (username, hash_password(password))
            )
        return True
    except Exception as e:
        st.error(f"Error adding credentials: {e}")
        return False

def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials."""
    with credentials_db.get_cursor() as cursor:
        result = cursor.execute(
            "SELECT Password FROM Credentials WHERE Username = ?",
            (username,)
        ).fetchone()
        
    if result:
        return result[0] == hash_password(password)
    return False

def render_login():
    """Render the login page."""
    st.title("SimTrading Game")
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Login"):
                if verify_credentials(username, password):
                    st.session_state.user = username
                    st.session_state.current_page = "overview"
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
                    
        with col2:
            if st.form_submit_button("Register"):
                if add_credentials(username, password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed")

def render_navigation():
    """Render the navigation sidebar."""
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("Overview"):
            st.session_state.current_page = "overview"
            st.experimental_rerun()
            
        if st.button("Trading Strategies"):
            st.session_state.current_page = "strategies"
            st.experimental_rerun()
            
        if HAS_ADMIN and st.session_state.user == "admin" and st.button("Admin Panel"):
            st.session_state.current_page = "admin"
            st.experimental_rerun()
            
        st.markdown("---")
        
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.current_page = "login"
            st.experimental_rerun()

def main():
    """Main application entry point."""
    init_session_state()
    
    if st.session_state.user is None:
        render_login()
        return
        
    render_navigation()
    
    if st.session_state.current_page == "overview":
        render_overview()
    elif st.session_state.current_page == "strategies":
        render_new_strategy()
    elif st.session_state.current_page == "admin":
        render_admin()
    else:
        st.error("Unknown page")

if __name__ == "__main__":
    main() 