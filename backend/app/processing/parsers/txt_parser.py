from app.core.exceptions import ValidationException
from app.processing.parsers.base_parser import BaseParser


class TxtParser(BaseParser):
    """Extracts text content from plain text files."""

    def extract_text(self, file_bytes: bytes) -> str:
        for encoding in ("utf-8", "latin-1"):
            try:
                return file_bytes.decode(encoding).strip()
            except UnicodeDecodeError:
                continue

        raise ValidationException("Could not decode text file — unsupported encoding")