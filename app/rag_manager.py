import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

VECTORSTORE_BASE = os.environ.get("CHROMA_PERSIST_DIR", "/app/rag/vectorstore")


class RAGManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or VECTORSTORE_BASE
        self.collections = {}
        self.embedder = None
        self._initialized = False
        self._init()

    def _init(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer(
                os.environ.get("EMBEDDER_MODEL", "all-MiniLM-L6-v2"),
                device=os.environ.get("DEVICE", "cpu"),
            )
            self._initialized = True
        except Exception as e:
            logger.warning(f"RAGManager init failed: {e}")

    def _get_collection(self, profile_name):
        if profile_name in self.collections:
            return self.collections[profile_name]
        import chromadb
        persist = os.path.join(self.base_dir, profile_name)
        os.makedirs(persist, exist_ok=True)
        client = chromadb.PersistentClient(path=persist)
        name = profile_name.replace("-", "_") + "_docs"
        try:
            col = client.get_collection(name)
        except ValueError:
            col = client.create_collection(name)
        self.collections[profile_name] = col
        return col

    def is_ready(self):
        return self._initialized

    def search(self, query, profile_name="pre_1931", top_k=3):
        if not self._initialized:
            return []
        try:
            col = self._get_collection(profile_name)
            qe = self.embedder.encode([query]).tolist()
            count = col.count()
            if count == 0:
                return []
            results = col.query(query_embeddings=qe, n_results=min(top_k, count))
            docs = []
            if results and results.get("documents"):
                for dl in results["documents"]:
                    for d in dl:
                        docs.append(d[:500])
            return docs
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []

    def add_document(self, text, profile_name="pre_1931", metadata=None):
        if not self._initialized:
            return
        try:
            col = self._get_collection(profile_name)
            did = str(hash(text))
            emb = self.embedder.encode([text]).tolist()
            col.add(
                documents=[text],
                embeddings=emb,
                metadatas=[metadata or {"source": "unknown", "profile": profile_name}],
                ids=[did],
            )
        except Exception as e:
            logger.error(f"Failed to add document: {e}")

    def get_stats(self, profile_name):
        try:
            col = self._get_collection(profile_name)
            return {"profile": profile_name, "documents": col.count()}
        except Exception:
            return {"profile": profile_name, "documents": 0}
