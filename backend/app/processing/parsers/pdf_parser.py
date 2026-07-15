import io

from pypdf import PdfReader

from app.core.exceptions import ValidationException
from app.processing.parsers.base_parser import BaseParser


class PDFParser(BaseParser):
    """Extracts text content from PDF files."""

    def extract_text(self, file_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
        except Exception as exc:
            raise ValidationException("Could not read PDF file — it may be corrupted") from exc

        pages_text = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        return "\n\n".join(pages_text).strip()