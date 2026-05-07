"""RAG retriever using ChromaDB and sentence-transformers."""

import os, logging
from typing import Optional

logger = logging.getLogger(__name__)


class RAGRetriever:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir
        self.collection = None
        self.embedder = None
        self._initialized = False
        self._init()

    def _init(self):
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2", device=os.environ.get("DEVICE", "cpu"))
            client = chromadb.PersistentClient(path=self.persist_dir)
            try:
                self.collection = client.get_collection("historical_docs")
            except ValueError:
                self.collection = client.create_collection("historical_docs")
            self._initialized = True
            count = self.collection.count()
            logger.info(f"RAG initialized with {count} documents in collection")
        except Exception as e:
            logger.warning(f"RAG initialization failed: {e}. RAG will be unavailable.")

    def is_ready(self) -> bool:
        return self._initialized and self.collection is not None

    def search(self, query: str, top_k: int = 5) -> list[str]:
        if not self.is_ready():
            return []
        try:
            qe = self.embedder.encode([query]).tolist()
            results = self.collection.query(
                query_embeddings=qe,
                n_results=min(top_k, self.collection.count() or top_k),
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

    def add_document(self, text: str, metadata: Optional[dict] = None):
        if not self.is_ready():
            return
        try:
            did = str(hash(text))
            emb = self.embedder.encode([text]).tolist()
            self.collection.add(
                documents=[text], embeddings=emb,
                metadatas=[metadata or {"source": "unknown"}], ids=[did],
            )
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
