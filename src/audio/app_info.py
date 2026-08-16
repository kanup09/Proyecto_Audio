import os

from audio.routing import obtener_filas_svcl


def obtener_nombres_amigables(filas=None):
    """Devuelve un diccionario {nombre_proceso_en_minuscula: nombre_amigable}.
    Si no le pasás 'filas', las pide él mismo (llamando a svcl.exe);
    pero para no duplicar la llamada, main_window.py le pasa las filas
    que ya pidió para la lista de dispositivos."""
    if filas is None:
        filas = obtener_filas_svcl()

    nombres = {}
    for fila in filas:
        if fila.get("Type") == "Application":
            ruta_proceso = fila.get("Process Path", "")
            if ruta_proceso:
                nombre_proceso = os.path.basename(ruta_proceso).lower()
                nombres[nombre_proceso] = fila.get("Name", "").strip()
    return nombres


def nombre_para_mostrar(nombre_proceso, nombres_amigables):
    """Devuelve el nombre amigable si existe; si no, arma uno razonable
    a partir del nombre del proceso (ej: 'wallpaper32.exe' -> 'Wallpaper32')."""
    amigable = nombres_amigables.get(nombre_proceso.lower())
    if amigable:
        return amigable
    base = nombre_proceso.rsplit(".", 1)[0]
    return base.replace("_", " ").title()