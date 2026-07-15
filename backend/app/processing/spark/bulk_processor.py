from dataclasses import dataclass

from app.core.logging import get_logger
from app.processing.parser_factory import extract_text_from_file
from app.processing.spark.spark_session import get_spark_session

logger = get_logger(__name__)


@dataclass
class BulkFileInput:
    """A single file to be processed as part of a bulk batch job."""

    filename: str
    extension: str
    file_bytes: bytes


@dataclass
class BulkProcessingResult:
    """The outcome of processing one file in a bulk batch."""

    filename: str
    success: bool
    extracted_text: str | None
    error_message: str | None


def _process_single_file(filename: str, extension: str, file_bytes: bytes) -> BulkProcessingResult:
    """Extract text from one file, capturing any failure without crashing the batch."""
    try:
        text = extract_text_from_file(extension, file_bytes)
        return BulkProcessingResult(filename=filename, success=True, extracted_text=text, error_message=None)
    except Exception as exc:
        logger.warning("Bulk processing failed for '%s': %s", filename, exc)
        return BulkProcessingResult(filename=filename, success=False, extracted_text=None, error_message=str(exc))


def process_files_in_bulk(files: list[BulkFileInput]) -> list[BulkProcessingResult]:
    """Process a batch of files in parallel using Spark's distributed RDD processing.

    For small batches this has more overhead than benefit, but for large
    bulk uploads (hundreds of files), Spark parallelizes extraction across
    all available CPU cores automatically.
    """
    if not files:
        return []

    spark = get_spark_session()
    sc = spark.sparkContext

    # Distribute the file list across partitions for parallel processing.
    file_tuples = [(f.filename, f.extension, f.file_bytes) for f in files]
    rdd = sc.parallelize(file_tuples, numSlices=min(len(files), 8))

    results_rdd = rdd.map(lambda item: _process_single_file(item[0], item[1], item[2]))
    results = results_rdd.collect()

    return results