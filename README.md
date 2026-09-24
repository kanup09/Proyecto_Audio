# Proyecto Audio

Aplicación de escritorio para Windows que permite controlar el volumen y elegir
el dispositivo de salida de cada aplicación con una sesión de audio activa.
Las preferencias se guardan y se vuelven a aplicar automáticamente.

Este es un proyecto de aprendizaje orientado a Python, interfaces gráficas,
SQLite, las API de audio de Windows, Git y distribución con PyInstaller.

## Funciones

- Detecta aplicaciones con sesiones de audio activas.
- Muestra los dispositivos de salida disponibles.
- Cambia el volumen de cada aplicación.
- Asigna una aplicación a un dispositivo específico.
- Permite seguir el dispositivo predeterminado de Windows.
- Reacciona cuando Windows cambia su dispositivo predeterminado.
- Guarda y aplica reglas automáticamente al abrir una aplicación.
- Muestra confirmaciones y errores dentro de la ventana.
- Permite elegir si la X minimiza a la bandeja o cierra la aplicación.
- Devuelve las aplicaciones al audio predeterminado al salir completamente.
- Reaplica las reglas guardadas al volver a iniciar Proyecto Audio.
- Conserva la configuración entre ejecuciones.

## Requisitos

- Windows 10 u 11.
- Python 3.10 o posterior.
- Git, si se desea clonar el repositorio.
- Al menos una salida de audio habilitada.

El enrutamiento utiliza actualmente `svcl.exe`, perteneciente a
SoundVolumeCommandLine de NirSoft. Se incluye en `tools` junto con su
documentación y sus condiciones de redistribución.

## Obtener el proyecto desde GitHub

Hay dos formas de usar Proyecto Audio.

### Opción A: usar un ejecutable publicado

Cuando exista una versión en la sección **Releases** de GitHub:

1. Descargar `Proyecto_Audio.exe` desde la versión más reciente.
2. Guardarlo en una carpeta local.
3. Abrirlo con doble clic.

El ejecutable generado con PyInstaller incluye las dependencias y no requiere
una instalación separada de Python. Como todavía no está firmado digitalmente,
Windows puede pedir confirmación antes de abrirlo.

### Opción B: ejecutar el código fuente

En PowerShell:

```powershell
git clone https://github.com/kanup09/Proyecto_Audio.git
cd .\Proyecto_Audio
```

También se puede descargar el repositorio como ZIP desde GitHub y extraerlo en
una carpeta local.

## Preparar el entorno

Crear un entorno virtual evita mezclar las dependencias del proyecto con otros
programas de Python:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si el comando `python` no existe pero está instalado el lanzador de Windows, se
puede usar `py` en la primera línea:

```powershell
py -m venv venv
```

El entorno `venv` se crea en cada computadora y no se guarda en Git.

## Ejecutar

Desde la carpeta que contiene `src`:

```powershell
.\venv\Scripts\python.exe .\src\main.py
```

## Uso básico

1. Abrir una aplicación que reproduzca audio.
2. Presionar **Actualizar** si todavía no aparece en la lista.
3. Elegir un dispositivo o **Predeterminado (seguir a Windows)**.
4. Ajustar el volumen con el control deslizante.
5. Revisar el resultado de la operación en la barra inferior.

El botón **Configuración** permite decidir si la X minimiza la aplicación a la
bandeja o la cierra completamente.

Al minimizar, las reglas siguen activas. Al salir completamente, las
aplicaciones administradas vuelven al dispositivo predeterminado de Windows,
pero sus reglas no se borran. Proyecto Audio las reaplica cuando vuelve a
iniciarse.

## Dependencias principales

| Dependencia | Uso |
|---|---|
| `customtkinter` | Interfaz gráfica |
| `pycaw` | Sesiones de audio y notificaciones de Windows |
| `comtypes` | Acceso a interfaces COM de Windows |
| `psutil` | Información de procesos asociados a las sesiones |
| `pystray` | Icono y menú de la bandeja del sistema |
| `Pillow` | Creación y lectura de imágenes para la bandeja |
| `PyInstaller` | Construcción del ejecutable |
| `svcl.exe` | Listado y enrutamiento de dispositivos por aplicación |

`requirements.txt` contiene las versiones exactas y las dependencias
transitivas necesarias para reproducir el entorno usado por el proyecto.

## Datos guardados

Las reglas y preferencias se almacenan localmente en:

```text
%APPDATA%\Proyecto_Audio\reglas.db
```

La base usa SQLite y no se envía a ningún servicio externo.

## Solución de problemas

### Una aplicación no aparece

La aplicación debe tener una sesión de audio. Reproducir algún sonido y
presionar **Actualizar**.

### No se puede cambiar el dispositivo

Comprobar que los tres archivos originales estén presentes en `tools`:

```text
svcl.exe
svcl.chm
readme.txt
```

### PowerShell no reconoce `python`

Probar con `py` para crear el entorno virtual. Después utilizar siempre el
intérprete ubicado en `venv\Scripts\python.exe`.

### Windows muestra una advertencia al abrir el ejecutable

El proyecto todavía no firma digitalmente sus ejecutables. Descargar versiones
únicamente desde el repositorio oficial y verificar su origen antes de abrirlas.

## Crear el ejecutable

```powershell
.\venv\Scripts\pyinstaller.exe .\Proyecto_Audio.spec
```

El resultado aparece en `dist`. Las carpetas `build` y `dist` no se versionan
porque pueden reconstruirse. Los ejecutables terminados pueden publicarse en la
sección **Releases** de GitHub.

## Licencias y componentes externos

SoundVolumeCommandLine es freeware de NirSoft, no software de código abierto.
Su licencia permite distribuir el paquete por Internet si no se cobra por él,
no forma parte de un producto comercial y se incluyen todos sus archivos sin
modificaciones. La licencia original está en `tools/readme.txt`.

Antes de aceptar contribuciones o permitir la reutilización del código fuente,
el proyecto debe elegir y añadir una licencia propia. La licencia futura del
proyecto no reemplazará las condiciones particulares de `svcl.exe`.

## Estructura

```text
assets/                  Recursos visuales
docs/                    Guías públicas de desarrollo
src/audio/               Sesiones, volumen, eventos y enrutamiento
src/gui/                 Ventana principal y bandeja del sistema
src/storage/             SQLite, reglas y preferencias
tools/                   SoundVolumeCommandLine y su documentación
Proyecto_Audio.spec      Configuración de PyInstaller
requirements.txt         Dependencias fijadas
```

## Limitación conocida

Algunos controladores Realtek mantienen los endpoints analógicos en estado
activo aunque se retire físicamente el conector. Detectar esos casos requiere
consultar interfaces de presencia del jack y depende del soporte del
controlador.

## Estado

Proyecto en desarrollo. Cada mejora se implementa, prueba manualmente y guarda
en un commit independiente.
