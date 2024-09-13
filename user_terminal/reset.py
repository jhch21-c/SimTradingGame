import os
import time
import threading
from datetime import datetime


from order_placement import *

from read_stock_price import *
connect_exchange = sqlite3.connect( "user_terminal/"+"exchange.db",check_same_thread=False )
curs_exchange = connect_exchange.cursor()
connect_exchange.execute('PRAGMA journal_mode=WAL;')

import sqlite3


def wipe_all_records():
    # Connect to the SQLite database
    conn = sqlite3.connect("user_terminal/"+"exchange.db")
    cursor = conn.cursor()

    # Retrieve the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all records from each table
    for table_name in tables:
        cursor.execute(f"DELETE FROM {table_name[0]};")
        print(f"All records from table {table_name[0]} deleted.")

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()
    print("All records have been wiped.")


# Example usage
wipe_all_records()
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
connect_credentials = sqlite3.connect("user_terminal/"+"credentials.db")
curs_credentials = connect_credentials.cursor()





for user in [row[0] for row in curs_credentials.execute("SELECT username From Credentials").fetchall()]:
    try:
        user_db = os.path.join(BASE_DIR, user + "/" + user + ".db")
        conn_user = sqlite3.connect(user_db)
        curs_user = conn_user.cursor()
        curs_user.execute("DELETE FROM portfolio")
        curs_user.execute(
            "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
            ("cash", 1000, 1, "long"))
        if user == "admin":
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("AAPL", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("AMZN", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("BABA", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("FB", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("GOOGL", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("MSFT", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("NFLX", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("NVDA", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("ORCL", 1000, 1, "long"))
            curs_user.execute(
                "INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",
                ("TSLA", 1000, 1, "long"))

        conn_user.commit()
        conn_user.close()
    except:
        pass

def wipe_all_but_first_record():
    # Connect to the SQLite database
    conn = sqlite3.connect("user_terminal/"+"stock_prices.db")
    cursor = conn.cursor()

    # Retrieve the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Delete all records but the first one from each table
    for table_name in tables:
        # Get the rowid of the first record
        cursor.execute(f'SELECT rowid FROM "{table_name[0]}" LIMIT 1;')
        first_record_rowid = cursor.fetchone()

        if first_record_rowid:
            # Delete all records except the first one
            cursor.execute(
                f'DELETE FROM "{table_name[0]}" WHERE rowid NOT IN (SELECT rowid FROM "{table_name[0]}" LIMIT 1);')
            print(f'All records except the first one from table {table_name[0]} deleted.')
        else:
            print(f'Table {table_name[0]} is empty.')

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()
    print("All records except the first one have been wiped.")


# Example usage
wipe_all_but_first_record()

new = open("user_terminal/ordernum.txt", "w")
new.write(str(0))
new.close()

new = open("user_terminal/recieptnum.txt", "w")
new.write(str(0))
new.close()

def ipo(username):
    names=get_stock_names()
    for stock in names:
        mu = current_ask_price(stock)
        execute_order(username=username,buy_sell="sell",pps=mu,quantity=1000,stock=stock)
ipo("admin")
