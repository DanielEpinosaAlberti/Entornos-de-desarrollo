import tkinter as tk
from pathlib import Path

import pytest

from operaciones import division, multiplicacion, resta, suma


class ResultadoPlugin:
    def __init__(self):
        self.resultados = []

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            nombre = report.nodeid.split("::")[-1].replace("test_", "")
            self.resultados.append((nombre, report.passed))


class CalculadoraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de escritorio")
        self.root.configure(bg="#f4f1ea")
        self.operacion_actual = None
        self.botones_operacion = {}

        self.colores = {
            "fondo": "#f4f1ea",
            "panel": "#fffdf8",
            "texto": "#1f1f1f",
            "subtexto": "#5b5b5b",
            "acento": "#c0622b",
            "acento_oscuro": "#9f4a1d",
            "exito": "#1f7a3d",
            "error": "#b42318",
            "linea": "#e5dac9",
        }

        self.valor_a = tk.StringVar()
        self.valor_b = tk.StringVar()
        self.resultado = tk.StringVar(value="Resultado: ")
        self.historial = []

        self._construir_interfaz()

    def _construir_interfaz(self):
        frame = tk.Frame(self.root, bg=self.colores["fondo"], padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Calculadora básica",
            bg=self.colores["fondo"],
            fg=self.colores["texto"],
            font=("Bahnschrift SemiBold", 20),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            frame,
            text="Operaciones y pruebas unitarias en una sola vista",
            bg=self.colores["fondo"],
            fg=self.colores["subtexto"],
            font=("Consolas", 10),
        ).grid(row=1, column=0, sticky="w", pady=(2, 10))

        panel = tk.Frame(
            frame,
            bg=self.colores["panel"],
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground=self.colores["linea"],
            padx=12,
            pady=12,
        )
        panel.grid(row=2, column=0, sticky="nsew")

        tk.Label(panel, text="Número A", bg=self.colores["panel"], fg=self.colores["texto"], font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.entry_a = tk.Entry(panel, textvariable=self.valor_a, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_a.grid(row=0, column=1, sticky="ew")

        tk.Label(panel, text="Número B", bg=self.colores["panel"], fg=self.colores["texto"], font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.entry_b = tk.Entry(panel, textvariable=self.valor_b, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_b.grid(row=1, column=1, sticky="ew", pady=(10, 0))

        botones = tk.Frame(panel, bg=self.colores["panel"])
        botones.grid(row=2, column=0, columnspan=2, pady=(14, 10), sticky="ew")

        self.botones_operacion["+"] = tk.Button(botones, text="+", width=6, font=("Segoe UI", 10, "bold"), command=lambda: self._seleccionar_operacion("+"))
        self.botones_operacion["-"] = tk.Button(botones, text="-", width=6, font=("Segoe UI", 10, "bold"), command=lambda: self._seleccionar_operacion("-"))
        self.botones_operacion["*"] = tk.Button(botones, text="×", width=6, font=("Segoe UI", 10, "bold"), command=lambda: self._seleccionar_operacion("*"))
        self.botones_operacion["/"] = tk.Button(botones, text="÷", width=6, font=("Segoe UI", 10, "bold"), command=lambda: self._seleccionar_operacion("/"))

        for indice, operacion in enumerate(["+", "-", "*", "/"]):
            boton = self.botones_operacion[operacion]
            boton.grid(row=0, column=indice, padx=4)

        self._aplicar_estilo_operaciones()

        tk.Button(
            panel,
            text="Calcular =",
            command=self.calcular,
            bg=self.colores["acento"],
            fg="white",
            activebackground=self.colores["acento_oscuro"],
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=8,
            pady=6,
        ).grid(row=3, column=0, columnspan=2, sticky="ew")

        self.entry_a.bind("<Return>", self._calcular_con_evento)
        self.entry_b.bind("<Return>", self._calcular_con_evento)
        self.root.bind("<KP_Enter>", self._calcular_con_evento)

        self.lbl_resultado = tk.Label(
            panel,
            textvariable=self.resultado,
            bg=self.colores["panel"],
            fg=self.colores["texto"],
            font=("Consolas", 11, "bold"),
            anchor="w",
        )
        self.lbl_resultado.grid(row=4, column=0, columnspan=2, pady=(10, 6), sticky="ew")

        acciones = tk.Frame(panel, bg=self.colores["panel"])
        acciones.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        acciones.grid_columnconfigure(0, weight=1)
        acciones.grid_columnconfigure(1, weight=1)

        tk.Button(
            acciones,
            text="Pruebas",
            command=self.ejecutar_pruebas,
            bg="#2d6a4f",
            fg="white",
            activebackground="#1f513b",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=8,
            pady=6,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        tk.Button(
            acciones,
            text="Limpiar",
            command=self.limpiar,
            bg="#8d5524",
            fg="white",
            activebackground="#734118",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            bd=0,
            padx=8,
            pady=6,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        self.salida_pruebas = tk.Text(
            panel,
            height=8,
            width=46,
            bg="#fffaf2",
            fg=self.colores["texto"],
            insertbackground=self.colores["texto"],
            font=("Consolas", 10),
            bd=1,
            relief="solid",
            padx=8,
            pady=8,
        )
        self.salida_pruebas.grid(row=6, column=0, columnspan=2, pady=(8, 0), sticky="nsew")

        tk.Label(
            panel,
            text="Historial de operaciones",
            bg=self.colores["panel"],
            fg=self.colores["subtexto"],
            font=("Segoe UI", 9, "bold"),
        ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 2))

        self.lista_historial = tk.Listbox(
            panel,
            height=5,
            bg="#fffaf2",
            fg=self.colores["texto"],
            font=("Consolas", 10),
            bd=1,
            relief="solid",
            activestyle="none",
        )
        self.lista_historial.grid(row=8, column=0, columnspan=2, sticky="nsew")

        self.salida_pruebas.tag_config("ok", foreground=self.colores["exito"])
        self.salida_pruebas.tag_config("ko", foreground=self.colores["error"])
        self.salida_pruebas.tag_config("resumen", foreground=self.colores["texto"], font=("Consolas", 10, "bold"))

        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(6, weight=1)
        panel.grid_rowconfigure(8, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _calcular_con_evento(self, _event):
        self.calcular()

    def _aplicar_estilo_operaciones(self):
        for operacion, boton in self.botones_operacion.items():
            if operacion == self.operacion_actual:
                boton.configure(
                    bg=self.colores["acento"],
                    fg="white",
                    activebackground=self.colores["acento_oscuro"],
                    activeforeground="white",
                    relief="sunken",
                    bd=1,
                )
            else:
                boton.configure(
                    bg="#f1e8dc",
                    fg=self.colores["texto"],
                    activebackground="#e8dac7",
                    activeforeground=self.colores["texto"],
                    relief="raised",
                    bd=1,
                )

    def _seleccionar_operacion(self, operacion):
        self.operacion_actual = operacion
        self._aplicar_estilo_operaciones()
        self.resultado.set(f"Operación seleccionada: {operacion}")
        self.lbl_resultado.configure(fg=self.colores["texto"])

    def calcular(self):
        try:
            a = float(self.valor_a.get())
            b = float(self.valor_b.get())
        except ValueError:
            self.resultado.set("Error: introduce números válidos")
            self.lbl_resultado.configure(fg=self.colores["error"])
            return

        if self.operacion_actual == "+":
            valor = suma(a, b)
        elif self.operacion_actual == "-":
            valor = resta(a, b)
        elif self.operacion_actual == "*":
            valor = multiplicacion(a, b)
        elif self.operacion_actual == "/":
            try:
                valor = division(a, b)
            except ValueError as exc:
                self.resultado.set(f"Error: {exc}")
                self.lbl_resultado.configure(fg=self.colores["error"])
                return
        else:
            self.resultado.set("Selecciona una operación")
            self.lbl_resultado.configure(fg=self.colores["error"])
            return

        self.resultado.set(f"Resultado: {valor:g}")
        self.lbl_resultado.configure(fg=self.colores["exito"])
        self._registrar_historial(a, b, valor)

    def _registrar_historial(self, a, b, valor):
        simbolos = {"+": "+", "-": "-", "*": "×", "/": "÷"}
        simbolo = simbolos.get(self.operacion_actual, "?")
        registro = f"{a:g} {simbolo} {b:g} = {valor:g}"
        self.historial.append(registro)
        self.lista_historial.insert(tk.END, registro)
        self.lista_historial.see(tk.END)

    def limpiar(self):
        self.valor_a.set("")
        self.valor_b.set("")
        self.operacion_actual = None
        self._aplicar_estilo_operaciones()
        self.resultado.set("Resultado: ")
        self.lbl_resultado.configure(fg=self.colores["texto"])
        self.salida_pruebas.delete("1.0", tk.END)
        self.lista_historial.delete(0, tk.END)
        self.historial.clear()
        self.entry_a.focus_set()

    def ejecutar_pruebas(self):
        self.salida_pruebas.delete("1.0", tk.END)

        plugin = ResultadoPlugin()
        test_file = Path(__file__).with_name("test_operaciones.py")
        pytest.main([str(test_file), "-q"], plugins=[plugin])

        total = len(plugin.resultados)
        correctas = 0

        for nombre, ok in plugin.resultados:
            etiqueta = nombre.replace("_", " ")
            if ok:
                self.salida_pruebas.insert(tk.END, f"✔ {etiqueta} correcta\n", "ok")
                correctas += 1
            else:
                self.salida_pruebas.insert(tk.END, f"❌ {etiqueta} fallida\n", "ko")

        self.salida_pruebas.insert(tk.END, f"Resultado: {correctas}/{total} pruebas correctas", "resumen")


def main():
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.minsize(520, 470)
    root.mainloop()


if __name__ == "__main__":
    main()
