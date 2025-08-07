#lateral_del_panel
#05/05/2025

import tkinter as tk

class LateralPanel:
    def __init__(self, parent, canvas, text_output):
        self.frame = tk.Frame(parent, width=200, bg="#DDE6ED")
        self.frame.pack(side="left", fill="y")

        tk.Label(self.frame, text="🛠 Herramientas", bg="#DDE6ED", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Button(self.frame, text="📁 Crear Excel", command=lambda: crear_excel(text_output)).pack(pady=5, fill="x", padx=10)
        tk.Button(self.frame, text="📊 Generar Gantt", command=lambda: generar_gantt(canvas, text_output)).pack(pady=5, fill="x", padx=10)

    def ocultar(self):
        self.frame.pack_forget()

    def mostrar(self):
        self.frame.pack(side="left", fill="y")
