import subprocess
import csv
import os
import tempfile

from paths import ruta_base

SVCL_PATH = os.path.join(ruta_base(), "tools", "svcl.exe")

# Evita que Windows abra una consola negra momentánea cada vez que
# lanzamos svcl.exe desde una app sin consola propia (--windowed).
FLAGS_SIN_CONSOLA = subprocess.CREATE_NO_WINDOW

# Valor especial que guardamos en la base de datos para las reglas que
# dicen "seguí al dispositivo predeterminado de Windows" en vez de un
# dispositivo fijo. No es un ID real de dispositivo.
DISPOSITIVO_PREDETERMINADO = "PREDETERMINADO"
NOMBRE_PREDETERMINADO = "Predeterminado (seguir a Windows)"


def obtener_filas_svcl():
    """Ejecuta svcl.exe UNA sola vez y devuelve todas las filas del CSV
    como lista de diccionarios. Tanto la lista de dispositivos como los
    nombres amigables de las apps se sacan de este mismo resultado, para
    no lanzar el proceso dos veces en cada actualización de la ventana."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        ruta_csv = tmp.name

    subprocess.run(
        [SVCL_PATH, "/scomma", ruta_csv],
        check=True,
        creationflags=FLAGS_SIN_CONSOLA,
    )

    with open(ruta_csv, encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))

    os.remove(ruta_csv)
    return filas


def listar_dispositivos_salida(filas=None):
    """Devuelve los dispositivos de salida activos, con nombre único
    (incluye la marca del hardware, ej: 'Altavoces (Realtek(R) Audio)')."""
    if filas is None:
        filas = obtener_filas_svcl()

    dispositivos = []
    for fila in filas:
        es_dispositivo_fisico = fila.get("Type") == "Device"
        es_salida_activa = (
            fila.get("Direction") == "Render"
            and fila.get("Device State") == "Active"
        )
        if es_dispositivo_fisico and es_salida_activa:
            nombre = fila.get("Name", "").strip()
            hardware = fila.get("Device Name", "").strip()
            dispositivos.append({
                "nombre_amigable": f"{nombre} ({hardware})" if hardware else nombre,
                "nombre_completo": fila.get("Command-Line Friendly ID", "").strip(),
            })
    return dispositivos


def obtener_dispositivo_predeterminado_actual(filas=None):
    """Busca cuál dispositivo de salida es HOY el predeterminado del
    sistema (columna 'Default' del CSV de svcl.exe) y devuelve su ID."""
    if filas is None:
        filas = obtener_filas_svcl()

    for fila in filas:
        es_dispositivo_fisico = fila.get("Type") == "Device"
        es_salida = fila.get("Direction") == "Render"
        es_default = fila.get("Default") == "Render"
        if es_dispositivo_fisico and es_salida and es_default:
            return fila.get("Command-Line Friendly ID", "").strip()
    return None


def enrutar_app(nombre_proceso, nombre_dispositivo):
    """Manda el audio de un proceso a un dispositivo de salida específico."""
    resultado = subprocess.run(
        [SVCL_PATH, "/SetAppDefault", nombre_dispositivo, "all", nombre_proceso],
        capture_output=True, text=True,
        creationflags=FLAGS_SIN_CONSOLA,
    )
    if resultado.returncode != 0:
        print(f"Error al enrutar {nombre_proceso}: {resultado.stderr}")
        return False
    return True