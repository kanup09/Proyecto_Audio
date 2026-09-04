"""Operaciones de volumen sobre sesiones de audio de Windows.

Las funciones de este módulo reciben sesiones obtenidas mediante ``pycaw``.
Separarlas de la interfaz gráfica permite reutilizarlas y probarlas sin conocer
los controles visuales de la aplicación.
"""

from pycaw.pycaw import ISimpleAudioVolume


def _interfaz_volumen(sesion):
    """Obtiene la interfaz COM que controla el volumen de una sesión."""
    return sesion._ctl.QueryInterface(ISimpleAudioVolume)


def obtener_volumen(sesion):
    """Devuelve el nivel actual de una sesión, entre 0.0 y 1.0."""
    return _interfaz_volumen(sesion).GetMasterVolume()


def cambiar_volumen(sesion, nivel):
    """Cambia el nivel de volumen de una sesión.

    Args:
        sesion: Sesión de audio proporcionada por ``pycaw``.
        nivel: Número entre 0.0 (silencio) y 1.0 (volumen máximo).

    Raises:
        ValueError: Si ``nivel`` está fuera del intervalo permitido.
    """
    if not 0.0 <= nivel <= 1.0:
        raise ValueError("El nivel de volumen debe estar entre 0.0 y 1.0")

    _interfaz_volumen(sesion).SetMasterVolume(nivel, None)


def mutear(sesion, mute=True):
    """Silencia una sesión o restaura su sonido."""
    _interfaz_volumen(sesion).SetMute(mute, None)
