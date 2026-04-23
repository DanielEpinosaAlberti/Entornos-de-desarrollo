import tkinter as tk
from tkinter import messagebox, ttk
import time
import json
from concurrent.futures import ThreadPoolExecutor
from no_opt import obtener_datos_no_opt
from opt import obtener_datos_opt
from profiler_utils import profile_function

UPDATE_INTERVAL = 3000  # ms
PROFILE_EVERY = 2


class App:
    """
    Aplicación principal con dos paneles:
    - No optimizado
    - Optimizado
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Rendimiento | ISS")
        self.root.geometry("1200x740")
        self.root.minsize(980, 620)
        self.root.state("zoomed")
        self.root.configure(bg="#0f172a")

        self.max_seen_time = 0.0001
        self.panels = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.resize_after_id = None
        self.history_limit = 30
        self.history = {
            "NO OPTIMIZADO": {"time": [], "lat": []},
            "OPTIMIZADO": {"time": [], "lat": []}
        }
        self.palette = {
            "NO OPTIMIZADO": "#fb923c",
            "OPTIMIZADO": "#34d399"
        }

        self._setup_styles()
        self._build_layout()
        self._bind_close_handler()

        self.setup_panel(self.left_panel, "NO OPTIMIZADO", "#f97316", obtener_datos_no_opt)
        self.setup_panel(self.right_panel, "OPTIMIZADO", "#22c55e", obtener_datos_opt)

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "Main.TFrame",
            background="#0f172a"
        )
        style.configure(
            "Card.TFrame",
            background="#111827"
        )
        style.configure(
            "HeaderTitle.TLabel",
            background="#0f172a",
            foreground="#e2e8f0",
            font=("Bahnschrift SemiBold", 24)
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background="#0f172a",
            foreground="#94a3b8",
            font=("Bahnschrift", 11)
        )
        style.configure(
            "SectionTitle.TLabel",
            background="#111827",
            foreground="#f8fafc",
            font=("Bahnschrift SemiBold", 12)
        )
        style.configure(
            "Value.TLabel",
            background="#111827",
            foreground="#cbd5e1",
            font=("Consolas", 11)
        )
        style.configure(
            "Action.TButton",
            font=("Bahnschrift SemiBold", 10),
            padding=(14, 8),
            foreground="#e2e8f0",
            background="#334155"
        )
        style.map(
            "Action.TButton",
            background=[("active", "#475569")]
        )
        style.configure(
            "ChartCard.TFrame",
            background="#0b1220"
        )
        style.configure(
            "ChartTitle.TLabel",
            background="#0b1220",
            foreground="#dbeafe",
            font=("Bahnschrift SemiBold", 11)
        )
        style.configure(
            "Legend.TLabel",
            background="#0b1220",
            foreground="#93c5fd",
            font=("Bahnschrift", 10)
        )

    def _build_layout(self):
        main = ttk.Frame(self.root, style="Main.TFrame", padding=18)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=0)
        main.rowconfigure(1, weight=5)
        main.rowconfigure(2, weight=3)
        main.rowconfigure(3, weight=0)

        header = ttk.Frame(main, style="Main.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Comparación Visual de Optimización", style="HeaderTitle.TLabel").pack(anchor="w")
        self.subtitle_label = ttk.Label(
            header,
            text="Monitoreo en vivo de latitudes ISS, tiempo de ejecución y profiling (actualiza cada 3 segundos).",
            style="HeaderSubtitle.TLabel"
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0), fill="x")

        container = ttk.Frame(main, style="Main.TFrame")
        container.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self.left_panel = ttk.Frame(container, style="Card.TFrame", padding=16)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.right_panel = ttk.Frame(container, style="Card.TFrame", padding=16)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.charts_section = ttk.Frame(main, style="Main.TFrame")
        self.charts_section.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self.charts_section.columnconfigure(0, weight=1)
        self.charts_section.columnconfigure(1, weight=1)
        self.charts_section.rowconfigure(0, weight=1)

        self.time_chart_card = ttk.Frame(self.charts_section, style="ChartCard.TFrame", padding=12)
        self.time_chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.time_chart_card.columnconfigure(0, weight=1)
        self.time_chart_card.rowconfigure(1, weight=1)
        ttk.Label(self.time_chart_card, text="Grafico de Tiempo (ms)", style="ChartTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.time_canvas = tk.Canvas(self.time_chart_card, bg="#0b1220", highlightthickness=0)
        self.time_canvas.grid(row=1, column=0, sticky="nsew", pady=(6, 4))
        ttk.Label(self.time_chart_card, text="Naranja: no optimizado | Verde: optimizado", style="Legend.TLabel").grid(row=2, column=0, sticky="w")

        self.lat_chart_card = ttk.Frame(self.charts_section, style="ChartCard.TFrame", padding=12)
        self.lat_chart_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.lat_chart_card.columnconfigure(0, weight=1)
        self.lat_chart_card.rowconfigure(1, weight=1)
        ttk.Label(self.lat_chart_card, text="Grafico de Latitud Promedio", style="ChartTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.lat_canvas = tk.Canvas(self.lat_chart_card, bg="#0b1220", highlightthickness=0)
        self.lat_canvas.grid(row=1, column=0, sticky="nsew", pady=(6, 4))
        ttk.Label(self.lat_chart_card, text="Evolucion de promedio_lat por ciclo", style="Legend.TLabel").grid(row=2, column=0, sticky="w")

        self.status_var = tk.StringVar(value="Inicializando paneles...")
        status = ttk.Label(main, textvariable=self.status_var, style="HeaderSubtitle.TLabel")
        status.grid(row=3, column=0, sticky="w", pady=(2, 0))
        self.root.after(120, self._refresh_charts)

    def _bind_close_handler(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self._on_resize)

    def _on_resize(self, _event):
        # Ajusta el wrapping del subtítulo para que no se corte en cambios de tamaño.
        width = max(500, self.root.winfo_width() - 80)
        self.subtitle_label.configure(wraplength=width)
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        self.resize_after_id = self.root.after(140, self._refresh_charts)

    def _append_history(self, title, elapsed, avg):
        item = self.history[title]
        item["time"].append(elapsed * 1000)
        item["lat"].append(avg)
        if len(item["time"]) > self.history_limit:
            item["time"] = item["time"][-self.history_limit:]
            item["lat"] = item["lat"][-self.history_limit:]

    def _draw_chart(self, canvas, series_data, y_label):
        canvas.delete("all")
        width = max(220, canvas.winfo_width())
        height = max(150, canvas.winfo_height())
        canvas.create_rectangle(0, 0, width, height, fill="#0b1220", outline="")

        left_pad = 36
        right_pad = 12
        top_pad = 14
        bottom_pad = 24
        plot_w = width - left_pad - right_pad
        plot_h = height - top_pad - bottom_pad
        if plot_w <= 10 or plot_h <= 10:
            return

        all_values = []
        for values, _ in series_data:
            all_values.extend(values)
        if not all_values:
            canvas.create_text(width / 2, height / 2, text="Esperando datos...", fill="#64748b", font=("Bahnschrift", 10))
            return

        min_v = min(all_values)
        max_v = max(all_values)
        if abs(max_v - min_v) < 1e-9:
            max_v = min_v + 1.0

        for i in range(5):
            y = top_pad + (plot_h * i / 4)
            canvas.create_line(left_pad, y, width - right_pad, y, fill="#1e293b", width=1)

        canvas.create_line(left_pad, top_pad, left_pad, height - bottom_pad, fill="#334155", width=1)
        canvas.create_line(left_pad, height - bottom_pad, width - right_pad, height - bottom_pad, fill="#334155", width=1)
        canvas.create_text(8, top_pad - 2, text=y_label, anchor="nw", fill="#94a3b8", font=("Bahnschrift", 9))

        for values, color in series_data:
            if len(values) < 2:
                continue
            count = len(values)
            points = []
            for idx, value in enumerate(values):
                x = left_pad + (idx / (count - 1)) * plot_w
                y_ratio = (value - min_v) / (max_v - min_v)
                y = height - bottom_pad - (y_ratio * plot_h)
                points.extend((x, y))
            canvas.create_line(points, fill=color, width=2.6, smooth=True)

        canvas.create_text(
            width - right_pad,
            top_pad,
            text=f"max {max_v:.2f}",
            anchor="ne",
            fill="#94a3b8",
            font=("Bahnschrift", 9)
        )
        canvas.create_text(
            width - right_pad,
            height - bottom_pad + 2,
            text=f"min {min_v:.2f}",
            anchor="ne",
            fill="#94a3b8",
            font=("Bahnschrift", 9)
        )

    def _refresh_charts(self):
        self.resize_after_id = None
        time_series = [
            (self.history["NO OPTIMIZADO"]["time"], self.palette["NO OPTIMIZADO"]),
            (self.history["OPTIMIZADO"]["time"], self.palette["OPTIMIZADO"]),
        ]
        lat_series = [
            (self.history["NO OPTIMIZADO"]["lat"], self.palette["NO OPTIMIZADO"]),
            (self.history["OPTIMIZADO"]["lat"], self.palette["OPTIMIZADO"]),
        ]
        self._draw_chart(self.time_canvas, time_series, "ms")
        self._draw_chart(self.lat_canvas, lat_series, "lat")

    def _make_text_box(self, parent, height=7):
        box = tk.Text(
            parent,
            height=height,
            bg="#0b1220",
            fg="#dbeafe",
            insertbackground="#dbeafe",
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
            font=("Consolas", 10),
            wrap="word"
        )
        box.configure(state="disabled")
        return box

    def _set_text(self, widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def setup_panel(self, frame, title, accent_color, func):
        """
        Configura un panel visual con métricas, datos y acciones.
        """
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=0)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=0)
        frame.rowconfigure(4, weight=3)
        frame.rowconfigure(5, weight=0)
        frame.rowconfigure(6, weight=2)
        frame.rowconfigure(7, weight=0)

        title_row = ttk.Frame(frame, style="Card.TFrame")
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        badge = tk.Canvas(title_row, width=12, height=12, bg="#111827", highlightthickness=0)
        badge.create_oval(1, 1, 11, 11, fill=accent_color, outline=accent_color)
        badge.pack(side="left", padx=(0, 8))
        ttk.Label(title_row, text=title, style="SectionTitle.TLabel").pack(side="left")

        metrics_frame = ttk.Frame(frame, style="Card.TFrame")
        metrics_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        avg_label = ttk.Label(metrics_frame, text="Promedio lat: --", style="Value.TLabel")
        avg_label.pack(anchor="w")

        time_label = ttk.Label(metrics_frame, text="Tiempo: --", style="Value.TLabel")
        time_label.pack(anchor="w", pady=(2, 0))

        updated_label = ttk.Label(metrics_frame, text="Actualizado: --", style="Value.TLabel")
        updated_label.pack(anchor="w", pady=(2, 0))

        progress = ttk.Progressbar(metrics_frame, mode="determinate", maximum=100)
        progress.pack(fill="x", pady=(8, 0))

        speed_chip = tk.Label(
            frame,
            text="Estado: esperando muestra...",
            bg="#1e293b",
            fg="#bfdbfe",
            padx=10,
            pady=5,
            font=("Bahnschrift", 10)
        )
        speed_chip.grid(row=2, column=0, sticky="w", pady=(0, 10))

        ttk.Label(frame, text="Datos", style="SectionTitle.TLabel").grid(row=3, column=0, sticky="w")
        data_box = self._make_text_box(frame, height=8)
        data_box.grid(row=4, column=0, sticky="nsew", pady=(4, 10))

        ttk.Label(frame, text="Top Profiling", style="SectionTitle.TLabel").grid(row=5, column=0, sticky="w")
        profile_box = self._make_text_box(frame, height=6)
        profile_box.grid(row=6, column=0, sticky="nsew", pady=(4, 12))

        actions = ttk.Frame(frame, style="Card.TFrame")
        actions.grid(row=7, column=0, sticky="ew")
        ttk.Button(actions, text="Help", style="Action.TButton", command=lambda: self.show_help(func)).pack(side="left")
        ttk.Button(
            actions,
            text="Actualizar ahora",
            style="Action.TButton",
            command=lambda f=func: self.update_data(f, force=True)
        ).pack(side="left", padx=8)

        self.panels[func] = {
            "avg_label": avg_label,
            "time_label": time_label,
            "updated_label": updated_label,
            "progress": progress,
            "speed_chip": speed_chip,
            "data_box": data_box,
            "profile_box": profile_box,
            "after_id": None,
            "poll_id": None,
            "future": None,
            "refresh_count": 0,
            "title": title
        }

        self.update_data(func)

    def update_data(self, func, force=False):
        """
        Programa la actualización sin bloquear la UI.
        """
        panel = self.panels[func]

        if force and panel["after_id"]:
            self.root.after_cancel(panel["after_id"])
            panel["after_id"] = None
        if force and panel["poll_id"]:
            self.root.after_cancel(panel["poll_id"])
            panel["poll_id"] = None

        future = panel.get("future")
        if future and not future.done():
            self.status_var.set(f"Actualización en curso en panel '{panel['title']}'...")
            if panel["after_id"] is None:
                panel["after_id"] = self.root.after(
                    UPDATE_INTERVAL,
                    lambda f=func: self.update_data(f)
                )
            return

        panel["refresh_count"] += 1
        should_profile = (panel["refresh_count"] % PROFILE_EVERY) == 0
        panel["future"] = self.executor.submit(self._fetch_panel_data, func, should_profile)
        self._poll_panel_future(func)

    def _fetch_panel_data(self, func, should_profile):
        start = time.perf_counter()
        if should_profile:
            result, profile_info = profile_function(func)
        else:
            result = func()
            profile_info = "Profiling omitido en este ciclo para mantener fluidez."
        elapsed = time.perf_counter() - start
        return result, profile_info, elapsed

    def _poll_panel_future(self, func):
        panel = self.panels[func]
        future = panel.get("future")
        if future is None:
            return

        if not future.done():
            panel["poll_id"] = self.root.after(80, lambda f=func: self._poll_panel_future(f))
            return

        panel["poll_id"] = None

        try:
            result, profile_info, elapsed = future.result()

            self.max_seen_time = max(self.max_seen_time, elapsed)
            normalized = min(100, (elapsed / self.max_seen_time) * 100)

            avg = result.get("promedio_lat", 0)
            data_text = json.dumps(result.get("datos", []), indent=2, ensure_ascii=False)
            now = time.strftime("%H:%M:%S")

            panel["avg_label"].config(text=f"Promedio lat: {avg:.6f}")
            panel["time_label"].config(text=f"Tiempo: {elapsed:.5f}s")
            panel["updated_label"].config(text=f"Actualizado: {now}")
            panel["progress"]["value"] = normalized
            panel["speed_chip"].config(
                text=f"Rendimiento: {elapsed * 1000:.1f} ms",
                fg="#dcfce7" if panel["title"] == "OPTIMIZADO" else "#ffedd5"
            )
            self._set_text(panel["data_box"], data_text)
            self._set_text(panel["profile_box"], profile_info.strip())
            self._append_history(panel["title"], elapsed, float(avg))
            self._refresh_charts()
            self.status_var.set(f"Actualización correcta en panel '{panel['title']}' ({now}).")
        except Exception as exc:
            now = time.strftime("%H:%M:%S")
            panel["time_label"].config(text="Tiempo: error")
            panel["updated_label"].config(text=f"Actualizado: {now}")
            panel["progress"]["value"] = 0
            panel["speed_chip"].config(text="Rendimiento: error de consulta", fg="#fecaca")
            self._set_text(panel["data_box"], "No se pudieron obtener datos.")
            self._set_text(panel["profile_box"], f"Error: {exc}")
            self.status_var.set(f"Error en panel '{panel['title']}': {exc}")
        finally:
            panel["future"] = None

        panel["after_id"] = self.root.after(
            UPDATE_INTERVAL,
            lambda f=func: self.update_data(f)
        )

    def show_help(self, func):
        """
        Muestra docstring de la función.
        """
        messagebox.showinfo("Help", func.__doc__ or "Sin documentación disponible.")

    def on_close(self):
        if self.resize_after_id:
            self.root.after_cancel(self.resize_after_id)
        for panel in self.panels.values():
            after_id = panel.get("after_id")
            if after_id:
                self.root.after_cancel(after_id)
            poll_id = panel.get("poll_id")
            if poll_id:
                self.root.after_cancel(poll_id)
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()