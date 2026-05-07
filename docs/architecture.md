# Architecture

## Overview
```
  User / API Client
         |
    HTTP :8000
         |
  FastAPI Server
   |          |            |
 Inference   RAG     Temporal
  Engine   Retriever   Filter
   |          |
 llama.cpp  ChromaDB
 (Qwen 7B) (vectors)
```

## Components
1. **Inference** — llama.cpp subprocess, Qwen 2.5 7B Q4_K_M
2. **RAG** — ChromaDB + sentence-transformers, historical doc retrieval
3. **Temporal Filter** — regex validator, 50+ forbidden modern terms
4. **Ingestion** — doc chunking and embedding pipeline
