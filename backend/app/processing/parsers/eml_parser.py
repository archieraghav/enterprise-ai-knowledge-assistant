from email import message_from_bytes
from email.message import Message

from app.core.exceptions import ValidationException
from app.processing.parsers.base_parser import BaseParser


class EmlParser(BaseParser):
    """Extracts text content (headers + body) from .eml email files."""

    def extract_text(self, file_bytes: bytes) -> str:
        try:
            message: Message = message_from_bytes(file_bytes)
        except Exception as exc:
            raise ValidationException("Could not read EML file — it may be corrupted") from exc

        header_lines = [
            f"From: {message.get('From', '')}",
            f"To: {message.get('To', '')}",
            f"Subject: {message.get('Subject', '')}",
            f"Date: {message.get('Date', '')}",
        ]

        body_text = self._extract_body(message)

        return "\n".join(header_lines) + "\n\n" + body_text

    def _extract_body(self, message: Message) -> str:
        if message.is_multipart():
            parts = []
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        parts.append(payload.decode(charset, errors="replace"))
            return "\n".join(parts).strip()

        payload = message.get_payload(decode=True)
        if payload:
            charset = message.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace").strip()
        return ""