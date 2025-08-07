# avatar.py
from tkinter import Canvas
from PIL import Image, ImageTk
import os

class Avatar:
    def __init__(self, parent):
        self.canvas = Canvas(parent, width=120, height=120, bg="#DDE6ED", highlightthickness=0)

        # Obtener ruta absoluta del archivo de imagen
        ruta_imagen = os.path.join(os.path.dirname(__file__), "assets", "avatar_image.png")

        self.imagen_avatar = Image.open(ruta_imagen)
        self.imagen_avatar = self.imagen_avatar.resize((100, 100))
        self.avatar_tk = ImageTk.PhotoImage(self.imagen_avatar)

    def mostrar(self):
        self.canvas.create_image(60, 60, image=self.avatar_tk)

