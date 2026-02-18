import os
from pathlib import Path

# Base directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"

# Database configurations
DATABASE_DIR = BASE_DIR / "data" / "db"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

CREDENTIALS_DB = DATABASE_DIR / "credentials.db"
STOCK_PRICES_DB = DATABASE_DIR / "stock_prices.db"
EXCHANGE_DB = DATABASE_DIR / "exchange.db"

# User data configuration
USER_DATA_DIR = BASE_DIR / "data" / "users"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Trading configuration
INITIAL_CASH = 1000.0
DEFAULT_COMMISSION = 0.001  # 0.1%

# Web interface configuration
STREAMLIT_CONFIG = {
    "page_title": "SimTrading Game",
    "page_icon": "📈",
    "layout": "wide",
}

# Bot configuration
BOT_STRATEGIES_DIR = SRC_DIR / "bots" / "strategies"
BOT_STRATEGIES_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "app.log",
        },
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
} 