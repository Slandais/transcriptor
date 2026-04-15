from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


INPUT_PDF = Path("feht-ychebnik-Valvil-19v.pdf")
OUTPUT_TXT = Path("feht-ychebnik-Valvil-19v.fr.v2.txt")
OUTPUT_PDF = Path("feht-ychebnik-Valvil-19v.fr.v2.pdf")

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
SPACE_RE = re.compile(r"\s+")
ALPHA_RE = re.compile(r"[A-Za-zÀ-ÿ]")
PUNCT_ONLY_RE = re.compile(r"^[,.'`´-]+$")
ROMAN_OR_PAGE_RE = re.compile(r"^[0-9IVXLCDM oO]+$")

REPLACEMENTS = [
    (" lig ne ", " ligne "),
    (" 011 ", " on "),
    (" Iportons ", " portons "),
    (" caries ", " car les "),
    (" I.es ", " Les "),
    (" de- paule", "d'épaule"),
    (" coure ", " court "),
    (" vousportez ", " vous portez "),
    (" quarte les ", " quarte, les "),
    (" au-dessus de la pointe de l'ennemi et ve nant", "au-dessus de la pointe de l'ennemi et venant"),
    (" n'est pas d'autre", " n'y a pas d'autre"),
    (" à l'être ", " à l'être "),
    (" en quarte ongle»", " en quarte, les ongles "),
    (" toutles deux", " tous les deux"),
    (" deflanc", " de flanc"),
    (" dÃ©figurÃ©", " défiguré"),
    (" quarré", " carré"),
    (" gallerie", " galerie"),
    (" connois", " connais"),
    (" vingt deux", " vingt-deux"),
    (" blanchela", " blanche la"),
    (" terribleaprÃ¨s", " terrible après"),
    (" terribleaprès", " terrible après"),
    (" maniÃ¨reque", " manière que"),
    (" manièreque", " manière que"),
    (" jecras", " j'écrase "),
    (" de terns", " de temps"),
    (" mÃ©rae", " même"),
    (" avgnt", " avaient"),
    (" garjle", " garde"),
]


