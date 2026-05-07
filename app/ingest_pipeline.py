"""Document ingestion pipeline with date metadata for cutoff-filtered retrieval."""

import os
import glob
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text, chunk_size=1000, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i: i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def estimate_date(filename):
    """Try to extract date from filename or return default."""
    name = filename.lower()
    for year_str in [str(y) for y in range(1800, 2030)]:
        if year_str in name:
            return f"{year_str}-01-01"
    return "1900-01-01"


def ingest_files():
    try:
        from app.rag_manager import RAGManager
        persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "/app/rag/vectorstore")
        rag = RAGManager(persist_dir)

        data_dir = "/app/data/processed"
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory {data_dir} not found. Creating placeholder.")
            os.makedirs(data_dir, exist_ok=True)
            sample = Path(data_dir) / "1908_harmsworth_encyclopedia_electricity.txt"
            if not sample.exists():
                sample.write_text(
                    "ELECTRICITY. A form of energy observed in natural phenomena such as lightning, "
                    "static discharge, and the action of voltaic cells. In the early twentieth century, "
                    "electricity is understood as the flow of electrons through conductive media. "
                    "The practical applications include incandescent lighting, electric motors, "
                    "telegraphy, and telephony. Voltaic piles and dynamos serve as generators. "
                    "\n\nSource: Adapted from the 1908 edition of Harmsworth Encyclopaedia."
                )
                logger.info("Created sample document (est. 1908).")

        text_files = glob.glob(os.path.join(data_dir, "*.txt"))
        if not text_files:
            logger.warning(f"No text files found in {data_dir}")
            return 0

        total_chunks = 0
        for filepath in text_files:
            filename = os.path.basename(filepath)
            source_date = estimate_date(filename)
            logger.info(f"Ingesting {filename} (date={source_date})...")
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            chunks = chunk_text(text)
            for chunk in chunks:
                rag.add_document(
                    chunk,
                    source_date=source_date,
                    metadata={"source": filename, "chunk_size": len(chunk)},
                )
                total_chunks += 1
            logger.info(f"  -> {len(chunks)} chunks from {filename}")
        logger.info(f"Ingestion complete: {total_chunks} total chunks")
        return total_chunks
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}")
        return -1


if __name__ == "__main__":
    t0 = time.time()
    count = ingest_files()
    elapsed = time.time() - t0
    logger.info(f"Ingestion finished in {elapsed:.1f}s. Chunks: {count}")
