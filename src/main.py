from audio.sessions import obtener_sesion_por_proceso
from audio.volume import obtener_volumen, cambiar_volumen

if __name__ == "__main__":
    sesion = obtener_sesion_por_proceso("Spotify.exe")

    if sesion:
        actual = obtener_volumen(sesion)
        print(f"Volumen actual: {actual:.2f}")

        nuevo = max(0.0, actual + 0.1)  # baja 10 puntos, sin ir debajo de 0
        cambiar_volumen(sesion, nuevo)
        print(f"Volumen nuevo: {nuevo:.2f}")
    else:
        print("No se encontró la sesión de Spotify")