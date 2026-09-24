"""Notificaciones de Windows relacionadas con dispositivos de audio."""

from pycaw.callbacks import MMNotificationClient
from pycaw.pycaw import AudioUtilities


class NotificadorDispositivoPredeterminado(MMNotificationClient):
    """Convierte el callback COM de Windows en un evento de Python."""

    def __init__(self, evento_cambio):
        super().__init__()
        self.evento_cambio = evento_cambio

    def on_default_device_changed(
        self,
        flow,
        flow_id,
        role,
        role_id,
        default_device_id,
    ):
        """Marca un cambio cuando Windows modifica una salida predeterminada."""
        if flow == "eRender":
            self.evento_cambio.set()


def registrar_notificador_dispositivo(evento_cambio):
    """Registra el callback y devuelve referencias que deben conservarse."""
    enumerador = AudioUtilities.GetDeviceEnumerator()
    notificador = NotificadorDispositivoPredeterminado(evento_cambio)
    enumerador.RegisterEndpointNotificationCallback(notificador)
    return enumerador, notificador
