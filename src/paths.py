import sys
import os


def ruta_base():
    """Carpeta base del proyecto. En desarrollo, es la raíz del repo.
    Empaquetado con PyInstaller (--onefile), es la carpeta temporal
    donde PyInstaller extrae los archivos en cada ejecución."""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))