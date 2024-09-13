import sqlite3
import threading

from read_stock_price import get_stock_names

connect_stock = sqlite3.connect( "user_terminal/stock_prices.db",check_same_thread=False  )
connect_stock.execute('PRAGMA journal_mode=WAL;')
curs_stock = connect_stock.cursor()
connect_exchange = sqlite3.connect( "user_terminal/exchange.db" ,check_same_thread=False )
curs_exchange = connect_exchange.cursor()
connect_exchange.execute('PRAGMA journal_mode=WAL;')



def main():
    names=get_stock_names()
    for name in names:
        try:
            curs_exchange.execute(f"SELECT MAX(ask_bid_price_per_share) FROM active_orders WHERE (buy_or_sell = 'buy') AND (stock=?)",(name,))
            bid=curs_exchange.fetchone()[0]
            curs_exchange.execute(f"SELECT MIN(ask_bid_price_per_share) FROM active_orders WHERE (buy_or_sell = 'sell') AND (stock =?)",(name,))
            ask=curs_exchange.fetchone()[0]
            curs_exchange.execute(f"SELECT bid_pps,time_of_execution FROM past_orders WHERE reciept_number = (SELECT MAX(reciept_number) FROM past_orders WHERE  (stock =?)) AND  (stock =?)",(name,name))
            last=curs_exchange.fetchall()[0]
            if (bid,ask,last[0],last[1])==curs_stock.execute(f"SELECT * FROM [{name}]").fetchall()[-1][:4]:
                pass
            else:
                if (bid == None or ask == None):
                    pass
                else:
                    curs_stock.execute(f"INSERT INTO [{name}] (bid,ask,last_trade_price,time) VALUES (?,?,?,?)",(bid,ask,last[0],last[1]))
            connect_stock.commit()
        except:
             pass

if __name__=="__main__":
    main()
