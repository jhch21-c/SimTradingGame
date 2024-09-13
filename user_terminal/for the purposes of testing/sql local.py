from github import Github
import sqlite3

connect_credentials = sqlite3.connect( "credentials.db" )

curs_credentials = connect_credentials.cursor()

g=Github("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")
repo=g.get_repo("Blackelm-Systematic/SimulatedGame")
curs_credentials.execute("INSERT INTO  Credentials (Username,Password) VALUES (?,?)",
                         (username,password))
connect_credentials.commit()
with open("credentials.db","rb") as file:
    repo.update_file("credentials.db",".",file.read(),repo.get_contents("user_terminal/credentials.db").sha,"main")