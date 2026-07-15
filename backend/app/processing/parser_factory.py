from app.core.exceptions import ValidationException
from app.processing.ocr_service import ImageOCRParser
from app.processing.parsers.base_parser import BaseParser
from app.processing.parsers.csv_parser import CsvParser
from app.processing.parsers.docx_parser import DocxParser
from app.processing.parsers.eml_parser import EmlParser
from app.processing.parsers.excel_parser import ExcelParser
from app.processing.parsers.pdf_parser import PDFParser
from app.processing.parsers.pptx_parser import PptxParser
from app.processing.parsers.txt_parser import TxtParser

_PARSER_REGISTRY: dict[str, type[BaseParser]] = {
    "pdf": PDFParser,
    "docx": DocxParser,
    "txt": TxtParser,
    "pptx": PptxParser,
    "csv": CsvParser,
    "xlsx": ExcelParser,
    "eml": EmlParser,
    "png": ImageOCRParser,
    "jpg": ImageOCRParser,
    "jpeg": ImageOCRParser,
}


def get_parser_for_extension(extension: str) -> BaseParser:
    """Return an instantiated parser for the given file extension."""
    parser_class = _PARSER_REGISTRY.get(extension.lower())
    if parser_class is None:
        raise ValidationException(f"No parser available for file type '.{extension}'")
    return parser_class()


def extract_text_from_file(extension: str, file_bytes: bytes) -> str:
    """Convenience function: get the right parser and extract text in one call."""
    parser = get_parser_for_extension(extension)
    return parser.extract_text(file_bytes)