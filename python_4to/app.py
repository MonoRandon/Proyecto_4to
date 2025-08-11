import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import uuid
from drawing_helper import analizar_y_corregir
from asistente import generar_reporte_ia
import base64
import requests
import openai
from excel_generator import crear_excel
from gantt_generator import crear_gantt_excel
from ia_assistant import analizar_con_ia, sugerencia_desde_texto
from arduino_control import enviar_a_arduino
import mysql.connector
from db import guardar_en_db
from asistente import usar_ia, obtener_sugerencia, obtener_sugerencias_ia
from drawing_helper import analizar_plano

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HF_TOKEN = "hf_...Tvgn"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_excel', methods=['POST'])
def crear_excel_route():
    carpeta = request.form.get('carpeta', 'MisExcels')
    archivo = request.form.get('archivo', 'archivo.xlsx')
    mensaje = crear_excel(carpeta, archivo)
    return render_template('index.html', mensaje=mensaje)

@app.route('/crear_gantt', methods=['POST'])
def crear_gantt_route():
    carpeta = request.form.get('carpeta', 'MisExcels')
    archivo = request.form.get('archivo', 'gantt.xlsx')
    mensaje = crear_gantt_excel(carpeta, archivo)
    return render_template('index.html', mensaje=mensaje)

@app.route('/analizar_entrada', methods=['POST'])
def analizar_entrada():
    entrada = request.form['entrada_usuario']
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
        texto_analizado = analizar_plano("static/plano_usuario.png")
        sugerencias = obtener_sugerencias_ia(texto_analizado)
        return jsonify({"sugerencias": sugerencias})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analizar-plano', methods=['POST'])
def analizar_y_sugerir():
    if 'plano' not in request.files:
        return "No se subió ninguna imagen."
    archivo = request.files['plano']
    ruta = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(ruta)
    analisis = analizar_plano(ruta)
    sugerencias = obtener_sugerencias_ia(analisis)
    return render_template('resultado.html', analisis=analisis, sugerencias=sugerencias, imagen=ruta)

@app.route("/analizar", methods=["POST"])
def analizar():
    archivo = request.files["archivo"]
    ruta_original = os.path.join(UPLOAD_FOLDER, archivo.filename)
    archivo.save(ruta_original)
    analisis = analizar_con_ia(ruta_original)
    ruta_corregida = corregir_plano(ruta_original)
    return render_template(
        "index.html",
        analisis=analisis,
        imagen_original=ruta_original,
        imagen_corregida=ruta_corregida
    )

@app.route('/guardar_dibujo', methods=['POST'])
def guardar_dibujo():
    data = request.get_json()
    imagen_data = data['imagen'].split(',')[1]
    nombre_archivo = "dibujo.png"
    ruta = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    with open(ruta, "wb") as f:
        f.write(base64.b64decode(imagen_data))
    detalles = analizar_plano(ruta)
    return redirect(url_for('resultado', detalles=detalles))

@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

@app.route("/analyze_drawing", methods=["POST"])
def analyze_drawing():
    data = request.get_json()
    image_data = data["image"].split(",")[1]
    image_bytes = base64.b64decode(image_data)
    filename = os.path.join(UPLOAD_FOLDER, "drawing.png")
    with open(filename, "wb") as f:
        f.write(image_bytes)
    hf_model = "microsoft/trocr-base-handwritten"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    with open(filename, "rb") as img_file:
        hf_response = requests.post(
            f"https://api-inference.huggingface.co/models/{hf_model}",
            headers=headers,
            data=img_file
        )
    hf_result = hf_response.json()
    detected_text = hf_result[0]["generated_text"] if isinstance(hf_result, list) else str(hf_result)
    prompt = f"Analiza este plano: {detected_text}. Describe en detalle y da sugerencias de mejora."
    openai_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    suggestions = openai_response["choices"][0]["message"]["content"]
    corrected_image_path = None
    return jsonify({
        "text": suggestions,
        "corrected_image": corrected_image_path
    })

def corregir_plano(ruta_imagen):
    img = cv2.imread(ruta_imagen)
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 50, 150)
    lineas = cv2.HoughLinesP(bordes, 1, np.pi / 180, 100, minLineLength=50, maxLineGap=10)
    if lineas is not None:
        for linea in lineas:
            x1, y1, x2, y2 = linea[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    ruta_salida = os.path.join(UPLOAD_FOLDER, "plano_corregido.png")
    cv2.imwrite(ruta_salida, img)
    return ruta_salida

@app.route("/upload_image", methods=["POST"])
def upload_image():
    # recibe archivo subido tradicional
    if 'archivo' in request.files:
        f = request.files['archivo']
        pid = str(uuid.uuid4())[:8]
        orig_name = f"{pid}_orig.png"
        ruta = os.path.join(UPLOAD_FOLDER, orig_name)
        f.save(ruta)
        return redirect(url_for("ver_proyecto", pid=pid))
    return "No file", 400

@app.route("/save_drawing", methods=["POST"])
def save_drawing():
    data = request.get_json()
    imgdata = data["image"].split(",")[1]
    pid = data.get("pid") or str(uuid.uuid4())[:8]
    ruta = os.path.join(UPLOAD_FOLDER, f"{pid}_orig.png")
    with open(ruta, "wb") as fh:
        fh.write(base64.b64decode(imgdata))
    return jsonify({"pid": pid})

@app.route("/analyze/<pid>", methods=["GET"])
def analyze_pid(pid):
    orig = os.path.join(UPLOAD_FOLDER, f"{pid}_orig.png")
    if not os.path.exists(orig):
        return "Proyecto no encontrado", 404

    resumen = analizar_y_corregir(orig, salida_dir=UPLOAD_FOLDER, basename=pid)
    # resumen contiene texto_bruto y ruta_corregida
    texto_bruto = resumen.get("texto_bruto","")
    # Llamar a IA para enriquecer el reporte
    reporte = generar_reporte_ia(texto_bruto)
    # devolver datos para la UI
    corr_path = resumen.get("ruta_corregida")
    return jsonify({
        "pid": pid,
        "ruta_orig": f"/{orig.replace(os.sep,'/')}",
        "ruta_corr": f"/{corr_path.replace(os.sep,'/')}",
        "texto_bruto": texto_bruto,
        "reporte": reporte
    })

@app.route("/ver/<pid>")
def ver_proyecto(pid):
    orig = os.path.join(UPLOAD_FOLDER, f"{pid}_orig.png")
    corr = os.path.join(UPLOAD_FOLDER, f"{pid}_corr.png")
    exists = os.path.exists(orig)
    return render_template("index.html", pid=pid, exists=exists)

# Eliminar la ruta vacía /upload

if __name__ == '__main__':
    app.run(debug=True)
    