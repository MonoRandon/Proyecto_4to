import mysql.connector

def conecta_db():
    return mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_password",
        database="nombre_de_tu_bd"
    )

def guardar_comando(imagen, sugerencias):
    db = conecta_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO logs (imagen, sugerencias) VALUES (%s, %s)",
            (imagen, sugerencias)
        )
        db.commit()
    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")
    finally:
        cursor.close()
        db.close()
def obtener_comandos():
    db = conecta_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, imagen, sugerencias, fecha FROM logs ORDER BY fecha DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener comandos de la base de datos: {e}")
        return []
    finally:
        cursor.close()
        db.close()