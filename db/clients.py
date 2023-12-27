import sqlite3
import os
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/HMI/db/"

URI = f"{direccion_db}/clients.db"

clients_table = '''CREATE TABLE clients (
    id_client INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL,
    business_name VARCHAR(20) NOT NULL
)'''

def create_clients_table():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(clients_table)
        con.close()
    except Exception as e:
        print("Error creando tabla de clientes: " + str(e))
        print(traceback.format_exc())
        
def getAllClients():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM clients")
        clients = cur.fetchall()
        con.close()
        return clients
    except Exception as e:
        print("Error obteniendo clientes: " + str(e))
        print(traceback.format_exc())
        
def getClientByName(name):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM clients WHERE name = ?", (name,))
        client = cur.fetchone()
        con.close()
        return client
    except Exception as e:
        print("Error obteniendo cliente por nombre: " + str(e))
        print(traceback.format_exc())