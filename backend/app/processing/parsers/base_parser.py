from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Defines the contract every file-type parser must implement."""

    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        """Extract plain text content from raw file bytes."""
        raise NotImplementedError