from order_matching_algorithm import execute_order
from read_stock_price import *
import random
def main(username):
    names=get_stock_names()
    stock = names[random.randint(0, len(names) - 1)]
    choice=random.randint(0,1)
    percent_adjust=round(random.uniform(-20,20)/100,4)
    print(percent_adjust)
    if choice==0:
        buy_sell="buy"
        pps=round(current_last_price(stock)*(1-percent_adjust),2)
    else:
        buy_sell="sell"
        pps=round(current_last_price(stock)*(1+percent_adjust),2)
    quantity=round(random.uniform(1, 50), 1)
    execute_order(username=username,buy_sell=buy_sell,pps=round(pps,2),quantity=quantity,stock=stock)

if __name__=="__main__":
    for x in range(1000):
        main("bot1")
        main("dev")