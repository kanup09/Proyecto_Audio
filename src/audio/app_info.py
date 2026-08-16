import subprocess
import csv
import tempfile
import os

from audio.routing import SVCL_PATH


def obtener_nombres_amigables():
    """Devuelve un diccionario {nombre_proceso_en_minuscula: nombre_amigable},
    usando la info de aplicaciones que ya expone svcl.exe (ej: 'spotify.exe' -> 'Spotify')."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        ruta_csv = tmp.name

    subprocess.run([SVCL_PATH, "/scomma", ruta_csv], check=True)

    nombres = {}
    with open(ruta_csv, encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            if fila.get("Type") == "Application":
                ruta_proceso = fila.get("Process Path", "")
                if ruta_proceso:
                    nombre_proceso = os.path.basename(ruta_proceso).lower()
                    nombres[nombre_proceso] = fila.get("Name", "").strip()

    os.remove(ruta_csv)
    return nombres


def nombre_para_mostrar(nombre_proceso, nombres_amigables):
    """Devuelve el nombre amigable si existe; si no, arma uno razonable
    a partir del nombre del proceso (ej: 'wallpaper32.exe' -> 'Wallpaper32')."""
    amigable = nombres_amigables.get(nombre_proceso.lower())
    if amigable:
        return amigable
    base = nombre_proceso.rsplit(".", 1)[0]
    return base.replace("_", " ").title()