

# ia_assistant.py
import openai

# Pega aquí tu clave real
openai.api_key = "TU_API_KEY_AQUI"

def analizar_con_ia(texto_usuario):
    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # O usa "gpt-4" si tienes acceso
            messages=[
                {"role": "system", "content": "Eres una IA que ayuda a mejorar presentaciones, organizar ideas, generar listas, y dar consejos útiles de diseño como Claude, PopAI o NapkinIA."},
                {"role": "user", "content": texto_usuario}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return respuesta['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al conectar con IA: {str(e)}"

def sugerencia_desde_texto(texto):
    texto = texto.lower()
    if "encender" in texto:
        return "ON"
    elif "apagar" in texto:
        return "OFF"
    elif "rojo" in texto:
        return "COLOR:RED"
    elif "verde" in texto:
        return "COLOR:GREEN"
    else:
        return "COMANDO DESCONOCIDO"

def usar_ia(prompt):
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content