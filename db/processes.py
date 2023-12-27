import sqlite3
import os
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/HMI/db/"

URI = f"{direccion_db}/processes.db"

process_table = '''CREATE TABLE processes (
    id_process INTEGER PRIMARY KEY AUTOINCREMENT,
    id_piece VARCHAR(10) NOT NULL,
    amount VARCHAR(5) NOT NULL,
    route VARCHAR(10) NOT NULL,
    date VARCHAR(20) NOT NULL,
    time VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    id_user VARCHAR(10) NOT NULL,
    folio_process INTEGER NOT NULL,
    check_servidor VARCHAR(10) default 'NO'
)'''

def create_processes_table():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(process_table)
        con.close()
    except Exception as e:
        print("Error creando tabla de procesos: " + str(e))
        print(traceback.format_exc())
        
def getProcessesInNO():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM processes WHERE check_servidor = 'NO'")
        processes = cur.fetchall()
        con.close()
        return processes
    except Exception as e:
        print("Error obteniendo todos los procesos en NO: " + str(e))
        print(traceback.format_exc())
        return None
    
def modifyCheckServidor(id_process):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(f"UPDATE processes SET check_servidor = 'OK' WHERE id_process = '{id_process}'")
        con.commit()
        con.close()
        return True
    except Exception as e:
        print("Error modificando el check_servidor: " + str(e))
        print(traceback.format_exc())
        return False
    
def insertProcess(id_piece, amount, route, date, time, status, id_user, folio_process):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(f"INSERT INTO processes (id_piece, amount, route, date, time, status, id_user, folio_process) VALUES ('{id_piece}', '{amount}', '{route}', '{date}', '{time}', '{status}', '{id_user}', '{folio_process}')")
        con.commit()
        con.close()
        return True
    except Exception as e:
        print("Error insertando proceso: " + str(e))
        print(traceback.format_exc())
        return False

#############################################################
#############################################################
#############################################################

process_history_table = '''CREATE TABLE process_history (
    id_process_history INTEGER PRIMARY KEY AUTOINCREMENT,
    id_piece VARCHAR(10) NOT NULL,
    amount VARCHAR(5) NOT NULL,
    date VARCHAR(20) NOT NULL,
    time VARCHAR(10) NOT NULL,
    id_user VARCHAR(10) NOT NULL
)'''

    
def create_process_history_table():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(process_history_table)
        con.close()
    except Exception as e:
        print("Error creando tabla de historial de procesos: " + str(e))
        print(traceback.format_exc())
        
def insertProcessHistory(id_piece, amount, date, time, id_user):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(f"INSERT INTO process_history (id_piece, amount, date, time, id_user) VALUES ('{id_piece}', '{amount}', '{date}', '{time}', '{id_user}')")
        con.commit()
        con.close()
        return True
    except Exception as e:
        print("Error insertando proceso historial: " + str(e))
        print(traceback.format_exc())
        return False
    
def getLastProcessHistory():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM process_history ORDER BY id_process_history DESC LIMIT 1")
        process = cur.fetchone()
        con.close()
        return process
    except Exception as e:
        print("Error obteniendo el ultimo proceso historial: " + str(e))
        print(traceback.format_exc())
        return None