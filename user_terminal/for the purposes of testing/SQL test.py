import os

import pymysql
from google.cloud.sql.connector import Connector
import google.auth
from google.auth.transport.requests import Request
import sqlalchemy

# IAM database user parameter (IAM user's email before the "@" sign, mysql truncates usernames)
# ex. IAM user with email "demo-user@test.com" would have database username "demo-user"
IAM_USER = "blackelm"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="application_default_credentials.json"
# initialize connector
connector = Connector()

# getconn now using IAM user and requiring no password with IAM Auth enabled

# helper function to return SQLAlchemy connection pool
    # function used to generate database connection
def getconn():
    conn = connector.connect(
        "blackelm-428420:europe-west2:blackelmsimulated",
        "pymysql",
        user="dev",
        password="dev",
        db="blackelm"
    )
    return conn

# create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

connector=Connector()
db_conn=pool.connect()
print(db_conn.execute(sqlalchemy.text("SELECT * FROM Credentials")).fetchall())