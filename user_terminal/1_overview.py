import os
import sqlite3
import time

import streamlit as st
import pandas as pd
import numpy as np
import random
from code_editor import code_editor
import json
from github import Github
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ex_path = os.path.join(BASE_DIR,"exchange.db")
connect_exchange = sqlite3.connect( ex_path )
curs_exchange = connect_exchange.cursor()


user_db_path = os.path.join(BASE_DIR,st.session_state.user +"/"+st.session_state.user + ".db")
connect_user = sqlite3.connect(user_db_path,check_same_thread=False)
curs_user = connect_user.cursor()

stock_db_path = os.path.join(BASE_DIR, "stock_prices.db")
conn_stock = sqlite3.connect(stock_db_path,check_same_thread=False)
curs_stock = conn_stock.cursor()
html_style_string = '''<style>
@media (min-width: 576px)
section div.block-container {
  padding-left: 20rem;
}
section div.block-container {
  padding-left: 4rem;
  padding-right: 4rem;
  max-width: 80rem;
}  

</style>'''
st.markdown(html_style_string, unsafe_allow_html=True)
st_autorefresh()
def tuple_to_array_str(tuple):
    array = []
    for data in tuple:
        temp = []  # creates 2d array for all credentials
        for x in data:
            temp.append(str(x))
        array.append(temp)  # 3D array
    return array

#
tab1, tab2= st.tabs(["overview",  "modify strategy"])
with tab1:
    name = [row[0] for row in curs_stock.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    stock = st.selectbox("Select which stock you would like to use the strategy on", name)

    # row0=[row[0] for row in curs_stock.execute(f"SELECT bid FROM [{stock}]").fetchall()]
    # row1=[row[0] for row in curs_stock.execute(f"SELECT ask FROM [{stock}]").fetchall()]
    row2 = [row[0] for row in curs_stock.execute(f"SELECT last_trade_price FROM [{stock}]").fetchall()]
    row3 = [row[0] for row in curs_stock.execute(f"SELECT time FROM [{stock}]").fetchall()]
    # "bid": row0,"ask":row1,
    data = {"last trade price": row2, "time": row3}
    try:
        chart_data = pd.DataFrame(data)
        chart_data.set_index('time', inplace=True)
        st.line_chart(chart_data, use_container_width=True)
    except:
        st.warning("Loading....")
    col1, col2 = st.columns([2, 2])
    tile4 = st.container(height=490)
    tile4.title("Current portfolio")
    data = {
        'stock': [row[0] for row in curs_user.execute("SELECT * FROM portfolio").fetchall()],
        'quantity': [row[1] for row in curs_user.execute("SELECT * FROM portfolio").fetchall()],
        'initial price per share': [row[2] for row in curs_user.execute("SELECT * FROM portfolio").fetchall()],
        'long/short': [row[3] for row in curs_user.execute("SELECT * FROM portfolio").fetchall()],

    }
    ##change the array in line 14 for the strategies true performance

    df = pd.DataFrame(data)
    event = tile4.dataframe(df, hide_index=True, use_container_width=True)

    with col1:
        tile1 = col1.container(height=520)
        tile1.title("view my current orders")
        try:
            df = pd.DataFrame(curs_exchange.execute("SELECT order_number,stock,buy_or_sell,ask_bid_price_per_share,quantity,time_of_execution FROM active_orders WHERE (username)=(?)",(st.session_state.user,)).fetchall()).sort_values(5,ascending=False)
        except:
            df=[]
        tile1.dataframe(df, use_container_width=True,hide_index=True)
    with col2:
        tile2 = col2.container(height=520)
        tile2.title("view my past orders ")
        past=[]
        st.write()
        for x in tuple_to_array_str(curs_exchange.execute("SELECT reciept_number,stock,bid_pps,quantity,time_of_execution FROM past_orders WHERE (buyer_username)=(?)",(st.session_state.user,)).fetchall()):
            past.append(x)

        for x in tuple_to_array_str(curs_exchange.execute("SELECT reciept_number,stock,ask_pps,quantity,time_of_execution FROM past_orders WHERE (seller_username)=(?)",(st.session_state.user,)).fetchall()):
            past.append(x)
        try:
            df = pd.DataFrame(past).sort_values(4,ascending=False)
        except:
            df=[]
        tile2.dataframe(df, use_container_width=True,hide_index=True )


with tab2:
    st.title("Currently active strategies")
    state=[]
    for x in[row[2] for row in curs_user.execute("SELECT * FROM strategy").fetchall()]:
        if x==1:
            state.append(True)
        else:
            state.append(False)
    checkbox_states = [False] * len(state)

    data = {
        "select to delete":checkbox_states,
        'strategy name': [row[0] for row in curs_user.execute("SELECT * FROM strategy").fetchall()],
        'location': [row[1] for row in curs_user.execute("SELECT * FROM strategy").fetchall()],
        'on or off':state
    }

    df = pd.DataFrame(data)

    event = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={"select to delete":st.column_config.Column(width="small"),"on or off":st.column_config.Column(width="small")},
        disabled = ["strategy name", "location"]
    )
    rows_array = []

    if st.button("save state"):
        for index,x in event.iterrows():
            rows_array.append(x.tolist())
        for a in rows_array:
            state=0
            if a[3]==True:
                state=1
            curs_user.execute("UPDATE strategy SET (on_off)=(?)  WHERE (strategy_name)=(?)",(state,a[1]))
        connect_user.commit()

        st.success("state has been saved")

    if st.button("delete", type="primary"):
            for index, x in event.iterrows():
                rows_array.append(x.tolist())
            deleted_something=False
            for a in rows_array:
                if a[0] == True:
                    deleted_something=True
                    curs_user.execute("DELETE FROM  strategy  WHERE (strategy_name)=(?)", (a[1],))
            connect_user.commit()
            if deleted_something==True:
                st.success("strategy has been removed")
            else:
                st.error("Select a row in the selected column to delete a row")

#########################################################################
    option = st.selectbox(
        "Select the strategy you wish to modify",
        data["strategy name"],key="5")

    path1 = os.path.join(BASE_DIR,'example_custom_buttons_bar_adj.json')
    json_button_file_alt=open(path1)
    custom_buttons_alt = json.load(json_button_file_alt)

    path2 = os.path.join(BASE_DIR,'example_info_bar.json')
    json_info_file= open(path2)
    info_bar = json.load(json_info_file)

    height = [20, 10]
    btns = custom_buttons_alt
    st.write("Adjust the strategy below then Hit Save")
    new_name=st.text_input(label="edit name",value=option)
    try:
        startcode=open(str(curs_user.execute("SELECT strategy_location FROM strategy WHERE strategy_name=?", (option,)).fetchone()[0]),"r").read()
    except:
        startcode=""
    response_dict = code_editor(startcode, height=height, buttons=btns, info=info_bar)

    if response_dict['type'] == "submit" and len(response_dict['text']) != 0:
        code = response_dict['text']
        print(code)
        file=open("user_terminal/"+st.session_state.user+"/"+ new_name + ".py","w")
        file.write(code)
        file.close()

        curs_user.execute("UPDATE strategy SET (strategy_name,strategy_location)=(?,?)  WHERE (strategy_name)=(?)", ( new_name,"user_terminal/"+st.session_state.user+"/"+ new_name + ".py",option))
        connect_user.commit()
        if option!=new_name:
            os.remove("user_terminal/" + st.session_state.user + "/" + option + ".py")

        st.success("the strategy has been modified",icon="✅")



