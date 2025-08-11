#Generador de Excel
#05/05/2025

import os
import openpyxl
from tkinter import messagebox

def crear_excel(nombre_carpeta="MisExcels", nombre_archivo="archivo.xlsx"):
    """Crea una carpeta y un archivo Excel dentro."""
    try:
        # Crear carpeta si no existe
        if not os.path.exists(nombre_carpeta):
            os.makedirs(nombre_carpeta)

        ruta_completa = os.path.join(nombre_carpeta, nombre_archivo)

        # Crear archivo Excel
        wb = openpyxl.Workbook()
        hoja = wb.active
        hoja.title = "Datos"
        hoja["A1"] = "Nombre"
        hoja["B1"] = "Descripción"
        wb.save(ruta_completa)

        return f"Excel creado: {ruta_completa}"
    except Exception as e:
        return f"Error al crear Excel: {str(e)}"

