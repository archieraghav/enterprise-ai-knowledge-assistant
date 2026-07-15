from pyspark.sql import SparkSession
import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

_spark_session: SparkSession | None = None


def get_spark_session() -> SparkSession:
    """Return a singleton local SparkSession for batch document processing.

    Uses local[*] mode — runs entirely on this machine using all available
    CPU cores, no external Spark cluster required. Suitable for dev and
    for the scale of bulk uploads this project targets.
    """
    global _spark_session

    if _spark_session is None:
        _spark_session = (
            SparkSession.builder.appName("KnowledgeAssistantBulkProcessor")
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", "4")
            .config("spark.ui.showConsoleProgress", "false")
            .getOrCreate()
        )

    return _spark_session


def stop_spark_session() -> None:
    """Stop the active SparkSession, if one exists."""
    global _spark_session
    if _spark_session is not None:
        _spark_session.stop()
        _spark_session = None