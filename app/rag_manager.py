"""Refactored RAGManager with metadata-filtered retrieval (date <= cutoff)."""

import os
import logging
from datetime import date

logger = logging.getLogger(__name__)

VECTORSTORE_BASE = os.environ.get("CHROMA_PERSIST_DIR", "/app/rag/vectorstore")


class RAGManager:
    """Profile-aware RAG with metadata-filtered retrieval by date."""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or VECTORSTORE_BASE
        self.collection = None
        self.embedder = None
        self._initialized = False
        self._init()

    def _init(self):
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            self.embedder = SentenceTransformer(
                os.environ.get("EMBEDDER_MODEL", "all-MiniLM-L6-v2"),
                device=os.environ.get("DEVICE", "cpu"),
            )
            os.makedirs(self.base_dir, exist_ok=True)
            client = chromadb.PersistentClient(path=self.base_dir)
            try:
                self.collection = client.get_collection("historical_docs")
            except ValueError:
                self.collection = client.create_collection("historical_docs")
            self._initialized = True
            count = self.collection.count()
            logger.info(f"RAGManager initialized: {count} documents")
        except Exception as e:
            logger.warning(f"RAGManager init failed: {e}")

    def is_ready(self):
        return self._initialized

    def search(self, query, cutoff_date=None, top_k=3):
        """Search documents where document_date <= cutoff_date."""
        if not self._initialized or self.collection is None:
            return []
        try:
            qe = self.embedder.encode([query]).tolist()
            count = self.collection.count()
            if count == 0:
                return []

            where_filter = None
            if cutoff_date:
                where_filter = {"document_date": {"$lte": str(cutoff_date)}}

            results = self.collection.query(
                query_embeddings=qe,
                n_results=min(top_k, count),
                where=where_filter if where_filter else None,
            )
            docs = []
            if results and results.get("documents"):
                for dl in results["documents"]:
                    for d in dl:
                        docs.append(d[:500])
            return docs
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []

    def add_document(self, text, source_date=None, metadata=None):
        """Add document with date metadata for filtered retrieval.

        Args:
            text: Document text content.
            source_date: ISO format date string (YYYY-MM-DD) or None for default.
            metadata: Optional dict with additional metadata.
        """
        if not self._initialized or self.collection is None:
            return
        try:
            did = str(hash(text))
            emb = self.embedder.encode([text]).tolist()
            meta = metadata or {}
            if source_date:
                meta["document_date"] = str(source_date)
            else:
                meta["document_date"] = "1900-01-01"
            self.collection.add(
                documents=[text],
                embeddings=emb,
                metadatas=[meta],
                ids=[did],
            )
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    def get_stats(self):
        """Get overall collection statistics."""
        if not self._initialized or self.collection is None:
            return {"total_documents": 0}
        try:
            return {"total_documents": self.collection.count()}
        except Exception:
            return {"total_documents": 0}