def normalize_fragment(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = SPACE_RE.sub(" ", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace(" ;", ";").replace(" :", ":")
    text = text.replace(" !", "!").replace(" ?", "?")
    text = text.replace("( ", "(").replace(" )", ")")
    return text.strip()


def merge_hyphenated(lines: list[str]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        if not line:
            continue
        if merged and merged[-1].endswith("-"):
            merged[-1] = merged[-1][:-1] + line.lstrip()
        else:
            merged.append(line)
    return merged


def bucket_to_lines(parts: list[tuple[float, float, str]]) -> list[str]:
    lines: list[str] = []
    current_y: float | None = None
    current_parts: list[tuple[float, str]] = []

    for y, x, text in sorted(parts, key=lambda item: (-item[0], item[1])):
        if current_y is None or abs(y - current_y) <= 2.5:
            current_parts.append((x, text))
            if current_y is None:
                current_y = y
        else:
            line = " ".join(piece for _, piece in sorted(current_parts))
            line = normalize_fragment(line)
            if line:
                lines.append(line)
            current_parts = [(x, text)]
            current_y = y

    if current_parts:
        line = " ".join(piece for _, piece in sorted(current_parts))
        line = normalize_fragment(line)
        if line:
            lines.append(line)

    return merge_hyphenated(lines)


def extract_french_page(page) -> str:
    parts: list[tuple[float, float, str]] = []

    def visitor(text, cm, tm, font_dict, font_size):
        x = float(tm[4])
        y = float(tm[5])
        if x >= 380:
            return
        if not text or not text.strip():
            return
        if CYRILLIC_RE.search(text):
            return

        cleaned = normalize_fragment(text)
        if cleaned:
            parts.append((round(y, 1), round(x, 1), cleaned))

    page.extract_text(visitor_text=visitor)
    if not parts:
        return ""

    header = [part for part in parts if part[0] >= 245]
    left_column = [part for part in parts if part[0] < 245 and part[1] < 180]
    right_column = [part for part in parts if part[0] < 245 and 180 <= part[1] < 380]

    lines: list[str] = []
    for bucket in (header, left_column, right_column):
        lines.extend(bucket_to_lines(bucket))

    lines = [line for line in lines if not PUNCT_ONLY_RE.match(line)]
    page_text = "\n".join(lines).strip()
    if len(ALPHA_RE.findall(page_text)) < 120:
        return ""

    return page_text


def cleanup_paragraph(text: str) -> str:
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace(" ;", ";").replace(" :", ":")
    text = text.replace(" ,", ",")
    text = re.sub(r"\s+", " ", text).strip()
    for src, dst in REPLACEMENTS:
        text = text.replace(src, dst)
    text = text.replace("contre - pointe", "contre-pointe")
    text = text.replace("dixseptième", "dix-septième")
    text = text.replace("II n'en existe qu'une", "Il n'en existe qu'une")
    text = text.replace("I] faut", "Il faut")
    text = text.replace("presqu'impossible", "presque impossible")
    text = text.replace("dêtente", "détente")
    text = text.replace("dèfiguré", "défiguré")
    text = text.replace("d'arrèts", "d'arrêts")
    return text


def build_paragraphs(page_number: int, page_text: str) -> list[str]:
    raw_lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    raw_lines = [line for line in raw_lines if not ROMAN_OR_PAGE_RE.match(line)]

    paragraphs: list[str] = []
    for line in raw_lines:
        if PUNCT_ONLY_RE.match(line):
            continue

        if not paragraphs:
            paragraphs.append(line)
            continue

        previous = paragraphs[-1]
        if previous.endswith((".", "!", "?", ":")) or line.startswith(("ARTICLE ", "Des ", "De ", "P L A N")):
            paragraphs.append(line)
        else:
            paragraphs[-1] = f"{previous} {line}"

    paragraphs = [cleanup_paragraph(p) for p in paragraphs if p.strip()]

    # Remove very noisy front-matter blocks while keeping the main treatise.
    if page_number < 6:
        return []

    return paragraphs


def wrap_line(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def write_pdf(text: str, output_path: Path) -> None:
    font_name = "Helvetica"
    arial_path = Path(r"C:\Windows\Fonts\arial.ttf")
    if arial_path.exists():
        pdfmetrics.registerFont(TTFont("ArialCustomV2", str(arial_path)))
        font_name = "ArialCustomV2"

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle("Transcription francaise v2 - feht-ychebnik-Valvil-19v")

    width, height = A4
    left_margin = 18 * mm
    right_margin = 18 * mm
    top_margin = 18 * mm
    bottom_margin = 18 * mm
    font_size = 10
    line_height = 13
    max_width = width - left_margin - right_margin

    y = height - top_margin
    pdf.setFont(font_name, font_size)

    for paragraph in text.splitlines():
        wrapped = wrap_line(paragraph, font_name, font_size, max_width)
        for line in wrapped:
            if y <= bottom_margin:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - top_margin
            pdf.drawString(left_margin, y, line)
            y -= line_height
        y -= line_height / 2

    pdf.save()


def main() -> None:
    reader = PdfReader(str(INPUT_PDF))
    blocks: list[str] = []

    for index, page in enumerate(reader.pages, start=1):
        page_text = extract_french_page(page)
        if not page_text:
            continue

        paragraphs = build_paragraphs(index, page_text)
        if not paragraphs:
            continue

        blocks.append("\n".join([f"[Page {index}]"] + paragraphs))

    final_text = "\n\n".join(blocks).strip()
    OUTPUT_TXT.write_text(final_text, encoding="utf-8")
    write_pdf(final_text, OUTPUT_PDF)

    print(OUTPUT_TXT)
    print(OUTPUT_PDF)
    print(f"pages kept: {len(blocks)}")


if __name__ == "__main__":
    main()
