import sqlite3
import os


def obtener_ruta_db():
    """Ubica la base de datos en una carpeta estable del usuario
    (AppData\\Roaming), no al lado del código fuente. Así los datos
    sobreviven aunque el .exe se ejecute desde una carpeta temporal."""
    carpeta_datos = os.path.join(os.getenv("APPDATA"), "Proyecto_Audio")
    os.makedirs(carpeta_datos, exist_ok=True)
    return os.path.join(carpeta_datos, "reglas.db")


RUTA_DB = obtener_ruta_db()


def obtener_conexion():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS reglas (
            proceso TEXT PRIMARY KEY,
            dispositivo_nombre_completo TEXT NOT NULL,
            dispositivo_nombre_amigable TEXT NOT NULL
        )
    """)
    return conexion