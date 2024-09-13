from read_stock_price import *
import random
from order_matching_algorithm import *

connect_exchange = sqlite3.connect( "exchange.db",check_same_thread=False )
curs_exchange = connect_exchange.cursor()
connect_exchange.execute('PRAGMA journal_mode=WAL;')

def main5(username):
    names=get_stock_names()
    stock = names[random.randint(0, len(names) - 1)]
    percent_adjust=round(random.uniform(10,20)/100,4)
    buy_sell="buy"
    pps=round(current_ask_price(stock)*(1+percent_adjust),2)
    quantity=round(random.uniform(100, 500), 1)
    execute_order(username=username,buy_sell=buy_sell,pps=pps,quantity=quantity,stock=stock)

# import time
# import threading
# from datetime import datetime
#
# import numpy as np
#
# from order_matching_algorithm import *
# from read_stock_price import *
# from numpy import random
# from multiprocessing import Process
#
# connect_exchange = sqlite3.connect( "exchange.db",check_same_thread=False )
# curs_exchange = connect_exchange.cursor()
# curs_exchange.execute('PRAGMA journal_mode=WAL;')
# import bot2
# import bot4
# import bot5
# def main5(username):
#     names=get_stock_names()
#     stock = names[random.randint(0, len(names) - 1)]
#     buy_sell="buy"
#     mu = current_ask_price(stock)+20
#     sigma = 20
#     pps=0
#     while pps<mu:
#         pps = random.normal(loc=mu, scale=sigma)
#
#     quantity = round(abs(pps-current_ask_price(stock))*100,2)
#     execute_order(username=username,buy_sell=buy_sell,pps=pps,quantity=quantity,stock=stock)