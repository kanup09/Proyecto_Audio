import customtkinter as ctk
import os

from paths import ruta_base

from audio.sessions import listar_sesiones
from audio.routing import listar_dispositivos_salida, enrutar_app, obtener_filas_svcl
from audio.volume import obtener_volumen, cambiar_volumen
from audio.app_info import obtener_nombres_amigables, nombre_para_mostrar
from storage.rules import guardar_regla, obtener_regla

INTERVALO_MONITOREO_MS = 3000  # cada cuánto revisar si hay apps nuevas

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        ruta_icono = os.path.join(
            ruta_base(),
            "assets",
            "icon.ico"
        )

        self.iconbitmap(ruta_icono)
        self.title("Proyecto_Audio")
        self.geometry("680x460")
        self.minsize(560, 320)

        self.dispositivos = []
        self.filas = {}
        self.procesos_conocidos = set()

        self._construir_interfaz()
        self.actualizar()
        self._verificar_sesiones_nuevas()

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

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.pack(fill="x", padx=24)
        fuente_encabezado = ctk.CTkFont(size=12, weight="bold")

        ctk.CTkLabel(encabezado, text="APLICACIÓN", font=fuente_encabezado, width=160, anchor="w").pack(side="left")
        ctk.CTkLabel(encabezado, text="DISPOSITIVO", font=fuente_encabezado, width=220, anchor="w").pack(side="left")
        ctk.CTkLabel(encabezado, text="VOLUMEN", font=fuente_encabezado, anchor="w").pack(side="left", padx=(10, 0))

        self.contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.contenedor.pack(fill="both", expand=True, padx=16, pady=(6, 16))

    def actualizar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.filas.clear()

        # Una sola llamada a svcl.exe por refresco: antes pedíamos el CSV
        # dos veces (dispositivos y nombres amigables por separado), lo
        # que duplicaba el corte/freeze de la interfaz en cada refresco.
        filas_svcl = obtener_filas_svcl()
        self.dispositivos = listar_dispositivos_salida(filas_svcl)
        nombres_dispositivos = [d["nombre_amigable"] for d in self.dispositivos]
        nombres_amigables = obtener_nombres_amigables(filas_svcl)

        procesos_vistos = set()
        for sesion in listar_sesiones():
            if not sesion.Process:
                continue
            nombre_proceso = sesion.Process.name()
            if nombre_proceso in procesos_vistos:
                continue
            procesos_vistos.add(nombre_proceso)

            texto_mostrado = nombre_para_mostrar(nombre_proceso, nombres_amigables)

            fila = ctk.CTkFrame(self.contenedor, corner_radius=10)
            fila.pack(fill="x", pady=5, padx=2)

            ctk.CTkLabel(fila, text=texto_mostrado, width=150, anchor="w").pack(side="left", padx=(12, 6), pady=10)

            combo = ctk.CTkComboBox(fila, values=nombres_dispositivos, width=210, state="readonly")
            combo.pack(side="left", padx=6, pady=10)

            regla = obtener_regla(nombre_proceso)
            if regla and regla["nombre_amigable"] in nombres_dispositivos:
                combo.set(regla["nombre_amigable"])
            else:
                combo.set("Elegir dispositivo...")

            combo.configure(
                command=lambda valor, proceso=nombre_proceso, c=combo: self._on_seleccion(proceso, c)
            )

            try:
                volumen_actual = int(obtener_volumen(sesion) * 100)
            except OSError:
                volumen_actual = 100

            label_volumen = ctk.CTkLabel(fila, text=f"{volumen_actual}%", width=36)

            slider = ctk.CTkSlider(fila, from_=0, to=100, width=130)
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
        if seleccionado not in [d["nombre_amigable"] for d in self.dispositivos]:
            return
        dispositivo = next(d for d in self.dispositivos if d["nombre_amigable"] == seleccionado)
        if enrutar_app(nombre_proceso, dispositivo["nombre_completo"]):
            guardar_regla(nombre_proceso, dispositivo["nombre_completo"], dispositivo["nombre_amigable"])
            print(f"{nombre_proceso} -> {dispositivo['nombre_amigable']} (guardado)")
        else:
            print(f"Error enrutando {nombre_proceso}")

    def _on_cambio_volumen(self, valor, sesion, label_volumen):
        nivel = float(valor) / 100
        cambiar_volumen(sesion, nivel)
        label_volumen.configure(text=f"{int(float(valor))}%")

    def _verificar_sesiones_nuevas(self):
        procesos_actuales = set()
        for sesion in listar_sesiones():
            if sesion.Process:
                procesos_actuales.add(sesion.Process.name())

        nuevos = procesos_actuales - self.procesos_conocidos

        if nuevos:
            for proceso in nuevos:
                regla = obtener_regla(proceso)
                if regla:
                    if enrutar_app(proceso, regla["nombre_completo"]):
                        print(f"[auto] {proceso} -> {regla['nombre_amigable']}")
            self.actualizar()
        elif procesos_actuales != self.procesos_conocidos:
            self.actualizar()

        self.after(INTERVALO_MONITOREO_MS, self._verificar_sesiones_nuevas)


def iniciar():
    VentanaPrincipal().mainloop()