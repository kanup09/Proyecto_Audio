from pycaw.pycaw import AudioUtilities

def listar_sesiones():
    """Devuelve la lista de sesiones de audio activas."""
    return AudioUtilities.GetAllSessions()

def obtener_sesion_por_proceso(nombre_proceso):
    """Busca una sesión por el nombre del proceso, ej: 'Spotify.exe'."""
    for sesion in listar_sesiones():
        if sesion.Process and sesion.Process.name().lower() == nombre_proceso.lower():
            return sesion
    return None