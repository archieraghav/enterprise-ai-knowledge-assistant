import csv
import io

from app.core.exceptions import ValidationException
from app.processing.parsers.base_parser import BaseParser


class CsvParser(BaseParser):
    """Extracts text content from CSV files, formatted as readable rows."""

    def extract_text(self, file_bytes: bytes) -> str:
        try:
            decoded = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValidationException("Could not decode CSV file — unsupported encoding") from exc

        try:
            reader = csv.reader(io.StringIO(decoded))
            rows = list(reader)
        except csv.Error as exc:
            raise ValidationException("Could not parse CSV file — invalid format") from exc

        if not rows:
            return ""

        header, *data_rows = rows
        lines = [" | ".join(header)]
        for row in data_rows:
            lines.append(" | ".join(row))

        return "\n".join(lines).strip()