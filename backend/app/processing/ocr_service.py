import io

import pytesseract
from PIL import Image

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.processing.parsers.base_parser import BaseParser

pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd_path


class ImageOCRParser(BaseParser):
    """Extracts text from images using Tesseract OCR."""

    def extract_text(self, file_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as exc:
            raise ValidationException("Could not read image file — it may be corrupted") from exc

        try:
            text = pytesseract.image_to_string(image)
        except Exception as exc:
            raise ValidationException("OCR text extraction failed") from exc

        return text.strip()