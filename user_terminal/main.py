import sqlite3
import os.path
from github import Github
import glob
import shutil

import streamlit as st
st.set_page_config(layout='wide')
import os.path
import time
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_db_path = os.path.join(BASE_DIR, "credentials.db")
connect_credentials = sqlite3.connect(cred_db_path,check_same_thread=False)

curs_credentials = connect_credentials.cursor()

if "user" not in st.session_state:
    st.session_state.user = None
#SQL

def add_credentials(username,password):
    curs_credentials.execute("INSERT INTO  Credentials (Username,Password) VALUES (?,?)",
                             (username, password))
    connect_credentials.commit()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    old_user_db_path = os.path.join(BASE_DIR,username + ".db")

    connect_user = sqlite3.connect(old_user_db_path,check_same_thread=False)
    curs_user = connect_user.cursor()

    curs_user.execute(
         "CREATE TABLE portfolio (stock	TEXT NOT NULL UNIQUE,quantity	REAL NOT NULL,initial_price_per_share	REAL NOT NULL,long_or_short	TEXT NOT NULL,PRIMARY KEY(stock))")
    curs_user.execute(
         "CREATE TABLE strategy (strategy_name TEXT NOT NULL UNIQUE, strategy_location BLOB NOT NULL,on_off	INTEGER NOT NULL, PRIMARY KEY(strategy_name))")
    curs_user.execute("INSERT INTO  portfolio (stock,quantity,initial_price_per_share,long_or_short) VALUES (?,?,?,?)",("cash",1000,1,"long"))
    connect_user.commit()
    connect_user.close()
    folder_path = os.path.join(BASE_DIR,username )
    os.mkdir(folder_path)
    shutil.move(old_user_db_path, folder_path)
    shutil.copy("user_terminal/order_placement.py", folder_path)
    shutil.copy("user_terminal/read_stock_price.py", folder_path)

    st.success("you have registered",icon="✅")
# used to store all the usernames and passwords as a 2d array
credentials = []
def retrieve_credentials():
    for data in  curs_credentials.execute("SELECT * from Credentials").fetchall():
        temp = []  # creates 2d array for all credentials
        for x in data:
            temp.append( x )
        credentials.append( temp )  #3D array

def checker(username,password):
    retrieve_credentials()
    temp=[str(username),str(password)]
    ##add some more errors ie no input and try registering
    if temp in credentials:
        st.session_state.user = username
        st.rerun()
    else:
        st.warning("Invalid Credentials")
def login():

    st.header("Log in")
    username = st.text_input("enter username")
    password = st.text_input("enter password")
    col1, col2 = st.columns([1, 1])  # Adjust column ratios as needed
    with col1:
        if st.button("Log in",use_container_width=True):
            checker(username, password)

    with col2:
        if st.button("Register", use_container_width=True):
            retrieve_credentials()
            if username in [row[0] for row in credentials]:
                st.warning("this username already exist, try a different one")
                return
            if username == "" or password == "":
                st.warning("one or more of the fields are blank, please add some text")
            else:
                add_credentials(username,password)
                st.rerun()

        ##add a login checking system here

def logout():
    st.session_state.user = None
    st.rerun()

def main():
    logout_page = st.Page(logout, title="Log out")
    request_1 = st.Page(
        "1_overview.py",
        title="Overview",
        default=True,

    )
    request_2 = st.Page(
        "2_new.py", title="New"
    )
    admin = st.Page(
        "admin.py", title="Admin",

    )
    st.title("Blackelm")
    if st.session_state.user=="admin" :
        pg = st.navigation( {"Account": [logout_page]} |{"Admin": [admin]}| {"Tools": [request_1, request_2]})
        pg.run()
    else:
        if (st.session_state.user != None) and (st.session_state.user != "admin"):
            pg = st.navigation({"Account": [logout_page]} | {"Tools": [request_1, request_2]})
            pg.run()
        else:
            pg = st.navigation([st.Page(login)])
            pg.run()
    while True:
        time.sleep(60)
        st.rerun()
if __name__=="__main__":
    main()
#