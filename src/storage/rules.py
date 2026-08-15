from storage.db import obtener_conexion


def guardar_regla(proceso, dispositivo_nombre_completo, dispositivo_nombre_amigable):
    """Guarda o actualiza la regla para un proceso."""
    conexion = obtener_conexion()
    conexion.execute("""
        INSERT INTO reglas (proceso, dispositivo_nombre_completo, dispositivo_nombre_amigable)
        VALUES (?, ?, ?)
        ON CONFLICT(proceso) DO UPDATE SET
            dispositivo_nombre_completo = excluded.dispositivo_nombre_completo,
            dispositivo_nombre_amigable = excluded.dispositivo_nombre_amigable
    """, (proceso, dispositivo_nombre_completo, dispositivo_nombre_amigable))
    conexion.commit()
    conexion.close()


def obtener_regla(proceso):
    """Devuelve el dispositivo guardado para un proceso, o None si no hay regla."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT dispositivo_nombre_completo, dispositivo_nombre_amigable FROM reglas WHERE proceso = ?",
        (proceso,)
    ).fetchone()
    conexion.close()
    if fila:
        return {"nombre_completo": fila[0], "nombre_amigable": fila[1]}
    return None


def obtener_todas_las_reglas():
    """Devuelve todas las reglas guardadas, como {proceso: {...}}."""
    conexion = obtener_conexion()
    filas = conexion.execute(
        "SELECT proceso, dispositivo_nombre_completo, dispositivo_nombre_amigable FROM reglas"
    ).fetchall()
    conexion.close()
    return {
        fila[0]: {"nombre_completo": fila[1], "nombre_amigable": fila[2]}
        for fila in filas
    }