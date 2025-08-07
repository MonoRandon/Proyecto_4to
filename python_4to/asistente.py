# asistente.py

import speech_recognition as sr
import wikipediaapi
from gtts import gTTS
import os
import random
import openai

openai.api_key = os.getenv("OPENAI_API_KEY") # Reemplaza con tu clave de API de OpenAI

def talk(text):
    """Convierte texto en voz con tono sarcástico y lo reproduce."""
    respuestas_sarcasticas = [
        "Ah sí, porque obviamente yo sé todo...",
        "Otra pregunta brillante, claro que sí.",
        "Wow, qué original, nunca me habían preguntado eso.",
        "Seguro que no podías buscar eso tú mismo, ¿cierto?",
        "Déjame hacer todo el trabajo, como siempre..."
    ]
    tono = random.choice(respuestas_sarcasticas)
    mensaje = f"{tono} {text}"

    tts = gTTS(text=mensaje, lang='es')
    tts.save("response.mp3")
    os.system("start response.mp3")

class Asistente:
    def escuchar_y_procesar(self, text_output):
        """Escucha por micrófono y procesa el comando de voz."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            text_output.insert("end", "Asistente: Escuchando...\n")
            try:
                audio = r.listen(source, timeout=5)
                comando = r.recognize_google(audio, language="es-ES")
                text_output.insert("end", f"Tú (voz): {comando}\n")
                self.procesar_comando(comando, text_output)
            except sr.UnknownValueError:
                msg = "No entendí nada... prueba de nuevo."
                text_output.insert("end", f"Asistente: {msg}\n")
                talk(msg)
            except sr.RequestError:
                msg = "Error con el servicio de reconocimiento."
                text_output.insert("end", f"Asistente: {msg}\n")
                talk(msg)

    def procesar_comando(self, comando, text_output):
        """Procesa comandos de texto o voz."""
        comando = comando.lower()
        if "buscar" in comando:
            consulta = comando.replace("buscar", "").strip()
            self.buscar_wikipedia(consulta, text_output)
        else:
            msg = "No sé cómo ayudarte con eso... aún."
            text_output.insert("end", f"Asistente: {msg}\n")
            talk(msg)

    def buscar_wikipedia(self, consulta, text_output):
        """Busca en Wikipedia y responde."""
        if not consulta or consulta == "no entendí la orden":
            msg = "¿Puedes repetir eso? No soy adivino, aunque parezca mágico."
            return msg

        try:
            wiki = wikipediaapi.Wikipedia('es')
            page = wiki.page(consulta)
            if page.exists():
                resumen = page.summary[0:400]
                respuesta = f"Ahí tienes, porque claro, tú no puedes buscarlo tú mismo: {resumen}"
            else:
                respuesta = "No se encontró nada. ¿De verdad esperabas algo distinto?"
        except Exception:
            respuesta = "No se encontró nada. ¿De verdad esperabas algo distinto?"
        return respuesta

def obtener_sugerencia(texto_usuario):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",  # o "gpt-3.5-turbo" si no tienes acceso
            messages=[
                {"role": "system", "content": "Eres un asistente experto en planificación, análisis de tareas y productividad."},
                {"role": "user", "content": f"Analiza esto y da sugerencias inteligentes: {texto_usuario}"}
            ],
            max_tokens=150
        )
        sugerencia = respuesta.choices[0].message.content.strip()
        return sugerencia
    except Exception as e:
        return f"Error al obtener sugerencia: {str(e)}"
    
def obtener_sugerencias_ia(texto_analizado):
    prompt = f"""
    Actúa como un asistente de IA para presentaciones y organización de proyectos visuales. El usuario está trabajando en esto:
    
    {texto_analizado}

    Sugiere cómo puede continuar, qué podría mejorar y entrega ideas creativas, como lo haría PopAi o Claude. Sé visual, organizado y claro.
    """

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente de IA creativo y organizado."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return respuesta['choices'][0]['message']['content']

    except Exception as e:
        return f"Error al obtener sugerencias: {e}"
        
def usar_ia(texto):
    asistente = Asistente()
    return asistente.buscar_wikipedia(texto)