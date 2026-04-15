from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ocr import extract_text
from .pdf_writer import write_text_pdf


@dataclass(slots=True)
class TranscriptionResult:
    input_path: Path
    output_path: Path
    text: str


def transcribe_file(input_file: str | Path, output_file: str | Path, lang: str = "fra") -> TranscriptionResult:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {input_path}")

    text = extract_text(input_path, lang=lang)
    if not text.strip():
        text = "[Aucun texte detecte]"

    write_text_pdf(output_path, text, title=f"Transcription - {input_path.name}")
    return TranscriptionResult(input_path=input_path, output_path=output_path, text=text)
