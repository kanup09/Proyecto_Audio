from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioSessionManager2, IAudioSessionControl2, DEVICE_STATE, EDataFlow
from pycaw.utils import AudioSession


def listar_sesiones():
    """Devuelve las sesiones de audio activas de TODOS los dispositivos
    de salida, no solo del que está configurado como predeterminado."""
    sesiones = []
    enumerador = AudioUtilities.GetDeviceEnumerator()
    dispositivos = enumerador.EnumAudioEndpoints(EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)

    for i in range(dispositivos.GetCount()):
        dispositivo = dispositivos.Item(i)
        try:
            manager = dispositivo.Activate(IAudioSessionManager2._iid_, CLSCTX_ALL, None)
            manager = manager.QueryInterface(IAudioSessionManager2)
            enum_sesiones = manager.GetSessionEnumerator()
            for j in range(enum_sesiones.GetCount()):
                ctl = enum_sesiones.GetSession(j)
                ctl2 = ctl.QueryInterface(IAudioSessionControl2)
                sesiones.append(AudioSession(ctl2))
        except OSError:
            # Algunos dispositivos (virtuales, deshabilitados) no dejan
            # activar su administrador de sesiones. Los salteamos.
            continue

    return sesiones


def obtener_sesion_por_proceso(nombre_proceso):
    """Busca una sesión por el nombre del proceso, ej: 'Spotify.exe'."""
    for sesion in listar_sesiones():
        if sesion.Process and sesion.Process.name().lower() == nombre_proceso.lower():
            return sesion
    return None