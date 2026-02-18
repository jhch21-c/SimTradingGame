#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Source and destination directories
USER_TERMINAL = ROOT_DIR / "user_terminal"
SRC_DIR = ROOT_DIR / "src"
CONFIG_DIR = ROOT_DIR / "config"
DATA_DIR = ROOT_DIR / "data"

# Create necessary directories
directories = {
    "web": SRC_DIR / "web" / "pages",
    "core_trading": SRC_DIR / "core" / "trading",
    "core_utils": SRC_DIR / "core" / "utils",
    "database": SRC_DIR / "database",
    "bots": SRC_DIR / "bots" / "strategies",
    "price_readers": SRC_DIR / "bots" / "price_readers",
    "data_db": DATA_DIR / "db",
    "data_users": DATA_DIR / "users",
}

# Create directories
for dir_path in directories.values():
    ensure_dir(dir_path)

# File mappings (source -> destination)
file_mappings = {
    # Web interface files
    "main.py": directories["web"].parent / "main.py",
    "1_overview.py": directories["web"] / "overview.py",
    "2_new.py": directories["web"] / "new_strategy.py",
    "admin.py": directories["web"] / "admin.py",
    
    # Core trading files
    "order_matching_algorithm.py": directories["core_trading"] / "matching.py",
    "order_placement.py": directories["core_trading"] / "orders.py",
    "scheduler.py": directories["core_trading"] / "scheduler.py",
    
    # Price related files
    "read_stock_price.py": directories["price_readers"] / "stock_price.py",
    "update_stock_price.py": directories["price_readers"] / "price_updater.py",
    
    # Database files
    "credentials.db": directories["data_db"] / "credentials.db",
    "exchange.db": directories["data_db"] / "exchange.db",
    "stock_prices.db": directories["data_db"] / "stock_prices.db",
    
    # Configuration files
    "example_custom_buttons_bar_adj.json": CONFIG_DIR / "editor_buttons.json",
    "example_info_bar.json": CONFIG_DIR / "editor_info.json",
}

def move_file(src, dest):
    if os.path.exists(src):
        print(f"Moving {src} to {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)

def move_bot_directories():
    # Move bot directories
    bot_dirs = ["bot1", "dev"]
    for bot_dir in bot_dirs:
        src_dir = USER_TERMINAL / bot_dir
        if src_dir.exists():
            for py_file in src_dir.glob("*.py"):
                if py_file.name.startswith("bot"):
                    dest = directories["bots"] / f"strategy_{py_file.stem}.py"
                elif py_file.name == "order_placement.py":
                    continue  # Skip as we've moved this to core
                elif py_file.name.startswith("read_"):
                    dest = directories["price_readers"] / py_file.name
                else:
                    dest = directories["core_utils"] / py_file.name
                move_file(py_file, dest)

def main():
    # Move files according to mappings
    for src_name, dest_path in file_mappings.items():
        src_path = USER_TERMINAL / src_name
        move_file(src_path, dest_path)
    
    # Move bot directories
    move_bot_directories()
    
    print("File reorganization complete!")

if __name__ == "__main__":
    main() 