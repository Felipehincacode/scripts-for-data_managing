# -*- coding: utf-8 -*-

"""
Módulo Core de Flowbooster.

Este archivo contiene toda la lógica de procesamiento de archivos,
dejando la interfaz de usuario completamente separada. Aquí se maneja
el análisis de carpetas, la creación de estructuras, el movimiento/copia
de archivos y la generación de reportes.
"""
import os
import shutil
import sys
import subprocess
import json
from datetime import datetime

# --- Constantes ---
# Listas de extensiones para clasificar los archivos.
IMG_JPG_EXT = ['.jpg', '.jpeg', '.png']
IMG_RAW_EXT = ['.cr2', '.nef', '.arw', '.raw']
VIDEO_EXT = ['.mp4', '.mov', '.avi', '.mkv']

# Diccionario con el contenido para los archivos README.md.
# Usar un diccionario facilita el mantenimiento y futuras traducciones.
README_CONTENT = {
    "jpg": "### 🖼️ Imágenes JPG\n\nEn esta carpeta se guardan las imágenes en formato estándar (JPG, PNG).",
    "raw": "### 📸 Imágenes RAW\n\nEn esta carpeta se guardan las imágenes en formato RAW, directas de la cámara.",
    "videos": "### 🎬 Videos\n\nEn esta carpeta se guardan todos los archivos de video."
}

# --- Funciones de Análisis y Estructura ---

def analizar_origen(origen):
    """
    Analiza la carpeta de origen para detectar tipos y cantidad de archivos.
    
    Recorre todos los elementos de la carpeta origen, los clasifica por extensión
    y devuelve un diccionario con el recuento y las listas de archivos.
    
    Args:
        origen (str): La ruta a la carpeta de origen.
        
    Returns:
        dict: Un diccionario con el análisis ('tipo_proyecto', 'counts', 'files').
    """
    analisis = {
        "tipo_proyecto": "vacio",
        "counts": {"JPG": 0, "RAW": 0, "VIDEO": 0},
        "files": {"JPG": [], "RAW": [], "VIDEO": []}
    }
    
    for archivo in os.listdir(origen):
        ruta_completa = os.path.join(origen, archivo)
        if not os.path.isfile(ruta_completa):
            continue  # Ignora subcarpetas, solo procesa archivos
        
        ext = os.path.splitext(archivo)[1].lower()
        if ext in IMG_JPG_EXT:
            analisis["counts"]["JPG"] += 1
            analisis["files"]["JPG"].append(archivo)
        elif ext in IMG_RAW_EXT:
            analisis["counts"]["RAW"] += 1
            analisis["files"]["RAW"].append(archivo)
        elif ext in VIDEO_EXT:
            analisis["counts"]["VIDEO"] += 1
            analisis["files"]["VIDEO"].append(archivo)

    # Determina el tipo de proyecto basado en los archivos encontrados
    has_images = analisis["counts"]["JPG"] > 0 or analisis["counts"]["RAW"] > 0
    has_videos = analisis["counts"]["VIDEO"] > 0

    if has_images and has_videos:
        analisis["tipo_proyecto"] = "Mixto"
    elif has_images:
        analisis["tipo_proyecto"] = "Fotografía"
    elif has_videos:
        analisis["tipo_proyecto"] = "Video"
        
    return analisis

def crear_estructura(destino, analisis, crear_todas):
    """
    Crea la estructura de carpetas en el destino.
    
    Puede crear todas las carpetas posibles o solo las necesarias
    basado en los archivos encontrados y la opción del usuario.
    
    Args:
        destino (str): Ruta a la carpeta de destino principal.
        analisis (dict): El diccionario resultado de analizar_origen().
        crear_todas (bool): Si es True, crea todas las carpetas sin importar el contenido.
        
    Returns:
        tuple: Una tupla conteniendo (lista de rutas creadas, diccionario de rutas posibles).
    """
    rutas_a_crear = []
    rutas_creadas = []
    
    rutas_posibles = {
        "jpg": os.path.join(destino, "img", "jpg"),
        "raw": os.path.join(destino, "img", "raw"),
        "videos": os.path.join(destino, "videos")
    }

    if crear_todas:
        rutas_a_crear.extend(rutas_posibles.values())
    else: # Crea carpetas solo si hay archivos de ese tipo
        if analisis["counts"]["JPG"] > 0: rutas_a_crear.append(rutas_posibles["jpg"])
        if analisis["counts"]["RAW"] > 0: rutas_a_crear.append(rutas_posibles["raw"])
        if analisis["counts"]["VIDEO"] > 0: rutas_a_crear.append(rutas_posibles["videos"])

    for ruta in rutas_a_crear:
        os.makedirs(ruta, exist_ok=True) # exist_ok=True evita errores si la carpeta ya existe
        rutas_creadas.append(ruta)
        
    return rutas_creadas, rutas_posibles

