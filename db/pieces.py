import sqlite3
import os
import traceback

direccion_actual = os.getcwd().replace("\\", "/")
direccion_db = direccion_actual + "/HMI/db/"

URI = f"{direccion_db}/pieces.db"

pieces_table = '''CREATE TABLE pieces (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20) NOT NULL,
    material VARCHAR(20) NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    length INTEGER NOT NULL,
    time1 INTEGER NOT NULL,
    time2 INTEGER NOT NULL,
    time3 INTEGER NOT NULL,
    time4 INTEGER NOT NULL,
    time5 INTEGER NOT NULL,
    time6 INTEGER NOT NULL,
    id_client INTEGER NOT NULL
)'''

def create_pieces_table():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute(pieces_table)
        con.close()
    except Exception as e:
        print("Error creando tabla de piezas: " + str(e))
        print(traceback.format_exc())
        
def getAllPieces():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces")
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo todas las piezas: " + str(e))
        print(traceback.format_exc())
        return None
    
def getAllPiecesOrderBySize():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces ORDER BY width DESC")
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo todas las piezas ordenadas por tamaño: " + str(e))
        print(traceback.format_exc())
        return None
    
def getAllPiecesOrderByType():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces ORDER BY material")
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo todas las piezas ordenadas por tipo: " + str(e))
        print(traceback.format_exc())
        return None
    
def getAllPiecesOrderByTypeMaterial(material):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces WHERE material = ?", (material,))
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo todas las piezas ordenadas por tipo y material: " + str(e))
        print(traceback.format_exc())
        return None
    
def getPieceByName(name):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces WHERE name = ?", (name,))
        piece = cur.fetchone()
        con.close()
        return piece
    except Exception as e:
        print("Error obteniendo pieza por nombre: " + str(e))
        print(traceback.format_exc())
        return None
    
def getPieceByClient(id_client):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces WHERE id_client = ?", (id_client,))
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo piezas por cliente: " + str(e))
        print(traceback.format_exc())
        return None

def getPieceByAlphabeticalOrder():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT * FROM pieces ORDER BY name")
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo piezas por orden alfabetico: " + str(e))
        print(traceback.format_exc())
        return None

def getPieceByDistincMaterial():
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()
        cur.execute("SELECT DISTINCT material FROM pieces")
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo piezas por material: " + str(e))
        print(traceback.format_exc())
        return None
    
def getPiecesWithClassificationSize(size):
    try:
        con = sqlite3.connect(URI)
        cur = con.cursor()

        query = """
            SELECT *,
                width * height * length AS volumen,
                CASE
                    WHEN width * height * length < 20 THEN 'Chico'
                    WHEN width * height * length >= 20 AND width * height * length < 50 THEN 'Mediano'
                    WHEN width * height * length >= 50 THEN 'Grande'
                    ELSE 'Otro'
                END AS clasificacion
            FROM pieces
            WHERE
                CASE
                    WHEN ? = 'Chico' AND width * height * length < 20 THEN 1
                    WHEN ? = 'Mediano' AND width * height * length >= 20 AND width * height * length < 50 THEN 1
                    WHEN ? = 'Grande' AND width * height * length >= 50 THEN 1
                    WHEN ? = 'Otro' THEN 1
                    ELSE 0
                END = 1;
        """

        cur.execute(query, (size, size, size, size))
        pieces = cur.fetchall()
        con.close()
        return pieces
    except Exception as e:
        print("Error obteniendo piezas por tamaño: " + str(e))
        print(traceback.format_exc())
        return None