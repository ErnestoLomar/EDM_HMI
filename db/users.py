import sqlite3
import os
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/HMI/db/"

URI = f"{direccion_db}/users.db"

users_table = '''CREATE TABLE users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL,
    user VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL,
    uid VARCHAR(20) NOT NULL
)'''

def create_users_table():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(users_table)
        con.close()
    except Exception as e:
        print("Error creando tabla de usuarios: " + str(e))
        print(traceback.format_exc())