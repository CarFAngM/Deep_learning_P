import os
import re

def eliminar_duplicados_similares(carpeta):
    archivos_vistos = {}

    for nombre_archivo in os.listdir(carpeta):
        if nombre_archivo.endswith('.mp3'):
            ruta_completa = os.path.join(carpeta, nombre_archivo)
            nombre_normalizado = re.sub(r"\s?\[.*\]", "", nombre_archivo)

            if nombre_normalizado in archivos_vistos:
                print(f"Eliminando archivo duplicado: {ruta_completa}")
                os.remove(ruta_completa)
            else:
                archivos_vistos[nombre_normalizado] = ruta_completa

carpeta = r"C:\Users\carlo\Downloads\Deep_learning_P\jamendo_tracks"
eliminar_duplicados_similares(carpeta)
