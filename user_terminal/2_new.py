import os.path
import sqlite3
import time

import streamlit_authenticator as stauth

import streamlit as st
import pandas as pd
import numpy as np
import random
from code_editor import code_editor
import json



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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

user_db_path = os.path.join(BASE_DIR,st.session_state.user +"/"+st.session_state.user + ".db")
connect_user = sqlite3.connect(user_db_path,check_same_thread=False)
curs_user = connect_user.cursor()

stock_db_path = os.path.join(BASE_DIR, "stock_prices.db")
conn_stock = sqlite3.connect(stock_db_path,check_same_thread=False)
curs_stock = conn_stock.cursor()

st.markdown(html_style_string, unsafe_allow_html=True)
if "bot_name" not in st.session_state:
    st.session_state.bot_name = None




st.title("Create a new trading strategy here")
st.session_state.bot_name = st.text_input("enter bot name here")
###

path1 = os.path.join(BASE_DIR, 'example_custom_buttons_bar_adj.json')
json_button_file_alt = open(path1)
custom_buttons_alt = json.load(json_button_file_alt)

path2 = os.path.join(BASE_DIR, 'example_info_bar.json')
json_info_file = open(path2)
info_bar = json.load(json_info_file)

height = [20, 22]
btns = custom_buttons_alt
st.write("Program your strategy below then Hit Save")



response_dict = code_editor("", height=height,   buttons=btns, info=info_bar)
if response_dict['type'] == "submit" and len(response_dict['text']) != 0 and len(st.session_state.bot_name) != 0:
    try:
        code=response_dict['text']
        print(code)
        file = open("user_terminal/" + st.session_state.user + "/" + st.session_state.bot_name + ".py", "w")
        file.write(code)
        curs_user.execute("INSERT INTO strategy(strategy_name, strategy_location,on_off) VALUES (?,?,?)", (
        st.session_state.bot_name, "user_terminal/" + st.session_state.user + "/" + st.session_state.bot_name + ".py",1))
        connect_user.commit()
        st.success("Strategy Saved",icon="✅")
    except sqlite3.Error as e:
            st.error("This strategy already exists")




elif  response_dict['type'] == "submit" and len(response_dict['text']) == 0:
    st.warning('Add your strategy before Hitting Save', icon="⚠️")
