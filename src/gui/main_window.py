import tkinter as tk
from tkinter import ttk

from audio.sessions import listar_sesiones
from audio.routing import listar_dispositivos_salida, enrutar_app


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Proyecto_Audio - Enrutador por app")
        self.geometry("500x400")

        self.dispositivos = []       # última lista de dispositivos cargada
        self.filas = {}              # proceso -> combobox

        self._construir_interfaz()
        self.actualizar()

    def _construir_interfaz(self):
        boton_actualizar = ttk.Button(self, text="Actualizar", command=self.actualizar)
        boton_actualizar.pack(pady=8)

        self.contenedor = ttk.Frame(self)
        self.contenedor.pack(fill="both", expand=True, padx=10, pady=10)

    def actualizar(self):
        # Tkinter no tiene "refrescar la lista sola": hay que borrar
        # los widgets viejos y crear los nuevos a mano.
        for widget in self.contenedor.winfo_children():
            widget.destroy()
        self.filas.clear()

        self.dispositivos = listar_dispositivos_salida()
        nombres_dispositivos = [d["nombre_amigable"] for d in self.dispositivos]

        procesos_vistos = set()
        for sesion in listar_sesiones():
            if not sesion.Process:
                continue
            nombre_proceso = sesion.Process.name()
            if nombre_proceso in procesos_vistos:
                continue  # una app puede tener más de una sesión
            procesos_vistos.add(nombre_proceso)

            fila = ttk.Frame(self.contenedor)
            fila.pack(fill="x", pady=4)

            ttk.Label(fila, text=nombre_proceso, width=25).pack(side="left")

            combo = ttk.Combobox(fila, values=nombres_dispositivos, state="readonly")
            combo.pack(side="left", fill="x", expand=True)
            combo.bind(
                "<<ComboboxSelected>>",
                lambda evento, proceso=nombre_proceso, c=combo: self._on_seleccion(proceso, c)
            )

            self.filas[nombre_proceso] = combo

    def _on_seleccion(self, nombre_proceso, combo):
        indice = combo.current()
        if indice < 0:
            return
        dispositivo = self.dispositivos[indice]
        if enrutar_app(nombre_proceso, dispositivo["nombre_completo"]):
            print(f"{nombre_proceso} -> {dispositivo['nombre_amigable']}")
        else:
            print(f"Error enrutando {nombre_proceso}")


def iniciar():
    VentanaPrincipal().mainloop()