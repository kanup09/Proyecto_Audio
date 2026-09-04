# Proyecto Audio

Aplicación de escritorio para Windows que permite controlar el volumen y
elegir el dispositivo de salida de las aplicaciones que tienen una sesión de
audio activa.

Este es un proyecto de aprendizaje. Su objetivo es practicar Python, interfaces
gráficas, persistencia con SQLite, las API de audio de Windows y la distribución
de aplicaciones con PyInstaller.

## Funciones actuales

- Detecta sesiones de audio activas.
- Muestra los dispositivos de salida disponibles.
- Cambia el volumen de cada aplicación.
- Asigna una aplicación a un dispositivo de salida.
- Guarda las asignaciones en una base de datos SQLite local.
- Se puede minimizar a la bandeja del sistema.

## Requisitos

- Windows 10 u 11.
- Python 3.10 o posterior.
- Un entorno virtual de Python.

El enrutamiento utiliza actualmente `svcl.exe`, perteneciente a
SoundVolumeCommandLine de NirSoft. El archivo `tools/readme.txt` contiene su
licencia y condiciones de redistribución. Una etapa futura del proyecto será
reemplazarlo por una implementación propia basada en las API de Windows.

## Preparar el proyecto

Desde PowerShell, situado en la carpeta del proyecto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El entorno `venv` no se guarda en Git. Cada colaborador lo crea en su equipo a
partir de `requirements.txt`.

## Ejecutar la aplicación

```powershell
python .\src\main.py
```

## Crear el ejecutable

```powershell
pyinstaller .\Proyecto_Audio.spec
```

PyInstaller genera las carpetas `build` y `dist`. Ambas están excluidas del
repositorio porque pueden reconstruirse en cualquier momento. Una versión
terminada del ejecutable puede publicarse en la sección **Releases** de GitHub.

## Estructura

```text
assets/                 Iconos y otros recursos visuales
src/audio/              Sesiones, volumen y enrutamiento de audio
src/gui/                Ventana principal y bandeja del sistema
src/storage/            Base de datos y reglas guardadas
tools/                  Herramienta externa usada para el enrutamiento
Proyecto_Audio.spec     Configuración de PyInstaller
requirements.txt        Dependencias de Python
```

## Qué debe guardarse en Git

Git debe contener el código y los archivos necesarios para reconstruir el
proyecto. No debe contener entornos virtuales, cachés, compilaciones ni datos
personales generados al ejecutar la aplicación. Estas reglas están documentadas
en `.gitignore`.

## Convenciones de documentación

- Los nombres de funciones y variables explican **qué representan**.
- Las docstrings explican el propósito, los argumentos, el resultado y los
  errores relevantes de una función pública.
- Los comentarios explican **por qué** se tomó una decisión que no resulta
  evidente; no repiten literalmente el código.
- El README explica cómo instalar, ejecutar, construir y entender el proyecto.

## Estado del proyecto

En desarrollo. La siguiente mejora planificada es sustituir la herramienta
externa de enrutamiento por código propio y documentar el proceso.
