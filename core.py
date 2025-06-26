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
from PIL import Image
import exifread

# --- Constantes ---
# Listas de extensiones para clasificar los archivos.
IMG_JPG_EXT = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
IMG_RAW_EXT = ['.cr2', '.nef', '.arw', '.raw', '.dng', '.orf', '.rw2', '.pef', '.srw']
VIDEO_EXT = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp']

# Diccionario con el contenido para los archivos README.md.
# Usar un diccionario facilita el mantenimiento y futuras traducciones.
README_CONTENT = {
    "jpg": "### 🖼️ Imágenes JPG\n\nEn esta carpeta se guardan las imágenes en formato estándar (JPG, PNG).",
    "raw": "### 📸 Imágenes RAW\n\nEn esta carpeta se guardan las imágenes en formato RAW, directas de la cámara.",
    "videos": "### 🎬 Videos\n\nEn esta carpeta se guardan todos los archivos de video.",
    "fecha": "### 📅 Archivos por Fecha\n\nEn esta carpeta se guardan los archivos organizados por fecha de creación."
}

# --- Funciones de Análisis y Estructura ---

def obtener_fecha_archivo(ruta_archivo):
    """
    Obtiene la fecha de creación del archivo, intentando extraer EXIF primero.
    
    Args:
        ruta_archivo (str): Ruta completa al archivo.
        
    Returns:
        datetime: Fecha del archivo o fecha de modificación del sistema.
    """
    try:
        # Intentar extraer fecha EXIF de imágenes
        ext = os.path.splitext(ruta_archivo)[1].lower()
        if ext in IMG_JPG_EXT + IMG_RAW_EXT:
            with open(ruta_archivo, 'rb') as f:
                tags = exifread.process_file(f, stop_tag='EXIF DateTimeOriginal')
                if 'EXIF DateTimeOriginal' in tags:
                    fecha_str = str(tags['EXIF DateTimeOriginal'])
                    return datetime.strptime(fecha_str, '%Y:%m:%d %H:%M:%S')
    except:
        pass
    
    # Si no se puede extraer EXIF, usar fecha de modificación del archivo
    return datetime.fromtimestamp(os.path.getmtime(ruta_archivo))

def analizar_origen_por_fecha(origen):
    """
    Analiza la carpeta de origen para detectar archivos y sus fechas.
    
    Args:
        origen (str): La ruta a la carpeta de origen.
        
    Returns:
        dict: Un diccionario con el análisis de archivos por fecha.
    """
    archivos_por_fecha = {}
    total_archivos = 0
    
    for archivo in os.listdir(origen):
        ruta_completa = os.path.join(origen, archivo)
        if not os.path.isfile(ruta_completa):
            continue
        
        ext = os.path.splitext(archivo)[1].lower()
        if ext in IMG_JPG_EXT + IMG_RAW_EXT + VIDEO_EXT:
            try:
                fecha = obtener_fecha_archivo(ruta_completa)
                archivos_por_fecha[archivo] = fecha
                total_archivos += 1
            except:
                continue
    
    return archivos_por_fecha, total_archivos

def crear_estructura_por_fecha(destino, archivos_por_fecha, nivel_organizacion):
    """
    Crea la estructura de carpetas organizadas por fecha.
    
    Args:
        destino (str): Ruta a la carpeta de destino principal.
        archivos_por_fecha (dict): Diccionario con archivos y sus fechas.
        nivel_organizacion (str): Nivel de organización ('dia', 'semana', 'mes', 'año').
        
    Returns:
        dict: Diccionario con las rutas creadas y archivos asignados.
    """
    estructura = {}
    
    for archivo, fecha in archivos_por_fecha.items():
        if nivel_organizacion == 'año':
            carpeta = fecha.strftime('%Y')
        elif nivel_organizacion == 'mes':
            carpeta = fecha.strftime('%Y-%m')
        elif nivel_organizacion == 'semana':
            # Obtener el número de semana del año
            semana = fecha.isocalendar()[1]
            carpeta = fecha.strftime(f'%Y-W{semana:02d}')
        else:  # día
            carpeta = fecha.strftime('%Y-%m-%d')
        
        ruta_carpeta = os.path.join(destino, carpeta)
        os.makedirs(ruta_carpeta, exist_ok=True)
        
        if ruta_carpeta not in estructura:
            estructura[ruta_carpeta] = []
        estructura[ruta_carpeta].append(archivo)
    
    return estructura

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

def procesar_proyecto_por_fecha(origen, destino, nivel_organizacion, copiar=False, incluir_readme=False):
    """
    Función principal para organizar archivos por fecha.
    
    Args:
        origen (str): Ruta de la carpeta origen.
        destino (str): Ruta de la carpeta destino.
        nivel_organizacion (str): Nivel de organización ('dia', 'semana', 'mes', 'año').
        copiar (bool): Si es True, copia los archivos. Si es False, los mueve.
        incluir_readme (bool): Si es True, genera los archivos README.md.
        
    Returns:
        tuple: (log, total_archivos) o (None, 0) si no hay archivos.
    """
    # 1. Analizar el contenido por fecha
    archivos_por_fecha, total_archivos = analizar_origen_por_fecha(origen)
    if total_archivos == 0:
        return None, 0

    # 2. Crear la estructura de carpetas por fecha
    estructura = crear_estructura_por_fecha(destino, archivos_por_fecha, nivel_organizacion)
    
    # 3. Generar README.md si se solicita
    if incluir_readme:
        for ruta_carpeta in estructura.keys():
            readme_path = os.path.join(ruta_carpeta, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(README_CONTENT["fecha"])

    log = []
    accion_str = "Copiado" if copiar else "Movido"
    
    # 4. Mover o copiar los archivos a sus carpetas por fecha
    for ruta_carpeta, archivos in estructura.items():
        for archivo in archivos:
            ruta_origen_archivo = os.path.join(origen, archivo)
            nueva_ruta_archivo = os.path.join(ruta_carpeta, archivo)
            
            # Ejecutar la acción
            if copiar:
                shutil.copy2(ruta_origen_archivo, nueva_ruta_archivo)
            else:
                shutil.move(ruta_origen_archivo, nueva_ruta_archivo)
            
            # Registrar en el log
            fecha_archivo = archivos_por_fecha[archivo]
            log.append(f"- `{archivo}` → **{os.path.basename(ruta_carpeta)}** ({accion_str}) - {fecha_archivo.strftime('%Y-%m-%d %H:%M')}")

    # 5. Generar los archivos de reporte
    generar_log(destino, log)
    
    # Crear info específica para organización por fecha
    info = {
        "tipo_proyecto": f"Organización por Fecha ({nivel_organizacion})",
        "fecha_creacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "rutas": {
            "origen": origen,
            "destino": destino
        },
        "nivel_organizacion": nivel_organizacion,
        "total_archivos": total_archivos,
        "carpetas_creadas": len(estructura)
    }
    ruta = os.path.join(destino, "proyecto_info.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
    
    return log, total_archivos

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
