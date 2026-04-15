from __future__ import annotations

from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def _wrap_line(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        candidate = f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


def write_text_pdf(output_path: Path, text: str, title: str | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    left_margin = 20 * mm
    right_margin = 20 * mm
    top_margin = 20 * mm
    bottom_margin = 20 * mm
    font_name = "Helvetica"
    font_size = 11
    line_height = 15
    max_width = width - left_margin - right_margin

    if title:
        pdf.setTitle(title)

    y = height - top_margin
    pdf.setFont(font_name, font_size)

    for paragraph in text.splitlines():
        wrapped_lines = _wrap_line(paragraph, font_name, font_size, max_width)
        for line in wrapped_lines:
            if y <= bottom_margin:
                pdf.showPage()
                pdf.setFont(font_name, font_size)
                y = height - top_margin
            pdf.drawString(left_margin, y, line)
            y -= line_height
        y -= line_height / 2

    pdf.save()
    output_path.write_bytes(buffer.getvalue())
