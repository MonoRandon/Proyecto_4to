import mysql.connector

def guardar_en_db(usuario, mensaje):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="TU_USUARIO_MYSQL",
            password="TU_PASSWORD_MYSQL",
            database="nombre_de_tu_bd"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (usuario, mensaje) VALUES (%s, %s)", (usuario, mensaje))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al guardar en base de datos:", e)
