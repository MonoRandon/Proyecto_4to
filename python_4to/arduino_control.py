import serial
import time

PORT = "COM3"  # cámbialo por el correcto
BAUDRATE = 9600

def enviar_a_arduino(comando):
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        time.sleep(2)
        ser.write((comando + '\n').encode())
        respuesta = ser.readline().decode().strip()
        ser.close()
        return f"Comando enviado: {comando}. Arduino respondió: {respuesta}"
    except serial.SerialException as e:
        return f"No se pudo abrir el puerto {PORT}: {e}"
    except Exception as e:
        return f"Error al enviar a Arduino: {str(e)}"