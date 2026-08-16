import tkinter as tk
from tkinter import ttk

from audio.sessions import listar_sesiones
from audio.routing import listar_dispositivos_salida, enrutar_app
from audio.volume import obtener_volumen, cambiar_volumen
from audio.app_info import obtener_nombres_amigables, nombre_para_mostrar
from storage.rules import guardar_regla, obtener_regla

INTERVALO_MONITOREO_MS = 3000  # cada cuánto revisar si hay apps nuevas


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto_Audio")
        self.geometry("640x420")
        self.minsize(520, 300)

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Encabezado.TLabel", font=("Segoe UI", 10, "bold"))
        estilo.configure("App.TLabel", font=("Segoe UI", 10))

        self.dispositivos = []
        self.filas = {}                  # proceso -> info de la fila
        self.procesos_conocidos = set()  # snapshot para detectar apps nuevas

        self._construir_interfaz()
        self.actualizar()
        self._verificar_sesiones_nuevas()

    def _construir_interfaz(self):
        barra_superior = ttk.Frame(self)
        barra_superior.pack(fill="x", padx=10, pady=8)
        ttk.Label(barra_superior, text="Proyecto_Audio", style="Encabezado.TLabel").pack(side="left")
        ttk.Button(barra_superior, text="Actualizar", command=self.actualizar).pack(side="right")

        encabezado = ttk.Frame(self)
        encabezado.pack(fill="x", padx=10)
        ttk.Label(encabezado, text="Aplicación", width=18, style="Encabezado.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(encabezado, text="Dispositivo de salida", style="Encabezado.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(encabezado, text="Volumen", style="Encabezado.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=(4, 0))

        # Zona con scroll, por si hay muchas apps sonando a la vez
        zona_scroll = ttk.Frame(self)
        zona_scroll.pack(fill="both", expand=True, padx=10, pady=6)

        self.canvas = tk.Canvas(zona_scroll, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(zona_scroll, orient="vertical", command=self.canvas.yview)
        self.contenedor = ttk.Frame(self.canvas)

        self.contenedor.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.contenedor, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Permite hacer scroll con la rueda del mouse estando sobre la ventana
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

    def actualizar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.filas.clear()

        self.dispositivos = listar_dispositivos_salida()
        nombres_dispositivos = [d["nombre_amigable"] for d in self.dispositivos]
        nombres_amigables = obtener_nombres_amigables()

        procesos_vistos = set()
        for sesion in listar_sesiones():
            if not sesion.Process:
                continue
            nombre_proceso = sesion.Process.name()
            if nombre_proceso in procesos_vistos:
                continue  # una app puede tener más de una sesión
            procesos_vistos.add(nombre_proceso)

            texto_mostrado = nombre_para_mostrar(nombre_proceso, nombres_amigables)

            fila = ttk.Frame(self.contenedor)
            fila.pack(fill="x", pady=3)

            ttk.Label(fila, text=texto_mostrado, width=18, style="App.TLabel").pack(side="left")

            combo = ttk.Combobox(fila, values=nombres_dispositivos, state="readonly", width=26)
            combo.pack(side="left", padx=(0, 10))

            regla = obtener_regla(nombre_proceso)
            if regla and regla["nombre_amigable"] in nombres_dispositivos:
                combo.set(regla["nombre_amigable"])

            combo.bind(
                "<<ComboboxSelected>>",
                lambda evento, proceso=nombre_proceso, c=combo: self._on_seleccion(proceso, c)
            )

            try:
                volumen_actual = int(obtener_volumen(sesion) * 100)
            except OSError:
                volumen_actual = 100

            label_volumen = ttk.Label(fila, text=f"{volumen_actual}%", width=4)

            # Ojo con el orden acá: creamos el slider SIN "command" todavía,
            # le seteamos el valor inicial, y RECIÉN AHÍ conectamos el
            # callback. Si conectás el callback antes de .set(), Tkinter lo
            # dispara igual al setear el valor inicial, y terminarías
            # llamando a cambiar_volumen() en cada refresco sin necesidad.
            slider = ttk.Scale(fila, from_=0, to=100, orient="horizontal", length=120)
            slider.set(volumen_actual)
            slider.configure(
                command=lambda valor, s=sesion, lbl=label_volumen: self._on_cambio_volumen(valor, s, lbl)
            )
            slider.pack(side="left")
            label_volumen.pack(side="left", padx=(6, 0))

            self.filas[nombre_proceso] = {"combo": combo, "sesion": sesion}

        self.procesos_conocidos = procesos_vistos

    def _on_seleccion(self, nombre_proceso, combo):
        indice = combo.current()
        if indice < 0:
            return
        dispositivo = self.dispositivos[indice]
        if enrutar_app(nombre_proceso, dispositivo["nombre_completo"]):
            guardar_regla(nombre_proceso, dispositivo["nombre_completo"], dispositivo["nombre_amigable"])
            print(f"{nombre_proceso} -> {dispositivo['nombre_amigable']} (guardado)")
        else:
            print(f"Error enrutando {nombre_proceso}")

    def _on_cambio_volumen(self, valor, sesion, label_volumen):
        nivel = float(valor) / 100
        cambiar_volumen(sesion, nivel)
        label_volumen.config(text=f"{int(float(valor))}%")

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