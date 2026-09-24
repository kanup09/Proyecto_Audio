"""Preferencias generales de la aplicación guardadas en SQLite."""

from storage.db import obtener_conexion


ACCION_CIERRE_BANDEJA = "bandeja"
ACCION_CIERRE_SALIR = "salir"
CLAVE_ACCION_CIERRE = "accion_cierre"


def obtener_accion_cierre():
    """Devuelve el comportamiento elegido para el botón de cerrar."""
    conexion = obtener_conexion()
    fila = conexion.execute(
        "SELECT valor FROM configuracion WHERE clave = ?",
        (CLAVE_ACCION_CIERRE,),
    ).fetchone()
    conexion.close()

    if fila and fila[0] in (ACCION_CIERRE_BANDEJA, ACCION_CIERRE_SALIR):
        return fila[0]
    return ACCION_CIERRE_BANDEJA


def guardar_accion_cierre(accion):
    """Guarda qué debe hacer la aplicación cuando se presiona la X."""
    if accion not in (ACCION_CIERRE_BANDEJA, ACCION_CIERRE_SALIR):
        raise ValueError("Acción de cierre no válida")

    conexion = obtener_conexion()
    conexion.execute(
        """
        INSERT INTO configuracion (clave, valor)
        VALUES (?, ?)
        ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor
        """,
        (CLAVE_ACCION_CIERRE, accion),
    )
    conexion.commit()
    conexion.close()
