# Historical RAG Agent

**Pre-1931 Knowledge-Constrained Reasoning with Retrieval-Augmented Generation**

A fully reproducible, Dockerized historical reasoning system that enforces a knowledge boundary of January 1, 1931. Built on Qwen 2.5 7B Instruct, llama.cpp, ChromaDB, and FastAPI.

---

## Quick Start

```
git clone https://github.com/paulrydberg/historical-rag-agent.git
cd historical-rag-agent
./scripts/download_model.sh
docker compose build
docker compose up -d
docker compose --profile ingest run ingest
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"prompt": "Explain what electricity is", "temperature": 0.3}'
```

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB | 20 GB |
| GPU | Not required | RTX 3070+ |

CPU-only at 11.2 tok/s.

## Architecture

User Client -> FastAPI -> [Inference (llama.cpp/Qwen 7B), RAG (ChromaDB), Temporal Filter]

## How It Works

1. **Knowledge Constraint**: System prompt enforces January 1, 1931 cutoff. Regex filter validates output against 50+ modern terms.
2. **Historical RAG**: Documents chunked, embedded via sentence-transformers, stored in ChromaDB.
3. **Inference**: Qwen 2.5 7B via llama.cpp CLI subprocess. CPU-only, Q4_K_M quantization.

## API Endpoints

- POST /chat - Primary inference with optional RAG + temporal constraint
- GET /health - System status (model_loaded, rag_loaded, temporal_filter)
- POST /rag/search - Direct RAG search
- GET /benchmark - Run performance benchmarks

## Performance

| Metric | Value |
|--------|-------|
| Prompt eval | 53.5 tok/s |
| Generation | 11.2 tok/s |
| RAG latency | ~50ms |
| Filter latency | <1ms |

## Why Not Talkie 1930?

The Talkie 1930 13B model family has a fundamental output layer corruption: resize_model_embeddings added OOV tokens with 4x variance, and lm_head_gain=3.89 amplifies them. Qwen 2.5 7B provides a clean, stable alternative with the constraint enforced via system prompt.

## Reproducibility

```
git clone https://github.com/paulrydberg/historical-rag-agent.git
cd historical-rag-agent
docker compose build --no-cache
./scripts/download_model.sh
docker compose up -d
```

---

*Built with llama.cpp, Qwen 2.5, ChromaDB, and public domain historical sources.*
