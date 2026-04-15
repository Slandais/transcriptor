from pathlib import Path

from transcriptor.ocr import is_image_file, is_pdf_file


def test_is_image_file_supports_common_extensions() -> None:
    assert is_image_file(Path("scan.JPG"))
    assert is_image_file(Path("scan.png"))
    assert not is_image_file(Path("document.pdf"))


def test_is_pdf_file_detects_pdf() -> None:
    assert is_pdf_file(Path("document.pdf"))
    assert not is_pdf_file(Path("photo.jpeg"))
