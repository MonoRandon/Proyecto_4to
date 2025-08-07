#para el mysql y funciones utiles
import mysql.connector

def conecta_db():
    return mysql.connector.connect(...)

def guardar_comando(imagen, sugerencias):
    db = conecta_db()
    ...
    cursor.execute("INSERT INTO logs ...", ...)
    db.commit()
