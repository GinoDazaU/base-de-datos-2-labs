import os
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv("DBNAME")
dbuser = os.getenv("DBUSER")
dbpass = os.getenv("DBPASS")
dbhost = os.getenv("DBHOST")

print(dbname)
print(dbuser)
print(dbpass)
print(dbhost)