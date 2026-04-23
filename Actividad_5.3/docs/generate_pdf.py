from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "docs" / "build" / "pdf"
OUTPUT_FILE = OUTPUT_DIR / "documentacion_proyecto_actividad_5_3.pdf"


class ProjectPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 16, style="F")
        self.set_text_color(226, 232, 240)
        self.set_xy(10, 5)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 6, "Actividad 5.3 | Documentacion del Proyecto", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(30, 41, 59)
        # Garantiza que el contenido siempre empiece por debajo de la banda del header.
        self.set_y(22)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 8, f"Pagina {self.page_no()}", align="C")


def add_title(pdf: ProjectPDF, text: str):
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(15, 23, 42)
    pdf.multi_cell(190, 10, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)


def add_subtitle(pdf: ProjectPDF, text: str):
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(190, 8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def add_paragraph(pdf: ProjectPDF, text: str):
    pdf.set_x(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(190, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def add_bullets(pdf: ProjectPDF, items):
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 65, 85)
    for item in items:
        pdf.set_x(10)
        pdf.multi_cell(190, 6, f"- {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf = ProjectPDF(orientation="P", unit="mm", format="A4")
    pdf.set_top_margin(22)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    add_title(pdf, "Documentacion Tecnica del Proyecto")
    add_paragraph(pdf, "Comparador visual de optimizacion con datos en vivo de la ISS")
    add_paragraph(pdf, f"Fecha de generacion: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    add_subtitle(pdf, "1. Descripcion general")
    add_paragraph(
        pdf,
        "Este proyecto implementa una aplicacion de escritorio en Python (Tkinter) "
        "para comparar en tiempo real dos enfoques de procesamiento: uno no optimizado "
        "y otro optimizado. Incluye metricas, profiling y graficos de evolucion.",
    )

    add_subtitle(pdf, "2. Objetivos")
    add_bullets(
        pdf,
        [
            "Comparar rendimiento entre implementaciones.",
            "Visualizar tiempo de ejecucion y latitud promedio.",
            "Mantener interfaz fluida con procesamiento asincrono.",
            "Documentar arquitectura y modulos del sistema.",
        ],
    )

    add_subtitle(pdf, "3. Arquitectura")
    add_paragraph(pdf, "El sistema se divide en cinco modulos principales:")
    add_bullets(
        pdf,
        [
            "main.py: interfaz grafica, layout, actualizaciones periodicas y graficos en Canvas.",
            "api.py: cliente HTTP de posicion ISS con timeout, reintentos y fallback.",
            "no_opt.py: estrategia no optimizada para comparacion.",
            "opt.py: estrategia optimizada con reduccion de I/O remoto.",
            "profiler_utils.py: perfilado con cProfile y resumen de funciones costosas.",
        ],
    )

    add_subtitle(pdf, "4. Flujo de ejecucion")
    add_bullets(
        pdf,
        [
            "La UI programa actualizaciones cada 3 segundos.",
            "Cada panel lanza tareas en segundo plano con ThreadPoolExecutor.",
            "Se actualizan etiquetas, bloque de datos, perfilado y graficos historicos.",
            "El profiling se alterna por ciclos para reducir carga sobre la interfaz.",
        ],
    )

    pdf.add_page()
    add_subtitle(pdf, "5. Requisitos y ejecucion")
    add_bullets(
        pdf,
        [
            "Python 3.10 o superior.",
            "Dependencia: requests.",
            "Ejecucion principal: python main.py",
            "Documentacion HTML: docs/build/html/index.html",
        ],
    )

    add_subtitle(pdf, "6. Modulos y funciones clave")
    add_bullets(
        pdf,
        [
            "api.get_iss_position(retries=2): consulta una posicion ISS con tolerancia a fallo.",
            "no_opt.obtener_datos_no_opt(): referencia de procesamiento no optimizado.",
            "opt.obtener_datos_opt(): flujo optimizado para comparativa.",
            "profiler_utils.profile_function(func): perfilado de funciones.",
            "App.update_data(...) y App._poll_panel_future(...): actualizacion no bloqueante.",
        ],
    )

    add_subtitle(pdf, "7. Mejoras implementadas en la version actual")
    add_bullets(
        pdf,
        [
            "Interfaz responsive para pantalla completa.",
            "Diseno visual modernizado con ttk y tarjetas.",
            "Graficos comparativos en vivo (tiempo y latitud).",
            "Robustez de red con fallback al ultimo valor conocido.",
        ],
    )

    add_subtitle(pdf, "8. Estructura del proyecto")
    add_paragraph(
        pdf,
        "api.py, main.py, no_opt.py, opt.py, profiler_utils.py, docs/ (source y build).",
    )

    add_subtitle(pdf, "9. Observaciones")
    add_paragraph(
        pdf,
        "El PDF se genera automaticamente desde docs/generate_pdf.py. "
        "La documentacion HTML en Sphinx permanece disponible como referencia navegable.",
    )

    pdf.output(str(OUTPUT_FILE))
    print(f"PDF generado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_pdf()
