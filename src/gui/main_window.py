import customtkinter as ctk
import comtypes
import ctypes
import os
import queue
import threading
from psutil import Error as PsutilError

from paths import ruta_base

from audio.sessions import listar_sesiones
from audio.device_events import registrar_notificador_dispositivo
from audio.routing import (
    listar_dispositivos_salida, enrutar_app, obtener_filas_svcl,
    restaurar_salida_windows,
    obtener_dispositivo_predeterminado_actual,
    DISPOSITIVO_PREDETERMINADO, NOMBRE_PREDETERMINADO,
)
from audio.volume import obtener_volumen, cambiar_volumen
from audio.app_info import obtener_nombres_amigables, nombre_para_mostrar
from storage.rules import guardar_regla, obtener_regla, obtener_todas_las_reglas
from storage.preferences import (
    ACCION_CIERRE_BANDEJA,
    ACCION_CIERRE_SALIR,
    guardar_accion_cierre,
    obtener_accion_cierre,
)
from gui.bandeja import ocultar_a_bandeja

INTERVALO_MONITOREO_MS = 3000  # cada cuánto revisar si hay apps nuevas

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _configurar_identidad_windows():
    """Evita que la barra de tareas agrupe la ventana como una app de Python."""
    app_id = "ProyectoAudio.Aplicacion"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        _configurar_identidad_windows()
        super().__init__()
        self.title("Proyecto_Audio")
        self.geometry("680x460")
        self.minsize(560, 320)

        try:
            icon_path = os.path.join(ruta_base(), "assets", "icon.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass

        self.accion_cierre = obtener_accion_cierre()
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)

        self.dispositivos = []
        self.opciones = {}   # nombre_amigable (o "Predeterminado...") -> nombre_completo real o sentinel
        self.filas = {}
        self.procesos_conocidos = set()
        self.dispositivo_predeterminado_conocido = None
        self.resultados_monitoreo = queue.Queue()
        self.evento_cambio_predeterminado = threading.Event()
        self.monitoreo_en_curso = False
        self.id_proximo_monitoreo = None
        self.enumerador_notificaciones = None
        self.notificador_dispositivo = None
        self.aplicar_reglas_iniciales = True
        self.salida_en_curso = False

        self._construir_interfaz()
        self.actualizar()
        self._iniciar_notificaciones_dispositivo()
        self._programar_monitoreo(0)
        self.after(100, self._comprobar_evento_dispositivo)

    def _construir_interfaz(self):
        barra_superior = ctk.CTkFrame(self, fg_color="transparent")
        barra_superior.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            barra_superior, text="Proyecto_Audio",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            barra_superior, text="Actualizar", width=100,
            command=self.actualizar
        ).pack(side="right")

        ctk.CTkButton(
            barra_superior, text="Configuración", width=110,
            command=self._abrir_configuracion
        ).pack(side="right", padx=(0, 8))

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=24)
        fuente_encabezado = ctk.CTkFont(size=12, weight="bold")

        ctk.CTkLabel(encabezado, text="APLICACIÓN", font=fuente_encabezado, width=160, anchor="w").pack(side="left")
        ctk.CTkLabel(encabezado, text="DISPOSITIVO", font=fuente_encabezado, width=220, anchor="w").pack(side="left")
        ctk.CTkLabel(encabezado, text="VOLUMEN", font=fuente_encabezado, anchor="w").pack(side="left", padx=(10, 0))

        self.contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.contenedor.pack(fill="both", expand=True, padx=16, pady=(6, 6))

        self.label_estado = ctk.CTkLabel(
            self,
            text="Listo",
            anchor="w",
            text_color=("gray40", "gray70"),
        )
        self.label_estado.pack(fill="x", padx=24, pady=(0, 12))

    def _mostrar_estado(self, mensaje, es_error=False):
        """Muestra el resultado de una operación dentro de la ventana."""
        color = ("#B00020", "#FF6B6B") if es_error else ("#187A2F", "#69D28B")
        self.label_estado.configure(text=mensaje, text_color=color)

    def _al_cerrar(self):
        """Aplica el comportamiento de cierre elegido por el usuario."""
        if self.accion_cierre == ACCION_CIERRE_BANDEJA:
            ocultar_a_bandeja(self, self._salir_aplicacion)
        else:
            self._salir_aplicacion()

    def _salir_aplicacion(self):
        """Detiene el monitoreo y prepara el audio antes de cerrar."""
        if self.salida_en_curso:
            return

        self.salida_en_curso = True
        if self.id_proximo_monitoreo is not None:
            self.after_cancel(self.id_proximo_monitoreo)
            self.id_proximo_monitoreo = None

        self._mostrar_estado("Restaurando las aplicaciones antes de salir...")
        self.update_idletasks()
        self._esperar_monitoreo_para_salir()

    def _esperar_monitoreo_para_salir(self):
        """Evita que una regla se reaplique después del restablecimiento."""
        if self.monitoreo_en_curso:
            self.after(100, self._esperar_monitoreo_para_salir)
            return

        try:
            for proceso in obtener_todas_las_reglas():
                if not restaurar_salida_windows(proceso):
                    print(f"No se pudo restaurar {proceso} al salir")
        except Exception as error:
            # Un fallo al restaurar no debe impedir que el usuario cierre.
            print(f"No se pudo restaurar el audio al salir: {error}")
        finally:
            self.destroy()

    def _abrir_configuracion(self):
        """Abre una ventana para elegir el comportamiento del botón X."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Configuración")
        ventana.geometry("430x230")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Al cerrar la ventana principal",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=24, pady=(24, 14))

        accion_elegida = ctk.StringVar(value=self.accion_cierre)

        ctk.CTkRadioButton(
            ventana,
            text="Minimizar a la bandeja del sistema",
            variable=accion_elegida,
            value=ACCION_CIERRE_BANDEJA,
        ).pack(anchor="w", padx=28, pady=6)

        ctk.CTkRadioButton(
            ventana,
            text="Salir completamente de la aplicación",
            variable=accion_elegida,
            value=ACCION_CIERRE_SALIR,
        ).pack(anchor="w", padx=28, pady=6)

        def guardar():
            self.accion_cierre = accion_elegida.get()
            guardar_accion_cierre(self.accion_cierre)
            self._mostrar_estado("Configuración de cierre guardada")
            ventana.destroy()

        ctk.CTkButton(
            ventana,
            text="Guardar",
            width=110,
            command=guardar,
        ).pack(pady=(18, 0))

    def actualizar(self):
        try:
            filas_svcl = obtener_filas_svcl()
            dispositivos = listar_dispositivos_salida(filas_svcl)
            nombres_amigables = obtener_nombres_amigables(filas_svcl)
            sesiones = listar_sesiones()
        except FileNotFoundError:
            mensaje = "No se encontró svcl.exe en la carpeta tools"
            self._mostrar_estado(mensaje, es_error=True)
            print(mensaje)
            return
        except Exception as error:
            mensaje = f"No se pudo actualizar el audio: {error}"
            self._mostrar_estado(mensaje, es_error=True)
            print(mensaje)
            return

        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.filas.clear()

        self.dispositivos = dispositivos

        self.opciones = {
            NOMBRE_PREDETERMINADO: DISPOSITIVO_PREDETERMINADO,
        }
        for d in self.dispositivos:
            self.opciones[d["nombre_amigable"]] = d["nombre_completo"]
        nombres_para_combo = list(self.opciones.keys())

        procesos_vistos = set()
        for sesion in sesiones:
            if not sesion.Process:
                continue
            try:
                nombre_proceso = sesion.Process.name()
            except (OSError, PsutilError):
                # El proceso puede cerrarse entre la detección y esta consulta.
                continue
            if nombre_proceso in procesos_vistos:
                continue
            procesos_vistos.add(nombre_proceso)

            texto_mostrado = nombre_para_mostrar(nombre_proceso, nombres_amigables)

            fila = ctk.CTkFrame(self.contenedor, corner_radius=10)
            fila.pack(fill="x", pady=5, padx=2)

            ctk.CTkLabel(fila, text=texto_mostrado, width=150, anchor="w").pack(side="left", padx=(12, 6), pady=10)

            combo = ctk.CTkComboBox(fila, values=nombres_para_combo, width=220, state="readonly")
            combo.pack(side="left", padx=6, pady=10)

            regla = obtener_regla(nombre_proceso)
            if regla and regla["nombre_completo"] == DISPOSITIVO_PREDETERMINADO:
                combo.set(NOMBRE_PREDETERMINADO)
            elif regla and regla["nombre_amigable"] in self.opciones:
                combo.set(regla["nombre_amigable"])
            else:
                # Sin una regla propia, Windows ya controla la salida de la
                # aplicación mediante su dispositivo predeterminado.
                combo.set(NOMBRE_PREDETERMINADO)

            combo.configure(
                command=lambda valor, proceso=nombre_proceso, c=combo: self._on_seleccion(proceso, c)
            )

            try:
                volumen_actual = int(obtener_volumen(sesion) * 100)
            except OSError:
                volumen_actual = 100

            label_volumen = ctk.CTkLabel(fila, text=f"{volumen_actual}%", width=36)

            slider = ctk.CTkSlider(fila, from_=0, to=100, width=120)
            slider.set(volumen_actual)
            slider.configure(
                command=lambda valor, s=sesion, lbl=label_volumen: self._on_cambio_volumen(valor, s, lbl)
            )
            slider.pack(side="left", padx=(10, 6), pady=10)
            label_volumen.pack(side="left", padx=(0, 12), pady=10)

            self.filas[nombre_proceso] = {"combo": combo, "sesion": sesion}

        self.procesos_conocidos = procesos_vistos

    def _on_seleccion(self, nombre_proceso, combo):
        seleccionado = combo.get()
        if seleccionado not in self.opciones:
            return

        elegido = self.opciones[seleccionado]

        if elegido == DISPOSITIVO_PREDETERMINADO:
            destino_real = obtener_dispositivo_predeterminado_actual()
            if not destino_real:
                mensaje = "No se pudo detectar el dispositivo predeterminado actual"
                self._mostrar_estado(mensaje, es_error=True)
                print(mensaje)
                return
            if enrutar_app(nombre_proceso, destino_real):
                guardar_regla(nombre_proceso, DISPOSITIVO_PREDETERMINADO, NOMBRE_PREDETERMINADO)
                mensaje = f"{nombre_proceso} ahora sigue el dispositivo predeterminado"
                self._mostrar_estado(mensaje)
                print(f"{mensaje} (guardado)")
            else:
                self._mostrar_estado(
                    f"No se pudo enrutar {nombre_proceso}",
                    es_error=True,
                )
        else:
            dispositivo = next(d for d in self.dispositivos if d["nombre_amigable"] == seleccionado)
            if enrutar_app(nombre_proceso, dispositivo["nombre_completo"]):
                guardar_regla(nombre_proceso, dispositivo["nombre_completo"], dispositivo["nombre_amigable"])
                mensaje = f"{nombre_proceso} fue asignado a {dispositivo['nombre_amigable']}"
                self._mostrar_estado(mensaje)
                print(f"{mensaje} (guardado)")
            else:
                mensaje = f"No se pudo enrutar {nombre_proceso}"
                self._mostrar_estado(mensaje, es_error=True)
                print(mensaje)

    def _on_cambio_volumen(self, valor, sesion, label_volumen):
        nivel = float(valor) / 100
        cambiar_volumen(sesion, nivel)
        label_volumen.configure(text=f"{int(float(valor))}%")

    def _iniciar_notificaciones_dispositivo(self):
        """Escucha los cambios de salida predeterminada informados por Windows."""
        try:
            referencias = registrar_notificador_dispositivo(
                self.evento_cambio_predeterminado
            )
            self.enumerador_notificaciones, self.notificador_dispositivo = referencias
        except Exception as error:
            # El monitoreo periódico continúa funcionando como respaldo.
            mensaje = f"No se pudo activar la detección inmediata: {error}"
            self._mostrar_estado(mensaje, es_error=True)
            print(mensaje)

    def _comprobar_evento_dispositivo(self):
        """Inicia una consulta inmediata cuando Windows informa un cambio."""
        if self.salida_en_curso:
            return

        if (
            self.evento_cambio_predeterminado.is_set()
            and not self.monitoreo_en_curso
        ):
            self.evento_cambio_predeterminado.clear()
            self._programar_monitoreo(0)

        self.after(100, self._comprobar_evento_dispositivo)

    def _programar_monitoreo(self, demora_ms):
        """Programa una única comprobación y reemplaza la espera anterior."""
        if self.salida_en_curso:
            return

        if self.id_proximo_monitoreo is not None:
            self.after_cancel(self.id_proximo_monitoreo)
        self.id_proximo_monitoreo = self.after(
            demora_ms,
            self._verificar_sesiones_nuevas,
        )

    def _verificar_sesiones_nuevas(self):
        """Inicia una consulta de sesiones sin bloquear la interfaz."""
        self.id_proximo_monitoreo = None
        if self.monitoreo_en_curso:
            return
        self.monitoreo_en_curso = True

        procesos_anteriores = set(self.procesos_conocidos)
        predeterminado_anterior = self.dispositivo_predeterminado_conocido
        aplicar_reglas_iniciales = self.aplicar_reglas_iniciales
        hilo = threading.Thread(
            target=self._consultar_sesiones_en_segundo_plano,
            args=(
                procesos_anteriores,
                predeterminado_anterior,
                aplicar_reglas_iniciales,
            ),
            daemon=True,
        )
        hilo.start()
        self.after(100, self._recoger_resultado_monitoreo)

    def _consultar_sesiones_en_segundo_plano(
        self,
        procesos_anteriores,
        predeterminado_anterior,
        aplicar_reglas_iniciales,
    ):
        """Consulta Windows desde un hilo y entrega datos, nunca widgets."""
        resultado = {
            "procesos": procesos_anteriores,
            "dispositivo_predeterminado": predeterminado_anterior,
            "mensajes": [],
            "error": None,
        }
        com_inicializado = False

        try:
            # Cada hilo que utiliza las interfaces COM de Windows debe
            # inicializarlas y liberarlas de manera independiente.
            comtypes.CoInitialize()
            com_inicializado = True

            procesos_actuales = set()
            for sesion in listar_sesiones():
                if not sesion.Process:
                    continue
                try:
                    procesos_actuales.add(sesion.Process.name())
                except (OSError, PsutilError):
                    continue

            resultado["procesos"] = procesos_actuales
            nuevos = procesos_actuales - procesos_anteriores
            predeterminado_actual = obtener_dispositivo_predeterminado_actual()
            resultado["dispositivo_predeterminado"] = predeterminado_actual
            cambio_predeterminado = (
                predeterminado_actual is not None
                and predeterminado_actual != predeterminado_anterior
            )

            reglas = obtener_todas_las_reglas()
            procesos_a_enrutar = (
                set(procesos_actuales)
                if aplicar_reglas_iniciales
                else set(nuevos)
            )
            if cambio_predeterminado:
                procesos_a_enrutar.update(
                    proceso
                    for proceso in procesos_actuales
                    if proceso in reglas
                    and reglas[proceso]["nombre_completo"]
                    == DISPOSITIVO_PREDETERMINADO
                )

            for proceso in procesos_a_enrutar:
                regla = reglas.get(proceso)
                if not regla:
                    continue

                destino = regla["nombre_completo"]
                if destino == DISPOSITIVO_PREDETERMINADO:
                    destino = predeterminado_actual

                if destino and enrutar_app(proceso, destino):
                    if cambio_predeterminado and proceso not in nuevos:
                        mensaje = (
                            f"{proceso} ahora sigue el nuevo dispositivo "
                            "predeterminado"
                        )
                    else:
                        mensaje = (
                            f"Regla automática aplicada: {proceso} → "
                            f"{regla['nombre_amigable']}"
                        )
                    resultado["mensajes"].append((mensaje, False))
                    print(f"[auto] {mensaje}")
                else:
                    resultado["mensajes"].append(
                        (f"No se pudo aplicar la regla de {proceso}", True)
                    )
        except Exception as error:
            resultado["error"] = str(error)
        finally:
            if com_inicializado:
                comtypes.CoUninitialize()
            self.resultados_monitoreo.put(resultado)

    def _recoger_resultado_monitoreo(self):
        """Procesa en el hilo principal los datos obtenidos en segundo plano."""
        try:
            resultado = self.resultados_monitoreo.get_nowait()
        except queue.Empty:
            self.after(100, self._recoger_resultado_monitoreo)
            return

        self.monitoreo_en_curso = False

        if resultado["error"]:
            mensaje = f"No se pudo comprobar el audio: {resultado['error']}"
            self._mostrar_estado(mensaje, es_error=True)
            print(mensaje)
        else:
            self.aplicar_reglas_iniciales = False
            self.dispositivo_predeterminado_conocido = resultado[
                "dispositivo_predeterminado"
            ]

            for mensaje, es_error in resultado["mensajes"]:
                self._mostrar_estado(mensaje, es_error=es_error)

            procesos_actuales = resultado["procesos"]
            if procesos_actuales != self.procesos_conocidos:
                # Se actualiza antes de redibujar para no volver a aplicar una
                # regla si la actualización visual falla de manera aislada.
                self.procesos_conocidos = procesos_actuales
                self.actualizar()

        # Un fallo aislado no debe detener las comprobaciones futuras.
        if not self.salida_en_curso:
            self._programar_monitoreo(INTERVALO_MONITOREO_MS)


def iniciar():
    VentanaPrincipal().mainloop()
