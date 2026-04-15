from pathlib import Path

from transcriptor.pdf_writer import write_text_pdf


def test_write_text_pdf_creates_file(tmp_path: Path) -> None:
    output_path = tmp_path / "result.pdf"

    write_text_pdf(output_path, "Bonjour\nCeci est un test", title="Test")

    assert output_path.exists()
    assert output_path.stat().st_size > 0
