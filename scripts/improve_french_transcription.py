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
OUTPUT_TXT = Path("feht-ychebnik-Valvil-19v.fr.cleaned.txt")
OUTPUT_PDF = Path("feht-ychebnik-Valvil-19v.fr.cleaned.pdf")

CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
ALPHA_RE = re.compile(r"[A-Za-zÀ-ÿ]")
SPACE_RE = re.compile(r"\s+")
PUNCT_ONLY_RE = re.compile(r"^[,.'`´-]+$")
PAGE_MARKER_RE = re.compile(r"^\[Page (\d+)\]$")


def normalize_fragment(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = SPACE_RE.sub(" ", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace(" ;", ";").replace(" :", ":")
    text = text.replace(" !", "!").replace(" ?", "?")
    text = text.replace("( ", "(").replace(" )", ")")
    return text.strip()


def merge_hyphenated_lines(lines: list[str]) -> list[str]:
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

    return merge_hyphenated_lines(lines)


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

    page_lines: list[str] = []
    for bucket in (header, left_column, right_column):
        page_lines.extend(bucket_to_lines(bucket))

    page_lines = [line for line in page_lines if not PUNCT_ONLY_RE.match(line)]
    page_text = "\n".join(page_lines).strip()

    if len(ALPHA_RE.findall(page_text)) < 120:
        return ""

    return page_text


def should_start_new_paragraph(line: str) -> bool:
    upper = line.upper()
    return (
        upper.startswith("ARTICLE ")
        or upper.startswith("P L A N")
        or upper.startswith("DES ")
        or upper.startswith("DE LA ")
        or upper.startswith("IL NE ")
        or upper.startswith("LE SOLDAT ")
        or upper.startswith("DE CETTE ")
    )


def build_paragraphs(page_text: str) -> list[str]:
    raw_lines = [line.strip() for line in page_text.splitlines() if line.strip()]
    paragraphs: list[str] = []

    for line in raw_lines:
        if PUNCT_ONLY_RE.match(line):
            continue
        if re.fullmatch(r"[0-9IVXLCDM oO]+", line):
            continue

        if not paragraphs:
            paragraphs.append(line)
            continue

        previous = paragraphs[-1]
        if (
            previous.endswith((".", "!", "?", ":"))
            or should_start_new_paragraph(line)
            or line[:1].isupper() and previous.endswith(",")
        ):
            paragraphs.append(line)
        else:
            paragraphs[-1] = f"{previous} {line}"

    cleaned: list[str] = []
    for paragraph in paragraphs:
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        paragraph = paragraph.replace(" ,", ",").replace(" .", ".")
        paragraph = paragraph.replace(" ;", ";").replace(" :", ":")
        cleaned.append(paragraph)

    return cleaned


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
        pdfmetrics.registerFont(TTFont("ArialCustom", str(arial_path)))
        font_name = "ArialCustom"

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setTitle("Transcription francaise amelioree - feht-ychebnik-Valvil-19v")

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
    page_blocks: list[str] = []

    for index, page in enumerate(reader.pages, start=1):
        page_text = extract_french_page(page)
        if not page_text:
            continue

        paragraphs = build_paragraphs(page_text)
        if not paragraphs:
            continue

        block = "\n".join([f"[Page {index}]"] + paragraphs)
        page_blocks.append(block)

    final_text = "\n\n".join(page_blocks).strip()
    OUTPUT_TXT.write_text(final_text, encoding="utf-8")
    write_pdf(final_text, OUTPUT_PDF)

    print(OUTPUT_TXT)
    print(OUTPUT_PDF)
    print(f"pages kept: {len(page_blocks)}")


if __name__ == "__main__":
    main()
