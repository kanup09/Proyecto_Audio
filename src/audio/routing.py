import subprocess
import csv
import os
import tempfile

# Ruta al ejecutable de svcl.exe dentro del proyecto
SVCL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "svcl.exe")


def listar_dispositivos_salida():
    """Devuelve una lista de dispositivos de salida disponibles,
    con su nombre completo tal como lo necesita svcl.exe."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        ruta_csv = tmp.name

    subprocess.run([SVCL_PATH, "/scomma", ruta_csv], check=True)

    dispositivos = []
    with open(ruta_csv, encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            es_dispositivo_fisico = fila.get("Type") == "Device"
            es_salida_activa = (
                fila.get("Direction") == "Render"
                and fila.get("Device State") == "Active"
            )
            if es_dispositivo_fisico and es_salida_activa:
                dispositivos.append({
                    "nombre_amigable": fila.get("Name", "").strip(),
                    "nombre_completo": fila.get("Command-Line Friendly ID", "").strip(),
                })

    os.remove(ruta_csv)
    return dispositivos


def enrutar_app(nombre_proceso, nombre_dispositivo):
    """Manda el audio de un proceso a un dispositivo de salida específico."""
    resultado = subprocess.run(
        [SVCL_PATH, "/SetAppDefault", nombre_dispositivo, "all", nombre_proceso],
        capture_output=True, text=True
    )
    if resultado.returncode != 0:
        print(f"Error al enrutar {nombre_proceso}: {resultado.stderr}")
        return False
    return True