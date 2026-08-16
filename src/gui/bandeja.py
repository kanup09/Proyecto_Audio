import threading

from PIL import Image, ImageDraw
import pystray


def _crear_imagen_icono():
    """Dibuja un círculo simple para no depender de un archivo .ico externo."""
    imagen = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.ellipse((8, 8, 56, 56), fill=(30, 144, 255, 255))
    return imagen


def _iniciar_icono(ventana):
    """pystray corre su propio loop bloqueante (icono.run()), por eso
    esta función se llama siempre desde un hilo aparte, nunca desde el
    hilo principal de Tkinter (si no, se congelaría la ventana entera)."""

    def mostrar(icono, item):
        icono.stop()
        # ventana.after(0, ...) programa la llamada en el hilo de Tkinter:
        # nunca hay que tocar widgets de Tkinter directo desde otro hilo.
        ventana.after(0, ventana.deiconify)

    def salir(icono, item):
        icono.stop()
        ventana.after(0, ventana.destroy)

    menu = pystray.Menu(
        pystray.MenuItem("Abrir", mostrar, default=True),
        pystray.MenuItem("Salir", salir),
    )
    icono = pystray.Icon("Proyecto_Audio", _crear_imagen_icono(), "Proyecto_Audio", menu)
    icono.run()


def ocultar_a_bandeja(ventana):
    """Oculta la ventana y deja el ícono corriendo en la bandeja."""
    ventana.withdraw()
    hilo = threading.Thread(target=_iniciar_icono, args=(ventana,), daemon=True)
    hilo.start()