# --- Funciones de Generación de Archivos ---

def generar_readme(rutas_posibles):
    """
    Genera un archivo README.md en cada carpeta de rutas_posibles.
    Args:
        rutas_posibles (dict): Diccionario que mapea tipo a ruta.
    """
    for key, ruta in rutas_posibles.items():
        if key in README_CONTENT:
            os.makedirs(ruta, exist_ok=True)  # Asegura que la carpeta exista
            with open(os.path.join(ruta, "README.md"), "w", encoding="utf-8") as f:
                f.write(README_CONTENT[key])

def generar_log(destino, log):
    """
    Genera un archivo log.md con el registro de archivos movidos/copiados.
    
    Args:
        destino (str): Ruta a la carpeta de destino.
        log (list): Una lista de strings, donde cada string es una línea del log.
    """
    ruta = os.path.join(destino, "log.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"# Registro de organización\n\n")
        f.write(f"📦 Proyecto organizado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Archivos procesados:\n")
        for linea in log:
            f.write(f"{linea}\n")

def generar_json_info(destino, origen, analisis):
    """
    Genera un archivo proyecto_info.json con metadatos del proyecto.
    
    Args:
        destino (str): Ruta a la carpeta de destino.
        origen (str): Ruta a la carpeta de origen.
        analisis (dict): El diccionario resultado de analizar_origen().
    """
    info = {
        "tipo_proyecto": analisis["tipo_proyecto"],
        "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "rutas": {
            "origen": origen,
            "destino": destino
        },
        "cantidad_archivos": analisis["counts"]
    }
    ruta = os.path.join(destino, "proyecto_info.json")
    with open(ruta, "w", encoding="utf-8") as f:
        # Escribe el JSON con indentación para que sea legible por humanos
        json.dump(info, f, indent=4, ensure_ascii=False)

# --- Función Principal de Procesamiento ---

def procesar_proyecto(origen, destino, copiar=False, crear_todas=False, incluir_readme=False):
    """
    Función principal que orquesta todo el proceso de organización.
    
    Args:
        origen (str): Ruta de la carpeta origen.
        destino (str): Ruta de la carpeta destino.
        copiar (bool): Si es True, copia los archivos. Si es False, los mueve.
        crear_todas (bool): Si es True, crea toda la estructura de carpetas.
        incluir_readme (bool): Si es True, genera los archivos README.md.
        
    Returns:
        tuple: (log, tipo_proyecto) o (None, "vacio") si no hay archivos.
    """
    # 1. Analizar el contenido
    analisis = analizar_origen(origen)
    if analisis["tipo_proyecto"] == "vacio":
        return None, "vacio"

    # 2. Crear la estructura de carpetas
    carpetas_creadas, rutas_posibles = crear_estructura(destino, analisis, crear_todas)
    
    # 3. Generar README.md en todas las carpetas posibles si se solicita
    if incluir_readme:
        generar_readme(rutas_posibles)

    log = []
    accion_str = "Copiado" if copiar else "Movido"
    
    # 4. Mover o copiar los archivos a sus nuevas carpetas
    for tipo, archivos in analisis["files"].items():
        if not archivos: continue # Si no hay archivos de este tipo, saltar
            
        # Determinar la ruta de destino según el tipo
        if tipo == "JPG":
            ruta_destino_tipo = rutas_posibles["jpg"]
        elif tipo == "RAW":
            ruta_destino_tipo = rutas_posibles["raw"]
        elif tipo == "VIDEO":
            ruta_destino_tipo = rutas_posibles["videos"]

        for archivo in archivos:
            ruta_origen_archivo = os.path.join(origen, archivo)
            nueva_ruta_archivo = os.path.join(ruta_destino_tipo, archivo)
            
            # Ejecutar la acción
            if copiar:
                shutil.copy2(ruta_origen_archivo, nueva_ruta_archivo)
            else:
                shutil.move(ruta_origen_archivo, nueva_ruta_archivo)
            
            # Registrar en el log
            log.append(f"- `{archivo}` → **{tipo}** ({accion_str})")

    # 5. Generar los archivos de reporte
    generar_log(destino, log)
    generar_json_info(destino, origen, analisis)
    
    return log, analisis["tipo_proyecto"]

# --- Función Auxiliar del Sistema ---

def abrir_carpeta(ruta):
    """
    Abre una carpeta en el explorador de archivos del sistema operativo.
    Es compatible con Windows, macOS y Linux.
    
    Args:
        ruta (str): La ruta a la carpeta que se desea abrir.
    """
    try:
        if sys.platform == "win32":
            os.startfile(os.path.realpath(ruta))
        elif sys.platform == "darwin": # macOS
            subprocess.Popen(["open", ruta])
        else: # linux (xdg-open es el estándar)
            subprocess.Popen(["xdg-open", ruta])
    except Exception as e:
        print(f"Error al intentar abrir la carpeta {ruta}: {e}")
