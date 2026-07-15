from pathlib import Path

import pytest

from app.processing.parser_factory import extract_text_from_file
from app.processing.parsers.csv_parser import CsvParser
from app.processing.parsers.docx_parser import DocxParser
from app.processing.parsers.eml_parser import EmlParser
from app.processing.parsers.excel_parser import ExcelParser
from app.processing.parsers.pptx_parser import PptxParser
from app.processing.parsers.txt_parser import TxtParser

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample-data"


def _read_sample(filename: str) -> bytes:
    path = SAMPLE_DIR / filename
    if not path.exists():
        pytest.skip(f"Fixture {filename} not found — run generate_fixtures.py first")
    return path.read_bytes()


def test_txt_parser_extracts_content() -> None:
    content = _read_sample("sample.txt")
    result = TxtParser().extract_text(content)
    assert "sample text document" in result


def test_csv_parser_extracts_rows() -> None:
    content = _read_sample("sample.csv")
    result = CsvParser().extract_text(content)
    assert "name | department | salary" in result
    assert "Alice" in result


def test_docx_parser_extracts_paragraphs_and_tables() -> None:
    content = _read_sample("sample.docx")
    result = DocxParser().extract_text(content)
    assert "Sample Company Policy" in result
    assert "Remote days" in result


def test_pptx_parser_extracts_slide_text() -> None:
    content = _read_sample("sample.pptx")
    result = PptxParser().extract_text(content)
    assert "Q3 Company Overview" in result
    assert "Revenue grew" in result


def test_excel_parser_extracts_sheet_data() -> None:
    content = _read_sample("sample.xlsx")
    result = ExcelParser().extract_text(content)
    assert "Marketing" in result
    assert "Engineering" in result


def test_eml_parser_extracts_headers_and_body() -> None:
    content = _read_sample("sample.eml")
    result = EmlParser().extract_text(content)
    assert "Weekly Update" in result
    assert "project update" in result


def test_parser_factory_dispatches_correctly() -> None:
    content = _read_sample("sample.txt")
    result = extract_text_from_file("txt", content)
    assert "sample text document" in result


def test_parser_factory_raises_for_unsupported_type() -> None:
    from app.core.exceptions import ValidationException

    with pytest.raises(ValidationException):
        extract_text_from_file("exe", b"fake binary content")