import sqlite3
import os

RUTA_DB = os.path.join(os.path.dirname(__file__), "..", "..", "reglas.db")


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