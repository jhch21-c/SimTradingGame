import sqlite3
import time
from datetime import datetime

from time import gmtime, strftime
from update_stock_price import main
connect_stock = sqlite3.connect( "user_terminal/stock_prices.db",check_same_thread=False )
curs_stock = connect_stock.cursor()
connect_stock.execute('PRAGMA journal_mode=WAL;')
from multiprocessing import Process
import threading
connect_exchange = sqlite3.connect( "user_terminal/exchange.db",check_same_thread=False )
curs_exchange = connect_exchange.cursor()
connect_exchange.execute('PRAGMA journal_mode=WAL;')

connect_credentials = sqlite3.connect("user_terminal/credentials.db",check_same_thread=False)
curs_credentials = connect_credentials.cursor()

def tuple_to_array(tuple):
    array=[]
    for data in  tuple:
        temp = []  # creates 2d array for all credentials
        for x in data:
            temp.append( x )
        array.append( temp )  #3D array
    return array

def cancel_order(ordernum):
    curs_exchange.execute("DELETE FROM active_orders WHERE (order_number)=(?)",(ordernum,))

def execute_trade(username,buy_sell,pps,quantity,stock,trade_to_execute):
    # pps and username varies of whether buy_sell is buy or sell since if user is seller then bid price will be the one on the exchange whereas if user is buyer then bid price will be inputted by system

    if buy_sell=="buy":
        conn_buyer=sqlite3.connect("user_terminal/"+username+"/"+username+".db",check_same_thread=False)
        curs_buyer=conn_buyer.cursor()
        conn_seller = sqlite3.connect("user_terminal/"+str(trade_to_execute[2]) +"/"+str(trade_to_execute[2]) + ".db",check_same_thread=False)
        curs_seller = conn_seller.cursor()
        pps=pps

    if buy_sell == "sell":
        conn_seller = sqlite3.connect("user_terminal/"+username+"/"+username+".db",check_same_thread=False)
        curs_seller = conn_seller.cursor()
        conn_buyer = sqlite3.connect("user_terminal/"+str(trade_to_execute[2]) +"/"+str(trade_to_execute[2]) + ".db",check_same_thread=False)
        curs_buyer = conn_buyer.cursor()
        pps=trade_to_execute[3]

    try:
        old_quantity=(curs_seller.execute("SELECT quantity FROM portfolio WHERE stock=?",(stock,)).fetchone()[0])
    except:
        old_quantity=0
    if (old_quantity == quantity) and (old_quantity!=0):
        curs_seller.execute("DELETE FROM portfolio WHERE stock=?", (stock,))
    elif (old_quantity - quantity)>0:
        curs_seller.execute("UPDATE portfolio SET (quantity,long_or_short)=(?,?) WHERE stock=(?)",((old_quantity-quantity),"long",stock))
    elif (old_quantity - quantity)<0:
        curs_seller.execute("UPDATE portfolio SET (quantity,long_or_short)=(?,?) WHERE stock=(?)",((old_quantity-quantity),"short",stock))
    old_cash=(curs_seller.execute("SELECT quantity FROM portfolio WHERE stock='cash'",).fetchone()[0])
    curs_seller.execute("UPDATE portfolio SET (quantity)=(?) WHERE stock='cash'", (old_cash+(pps * quantity),))
    ###seller done
    try:
        old_quantity_2=(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock=?",(stock,)).fetchone()[0])
    except:
        old_quantity_2=0
    if old_quantity_2 == 0:
        curs_buyer.execute("INSERT INTO portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",(stock, quantity, pps, "long"))
    elif old_quantity_2 +quantity>0:
        curs_buyer.execute("UPDATE portfolio SET (quantity,long_or_short)=(?,?) WHERE (stock)=(?)", (old_quantity_2+quantity,"long", stock))
    elif old_quantity_2 +quantity<0:
        curs_buyer.execute("UPDATE portfolio SET (quantity,long_or_short)=(?,?) WHERE (stock)=(?)", (old_quantity_2+quantity,"short", stock))
    old_cash_2=(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock='cash'",).fetchone()[0])
    curs_buyer.execute("UPDATE portfolio SET (quantity)=(?) WHERE stock='cash'", (old_cash_2*(pps * quantity),))

    conn_buyer.commit()
    conn_seller.commit()
    connect_exchange.commit()



def quantity_adjustments(username,buy_sell,pps,quantity,stock,trade_to_execute,ordernum):
    if trade_to_execute[4]<quantity:

        execute_trade(username, buy_sell, pps, trade_to_execute[4], stock, trade_to_execute)
        if buy_sell=="buy":
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock,username,pps ,trade_to_execute[4] ,trade_to_execute[3] ,trade_to_execute[2] ,time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            #print("executed order:",[recieptnum,username,pps ,trade_to_execute[4] ,trade_to_execute[3] ,trade_to_execute[2]])
        else:
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock,trade_to_execute[2],trade_to_execute[3] ,trade_to_execute[4] ,pps ,username ,time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            #print("executed order:",[recieptnum,username,pps ,trade_to_execute[4] ,trade_to_execute[3] ,trade_to_execute[2]])
        curs_exchange.execute("DELETE FROM active_orders WHERE order_number=?", ( trade_to_execute[0],))

        curs_exchange.execute("UPDATE active_orders SET (quantity)=(?)  WHERE (order_number)=(?)",(quantity-trade_to_execute[4],ordernum))

        check_database(username, buy_sell, pps, quantity-trade_to_execute[4], stock, ordernum)


        #add sellers quantity of stock to buyers portfolio then remove sellers stock from sellers portfolio, modify buyers active order by buyer quantity- sellers quantity
    if trade_to_execute[4]>quantity:

        execute_trade(username, buy_sell, pps, quantity, stock, trade_to_execute)
        if buy_sell == "buy":
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock, username, pps, quantity, trade_to_execute[3], trade_to_execute[2],
                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            #print("executed order:",[recieptnum,stock, username, pps, quantity, trade_to_execute[3], trade_to_execute[2]])
        else:
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock , trade_to_execute[2], trade_to_execute[3], quantity, pps, username,
                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            #print("executed order:",[recieptnum,stock , trade_to_execute[2], trade_to_execute[3], quantity, pps, username])
        curs_exchange.execute("DELETE FROM active_orders WHERE order_number=?", (ordernum,))

        curs_exchange.execute("UPDATE active_orders SET(quantity)=(?) WHERE (order_number)=(?)",(trade_to_execute[4]-quantity, trade_to_execute[0]))

        check_database(trade_to_execute[2], trade_to_execute[1], trade_to_execute[3], trade_to_execute[4]-quantity, trade_to_execute[5], trade_to_execute[0])


        #add buyers quantity of stock to buyers portfolio then remove buyer from active orders and keep seller on active order with reduced quantity
    if trade_to_execute[4]==quantity:

        execute_trade(username, buy_sell, pps, trade_to_execute[4], stock, trade_to_execute)

        curs_exchange.execute("DELETE FROM active_orders WHERE order_number=?", (ordernum,))
        curs_exchange.execute("DELETE FROM active_orders WHERE order_number=?", ( trade_to_execute[0],))

        if buy_sell == "buy":
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock , username, pps, trade_to_execute[4], trade_to_execute[3], trade_to_execute[2],
                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            print("executed order:",[recieptnum, username, pps, trade_to_execute[4], trade_to_execute[3], trade_to_execute[2]])
        else:
            recieptnum = int(open("user_terminal/" + "recieptnum.txt", "r").readline())
            new = open("user_terminal/" + "recieptnum.txt", "w")
            new.write(str(recieptnum + 1))
            new.close()
            curs_exchange.execute(
                "INSERT INTO past_orders (reciept_number,stock,buyer_username,bid_pps,quantity,ask_pps,seller_username,time_of_execution) VALUES (?,?,?,?,?,?,?,?)",
                (recieptnum,stock ,trade_to_execute[2], trade_to_execute[3], trade_to_execute[4], pps, username,
                 time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            print("executed order:",[recieptnum, trade_to_execute[2], trade_to_execute[3], trade_to_execute[4], pps, username])

    connect_exchange.commit()
    connect_stock.commit()

def check_incomplete():
    for username in [row[0] for row in curs_credentials.execute("SELECT username From Credentials").fetchall()]:

        orders=tuple_to_array(curs_exchange.execute("SELECT * FROM active_orders WHERE (username)=(?)",(username,)).fetchall())
        for order in orders:
            difference=datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),"%Y-%m-%d %H:%M:%S")- datetime.strptime(order[6], "%Y-%m-%d %H:%M:%S")
            if difference.seconds>60:
                if order[1]=="buy":
                    try:
                        # new_price = curs_exchange.execute(
                        #     "SELECT MIN(ask_bid_price_per_share) FROM active_orders WHERE  (stock =?) AND (buy_or_sell='sell') AND (username!=?) AND (username!='admin')",
                        #     (order[5], order[2])).fetchone()
                        cancel_order( order[0])

                        # execute_order(username=username, buy_sell=order[1], pps=new_price[0], quantity=order[4],
                        #                   stock=order[5])

                    except:
                        pass

                if order[1]=="sell":
                    try:
                        # new_price = curs_exchange.execute(
                        #     "SELECT MAX(ask_bid_price_per_share) FROM active_orders WHERE  (stock =?) AND (buy_or_sell='buy') AND (username!=?)",
                        #     (order[5], order[2])).fetchone()
                        cancel_order( order[0])
                        # execute_order(username=username, buy_sell=order[1], pps=new_price[0], quantity=order[4], stock=order[5])
                    except:
                        pass
            connect_exchange.commit()



def check_database(username,buy_sell,pps,quantity,stock,ordernum):

    main()
    if buy_sell=="buy":

        curs_exchange.execute(
            "SELECT * FROM active_orders WHERE (stock = ?) AND (username != ?) AND (ask_bid_price_per_share <= ?)  AND (buy_or_sell != ?) ORDER BY abs(ask_bid_price_per_share - ?), order_number",(stock, username,pps ,buy_sell,pps))
    if buy_sell == "sell":
        curs_exchange.execute(
            "SELECT * FROM active_orders WHERE (stock = ?) AND (username != ?) AND (ask_bid_price_per_share >= ?)  AND (buy_or_sell != ?) ORDER BY abs(ask_bid_price_per_share - ?), order_number",(stock, username, pps, buy_sell, pps))
    orders=tuple_to_array(curs_exchange.fetchall())
    #print("potential stocks to buy:",orders)
    if len(orders)==0:
        pass
        #print("currently no active orders to match current order")
    else:
        quantity_adjustments(username,buy_sell,pps,quantity,stock,orders[0],ordernum)

def check_funds(username,buy_sell,pps,quantity):
    if buy_sell=="buy":
        conn_buyer = sqlite3.connect("user_terminal/"+username+"/"+username+".db",check_same_thread=False)
        curs_buyer = conn_buyer.cursor()
        if float(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock='cash'").fetchone()[0])<float(quantity*pps):
            print("insufficent funds",float(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock='cash'").fetchone()[0]))
            return False
        else:
            return True
    else:
        return True

def check_stock(username,buy_sell,stock,quantity):
    if buy_sell=="sell":
        conn_buyer = sqlite3.connect("user_terminal/"+username+"/"+username+".db",check_same_thread=False)
        curs_buyer = conn_buyer.cursor()
        if float(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock=?",(stock,)).fetchone()[0])<float(quantity):
            #print("insufficent stock to sell",float(curs_buyer.execute("SELECT quantity FROM portfolio WHERE stock=?",(stock)).fetchone()[0]))
            return False
        else:
            return True
    else:
        return True
def recheck_all():
    orders=tuple_to_array(curs_exchange.execute("SELECT * FROM active_orders").fetchall())
    for order in orders:
        check_database(order[2], order[1], order[3], order[4], order[5], order[0])



def execute_order(username,buy_sell,pps,quantity,stock):
    if check_funds(username,buy_sell,pps,quantity)==True:
        if check_stock(username, buy_sell, stock, quantity) == True:

            ordernum=int(open("user_terminal/"+"ordernum.txt","r").readline())
            #print("current user:",[buy_sell,username,pps,quantity,stock])
            curs_exchange.execute("INSERT INTO  active_orders (order_number,buy_or_sell, username, ask_bid_price_per_share,quantity, stock, time_of_execution) VALUES (?,?,?,?,?,?,?)",
                                     (ordernum,buy_sell,username,pps,quantity, stock ,time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))

            connect_exchange.commit()
            new = open("user_terminal/"+"ordernum.txt", "w")
            new.write(str(ordernum + 1))
            new.close()
            check_database(username,buy_sell,pps,quantity,stock,ordernum)
        else:
            return
    else:
         return



#to use
# from order_matching_algorithm import execute_order
# execute_order(...)


