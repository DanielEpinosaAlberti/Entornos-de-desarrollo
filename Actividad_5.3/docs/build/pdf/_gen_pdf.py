from pathlib import Path
from html.parser import HTMLParser
from fpdf import FPDF

root = Path(r"c:\DAW\entornos de desarrollo\2º Trimestre\Optimización y documentacion\Actividad_5.3")
html_dir = root / "docs" / "build" / "html"
pdf_dir = root / "docs" / "build" / "pdf"
pdf_dir.mkdir(parents=True, exist_ok=True)
out_file = pdf_dir / "documentacion_proyecto_actividad_5_3.pdf"

files = [
    ("Portada", html_dir / "index.html"),
    ("Arquitectura", html_dir / "arquitectura.html"),
    ("Guia de Uso", html_dir / "uso.html"),
    ("Referencia de Modulos", html_dir / "modulos.html"),
]

class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "nav", "footer"}:
            self.skip = True
        if tag in {"h1", "h2", "h3", "p", "li", "pre", "code", "br", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "footer"}:
            self.skip = False
        if tag in {"h1", "h2", "h3", "p", "li", "pre", "code", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            txt = data.strip()
            if txt:
                self.parts.append(txt)

    def get_text(self):
        text = " ".join(self.parts)
        lines = [" ".join(line.split()) for line in text.split("\n")]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)


def chunk_long_tokens(line: str, size: int = 70) -> str:
    parts = []
    for token in line.split(" "):
        if len(token) <= size:
            parts.append(token)
            continue
        chunked = [token[i:i+size] for i in range(0, len(token), size)]
        parts.append(" ".join(chunked))
    return " ".join(parts)


def normalize_line(line: str) -> str:
    replacements = {
        "•": "-",
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "’": "'",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)
    line = line.encode("latin-1", "ignore").decode("latin-1")
    line = chunk_long_tokens(line)
    return line


pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=12)
pdf.set_left_margin(12)
pdf.set_right_margin(12)

for title, file_path in files:
    if not file_path.exists():
        continue
    parser = VisibleTextParser()
    parser.feed(file_path.read_text(encoding="utf-8", errors="ignore"))
    content = parser.get_text()

    pdf.add_page()
    pdf.set_fill_color(12, 18, 32)
    pdf.rect(0, 0, 210, 24, style="F")
    pdf.set_text_color(230, 240, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(12, 7)
    pdf.cell(0, 8, normalize_line(title))

    pdf.set_text_color(20, 30, 40)
    pdf.set_xy(12, 30)
    pdf.set_font("Helvetica", "", 11)

    for line in content.splitlines():
        safe = normalize_line(line)
        if safe:
            pdf.multi_cell(186, 6, safe)

pdf.output(str(out_file))
print(f"PDF generado: {out_file}")
