from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import transcribe_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transcriptor",
        description="Transcrit un PDF ou une image vers un PDF texte."
    )
    parser.add_argument("input", type=Path, help="Chemin du fichier source PDF ou image")
    parser.add_argument("output", type=Path, help="Chemin du PDF de sortie")
    parser.add_argument(
        "--lang",
        default="fra",
        help="Langue Tesseract a utiliser, par exemple fra, eng ou fra+eng",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = transcribe_file(args.input, args.output, lang=args.lang)
    print(f"Transcription terminee: {result.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
