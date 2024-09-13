import multiprocessing
import os
import threading
import time
import sqlite3
import subprocess
from order_matching_algorithm import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred_db_path = os.path.join(BASE_DIR, "credentials.db")
connect_credentials = sqlite3.connect(cred_db_path,check_same_thread=False)
curs_credentials = connect_credentials.cursor()

new = open("user_terminal/compiler_location.txt")
compiler_location = new.readline()

def tuple_to_array(tuple):
    array = []
    for data in tuple:
        temp = []  # creates 2d array for all credentials
        for x in data:
            temp.append(x)
        array.append(temp)  # 3D array
    return array

def run_bot_script():
    while True:
        all_strat = []
        all_locations = []
        for user in [row[0] for row in curs_credentials.execute("SELECT username From Credentials").fetchall()]:
            try:
                user_db = os.path.join(BASE_DIR, user + "/" + user + ".db")
                conn_user = sqlite3.connect(user_db,check_same_thread=False)
                curs_user = conn_user.cursor()
                conn_user.execute('PRAGMA journal_mode=WAL;')

                all_strat.append(tuple_to_array(curs_user.execute("SELECT * FROM strategy WHERE on_off=1").fetchall()))
            except:
                pass
        for strat_per_user in all_strat:
            for individual_strat in strat_per_user:
                try:
                    if individual_strat[2] == 1:
                        all_locations.append(individual_strat[1])
                except:
                    pass
        for file_path in all_locations:
            file_path_2 = os.path.join(BASE_DIR, file_path[14:])

            subprocess.run([compiler_location, file_path_2])

        # Simulate staggered start
def start_bot_scripts():
    threading.Thread(target=run_bot_script, daemon=True).start()

def order_matching_runner():
    while True:
        #print("rechecking")
        process1 = multiprocessing.Process(target=recheck_all())
        process1.start()
        process2 = multiprocessing.Process(target=check_incomplete())
        process2.start()
        #time.sleep(1)

def start_order_matching():
    threading.Thread(target=order_matching_runner, daemon=True).start()

def recheck_incomplete():
    while True:
        print("rechecking")
        process1 = multiprocessing.Process(target=check_incomplete())
        process1.start()

def start_recheck_incomplete():
    threading.Thread(target=recheck_incomplete, daemon=True).start()


if __name__ == "__main__":
    # Path to the database file
    # Start the order matching algorithm
    start_bot_scripts()

    start_order_matching()

    #start_recheck_incomplete()
    # Start the bot scripts

    # Keep the main thread alive
    while True:
        time.sleep(0)
