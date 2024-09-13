import time
import threading
from datetime import datetime

import numpy as np

from order_matching_algorithm import *
from read_stock_price import *
from numpy import random
from multiprocessing import Process

connect_exchange = sqlite3.connect( "exchange.db",check_same_thread=False )
curs_exchange = connect_exchange.cursor()
curs_exchange.execute('PRAGMA journal_mode=WAL;')
import bot2
import bot4
import bot5
def main1(username):
    names=get_stock_names()
    stock = names[random.randint(0, len(names) - 1)]
    choice=np.random.randint(2)
    if username=="bot1":
        buy_sell="buy"
        mu = current_last_price(stock)
        sigma = 3
        pps = random.normal(loc=mu, scale=sigma)
    else:
        buy_sell="sell"
        mu = current_last_price(stock)
        sigma = 3
        pps = random.normal(loc=mu, scale=sigma)

    quantity = round(abs(pps-current_last_price(stock))*100,2)
    execute_order(username=username,buy_sell=buy_sell,pps=pps,quantity=quantity,stock=stock)



if __name__=="__main__":
    while True:
        lock=threading.Lock()

        threading.Thread(target=bot2.main2("bot1")).start()
        threading.Thread(target=bot2.main2("dev")).start()
        # threading.Thread(target=bot2.main2("bot1")).start()
        # threading.Thread(target=bot2.main2("dev")).start()
        # threading.Thread(target=bot2.main2("bot1")).start()
        # threading.Thread(target=bot2.main2("dev")).start()
        # threading.Thread(target=check_incomplete("bot1",100)).start()
        # threading.Thread(target=check_incomplete("dev",100)).start()
        # threading.Thread(target=recheck_all()).start()


        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        # threading.Thread(target=bot5.main5("bot1")).start()
        # threading.Thread(target=bot5.main5("dev")).start()
        #
        #
        # threading.Thread(target=bot4.main4("bot1")).start()
        # threading.Thread(target=bot4.main4("dev")).start()#
        # threading.Thread(target=bot4.main4("bot1")).start()
        # threading.Thread(target=bot4.main4("dev")).start()
        # threading.Thread(target=bot4.main4("bot1")).start()
        # threading.Thread(target=bot4.main4("dev")).start()
        # threading.Thread(target=bot4.main4("bot1")).start()
        # threading.Thread(target=bot4.main4("dev")).start()

