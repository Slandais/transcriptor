from __future__ import annotations

from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image
import pytesseract


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def is_pdf_file(path: Path) -> bool:
    return path.suffix.lower() == ".pdf"


def extract_text_from_image(image_path: Path, lang: str) -> str:
    with Image.open(image_path) as image:
        return pytesseract.image_to_string(image, lang=lang).strip()


def extract_text_from_pdf(pdf_path: Path, lang: str, dpi: int = 300) -> str:
    pages = convert_from_path(str(pdf_path), dpi=dpi)
    texts: list[str] = []

    for index, page in enumerate(pages, start=1):
        page_text = pytesseract.image_to_string(page, lang=lang).strip()
        header = f"[Page {index}]"
        texts.append(f"{header}\n{page_text}".strip())

    return "\n\n".join(texts).strip()


def extract_text(input_path: Path, lang: str, dpi: int = 300) -> str:
    if is_image_file(input_path):
        return extract_text_from_image(input_path, lang=lang)

    if is_pdf_file(input_path):
        return extract_text_from_pdf(input_path, lang=lang, dpi=dpi)

    raise ValueError(
        "Format d'entree non supporte. Utilisez une image ou un PDF."
    )
