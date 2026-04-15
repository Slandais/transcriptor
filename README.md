# Transcriptor

Transcriptor est une application CLI qui prend en entree un fichier PDF ou une image,
extrait le texte via OCR, puis genere un PDF contenant la transcription.

## Fonctionnalites

- OCR sur image (`.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp`)
- OCR sur PDF via conversion page par page
- Generation d'un PDF de sortie avec le texte transcrit
- Choix de la langue Tesseract

## Prerequis systeme

Le projet s'appuie sur des outils natifs :

- `tesseract` doit etre installe et accessible dans le `PATH`
- pour les PDF, `poppler` doit etre installe afin que `pdf2image` puisse convertir les pages

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## Utilisation

```bash
transcriptor input.pdf output.pdf --lang fra
```

Exemple avec une image :

```bash
transcriptor scan.jpg transcription.pdf --lang fra
```

## Structure

- `src/transcriptor/ocr.py` : extraction OCR
- `src/transcriptor/pdf_writer.py` : generation du PDF de sortie
- `src/transcriptor/pipeline.py` : orchestration complete
- `src/transcriptor/cli.py` : point d'entree en ligne de commande
