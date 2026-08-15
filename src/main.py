from audio.routing import listar_dispositivos_salida, enrutar_app

if __name__ == "__main__":
    dispositivos = listar_dispositivos_salida()
    print("Dispositivos de salida disponibles:")
    for i, d in enumerate(dispositivos):
        print(f"  [{i}] {d['nombre_amigable']}")

    # Ejemplo: mandar Spotify al dispositivo número 0 de la lista
    if dispositivos:
        exito = enrutar_app("Spotify.exe", dispositivos[0]["nombre_completo"])
        print("Ruteo aplicado" if exito else "Falló el ruteo")
