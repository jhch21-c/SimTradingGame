import time
import threading
from datetime import datetime

import numpy as np

from order_placement import *

from read_stock_price import *
from numpy import random
connect_exchange = sqlite3.connect( "exchange.db",check_same_thread=False )
curs_exchange = connect_exchange.cursor()
connect_exchange.execute('PRAGMA journal_mode=WAL;')

def main2(username):
    names=get_stock_names()
    stock = names[random.randint(0, len(names) - 1)]
    choice=np.random.randint(2)
    if username=="bot1":
        buy_sell="buy"
        mu = current_ask_price(stock)
        sigma = 3
        pps = random.normal(loc=mu, scale=sigma)
    else:
        buy_sell="sell"
        mu = current_bid_price(stock)
        sigma = 3
        pps = random.normal(loc=mu, scale=sigma)
    quantity = round(abs(pps-mu)*100,2)
    if quantity==0:
        quantity=100
    execute_order(username=username,buy_sell=buy_sell,pps=pps,quantity=quantity,stock=stock)
if __name__=="__main__":
        main2("bot1")
        main2("dev")