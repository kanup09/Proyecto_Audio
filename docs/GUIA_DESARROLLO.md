# Guía de desarrollo

Esta guía explica las decisiones básicas de mantenimiento del repositorio. La
idea no es memorizar comandos, sino entender qué información pertenece al
proyecto y cuál puede volver a generarse.

## 1. Qué hace `.gitignore`

Git observa todos los archivos que aparecen dentro del repositorio. El archivo
`.gitignore` contiene patrones que le indican cuáles no debe comenzar a seguir.

Ejemplos del proyecto:

```gitignore
venv/          # Entorno virtual instalado en esta computadora
__pycache__/   # Código intermedio generado por Python
build/         # Archivos temporales de PyInstaller
dist/          # Ejecutable generado por PyInstaller
reglas.db      # Preferencias personales del usuario
```

Una regla importante: `.gitignore` solo afecta archivos que Git todavía no
sigue. Si un archivo ya fue incluido en un commit, hay que retirarlo del índice:

```powershell
git rm -r --cached build dist
git rm --cached reglas.db
```

`--cached` significa «dejar de versionar»; no borra la copia del disco. Después
se crea un commit que registra esa limpieza.

## 2. Flujo de trabajo con Git

Antes de preparar un cambio:

```powershell
git status
git diff
```

Para preparar y revisar el cambio:

```powershell
git add .gitignore README.md docs src
git diff --staged
```

Si la revisión es correcta:

```powershell
git commit -m "Ordena el repositorio y agrega documentación"
git push origin main
```

Conviene que cada commit represente una idea completa y pequeña. Un mensaje
como `Corrige validación del volumen` explica mejor la intención que `cambios`.

## 3. Cómo documentar código

Hay cuatro herramientas distintas:

### Nombres claros

Son la documentación más cercana al código. `obtener_volumen` comunica mejor la
intención que `get_v`.

### Docstrings

Describen módulos, clases y funciones. Deben aclarar el contrato del código:
qué hace, qué recibe, qué devuelve y qué errores puede producir.

```python
def cambiar_volumen(sesion, nivel):
    """Cambia el nivel de volumen de una sesión.

    Args:
        sesion: Sesión de audio proporcionada por pycaw.
        nivel: Número entre 0.0 y 1.0.

    Raises:
        ValueError: Si el nivel está fuera del intervalo permitido.
    """
```

No es necesario escribir todas las secciones cuando la función es evidente y
no tiene condiciones especiales.

### Comentarios

Un comentario debe explicar una razón, una limitación o una decisión difícil de
deducir. Este es útil:

```python
# El CSV incluye una marca BOM; utf-8-sig la elimina al leerlo.
```

Este comentario no aporta información:

```python
# Aumenta contador en uno.
contador += 1
```

### README

Documenta el proyecto desde la perspectiva de alguien que acaba de encontrarlo:
qué hace, qué necesita, cómo se instala, cómo se ejecuta y cuáles son sus
limitaciones conocidas.

## 4. Dependencias

`requirements.txt` permite reconstruir el entorno. No sustituye al entorno
virtual: contiene una lista de paquetes, mientras que `venv` contiene los
paquetes instalados para una computadora concreta.

Cuando se agregue una dependencia, debe existir una razón visible en el código.
Las herramientas exclusivas de desarrollo, como PyInstaller, pueden separarse
más adelante en un archivo `requirements-dev.txt`.

## 5. Antes de publicar un cambio

Comprueba siempre:

1. Que `git status` no incluya contraseñas, bases de datos personales ni
   archivos generados.
2. Que la aplicación arranque dentro de un entorno limpio.
3. Que el README siga describiendo los comandos reales.
4. Que las nuevas funciones validen sus entradas y documenten las decisiones
   poco evidentes.
5. Que el commit contenga una sola mejora comprensible.
