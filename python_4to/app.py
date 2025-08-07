from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask import request, jsonify
import os
from excel_generator import crear_excel
from gantt_generator import crear_gantt_excel
from ia_assistant import analizar_con_ia
from ia_assistant import sugerencia_desde_texto
from arduino_control import enviar_a_arduino  # comunicación serial con Arduino
import mysql.connector
from db import guardar_en_db
from asistente import usar_ia
from asistente import obtener_sugerencia
from asistente import obtener_sugerencias_ia
from drawing_helper import analizar_plano # análisis de planos


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # carga la página principal

@app.route('/crear_excel', methods=['POST'])
def crear_excel_route():
    carpeta = request.form.get('carpeta', 'MisExcels')  # recibe el nombre
    archivo = request.form.get('archivo', 'archivo.xlsx')  # recibe el archivo
    mensaje = crear_excel(carpeta, archivo)  # llama la función para crearlo
    return render_template('index.html', mensaje=mensaje)  # muestra resultado

@app.route('/crear_gantt', methods=['POST'])
def crear_gantt_route():
    carpeta = request.form.get('carpeta', 'MisExcels')
    archivo = request.form.get('archivo', 'gantt.xlsx')
    mensaje = crear_gantt_excel(carpeta, archivo)
    return render_template('index.html', mensaje=mensaje)

# Nueva ruta para analizar con IA
@app.route('/analizar_entrada', methods=['POST'])
def analizar_entrada():
    entrada = request.form['entrada_usuario']
    
    # Usa la IA avanzada
    respuesta = analizar_con_ia(entrada)
    
    return render_template('index.html', respuesta_ia=respuesta)

@app.route('/enviar_comando', methods=['POST'])
def enviar_comando():
    comando_usuario = request.form['comando']
    comando_ia = sugerencia_desde_texto(comando_usuario)
    resultado = enviar_a_arduino(comando_ia)
    guardar_en_db("usuario_tu_nombre", comando_ia)
    return redirect(url_for('index', resultado=f"{comando_ia} → {resultado}"))

def guardar_en_db(usuario, mensaje):
    conn = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_password",
        database="nombre_de_tu_bd"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (usuario, mensaje) VALUES (%s, %s)", (usuario, mensaje))
    conn.commit()
    cursor.close()
    conn.close()
    
@app.route('/enviar_arduino', methods=['POST'])
def arduino_route():
    comando = request.form.get('comando')
    mensaje = enviar_a_arduino(comando)
    return render_template('index.html', mensaje=mensaje)

@app.route('/usar_ia', methods=['POST'])
def usar_ia_route():
    comando_ia = request.form.get('comando_ia')
    respuesta = usar_ia(comando_ia)
    return render_template('index.html', mensaje=respuesta)


@app.route('/sugerencia', methods=['POST'])
def sugerencia():
    texto = request.form.get('contenido', '')
    if texto:
        sugerencia = obtener_sugerencia(texto)
        return render_template('index.html', sugerencia=sugerencia)
    return render_template('index.html', sugerencia="No se envió texto.")


@app.route("/completar_orden", methods=["POST"])
def completar_orden():
    try:
        # Analizar el plano cargado (ej. imagen)
        texto_analizado = analizar_plano("static/plano_usuario.png")  # o el nombre correcto

        # Enviar texto a la IA para obtener sugerencias
        sugerencias = obtener_sugerencias_ia(texto_analizado)

        return jsonify({"sugerencias": sugerencias})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/analizar-plano', methods=['POST'])
def analizar_y_sugerir():
    if 'plano' not in request.files:
        return "No se subió ninguna imagen."

    archivo = request.files['plano']
    ruta = os.path.join('static/uploads', archivo.filename)
    archivo.save(ruta)

    # Analizar el plano con OpenCV
    analisis = analizar_plano(ruta)

    # Obtener sugerencias desde la IA
    sugerencias = obtener_sugerencias_ia(analisis)

    return render_template('resultado.html', analisis=analisis, sugerencias=sugerencias, imagen=ruta)

    
if __name__ == '__main__':
    app.run(debug=True)
