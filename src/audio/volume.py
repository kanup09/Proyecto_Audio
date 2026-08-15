from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import ISimpleAudioVolume

def obtener_volumen(sesion):
    """Devuelve el volumen de una sesión (0.0 a 1.0)."""
    volumen = sesion._ctl.QueryInterface(ISimpleAudioVolume)
    return volumen.GetMasterVolume()

def cambiar_volumen(sesion, nivel):
    """Cambia el volumen de una sesión. nivel entre 0.0 y 1.0."""
    volumen = sesion._ctl.QueryInterface(ISimpleAudioVolume)
    volumen.SetMasterVolume(nivel, None)

def mutear(sesion, mute=True):
    """Mutea o desmutea una sesión."""
    volumen = sesion._ctl.QueryInterface(ISimpleAudioVolume)
    volumen.SetMute(mute, None)