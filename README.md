# Time-Bound Reasoning Engine

**A cutoff-driven temporal constraint system.**

Configure ANY knowledge cutoff date. The system dynamically generates forbidden terms,
era-appropriate system prompts, reasoning style, and RAG retrieval filters from a single
runtime parameter: `cutoff_date`.

---

## Quick Start

```bash
git clone https://github.com/paulrydberg/temporal-rag-framework.git
cd temporal-rag-framework
./scripts/download_model.sh
docker compose build
docker compose up -d

# Chat with 1931 knowledge cutoff (default)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"cutoff_date": "1931-01-01", "prompt": "Explain electricity"}'

# Chat with Victorian-era cutoff
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"cutoff_date": "1900-01-01", "prompt": "Describe a horseless carriage"}'

# Chat with turn-of-the-millennium cutoff
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"cutoff_date": "2000-01-01", "prompt": "What is the internet?"}'
```

---

## How It Works

This system replaces hardcoded profiles with a **single unified cutoff-driven architecture**:

1. **Pick a date**: Pass any `cutoff_date` (YYYY-MM-DD) at runtime
2. **Dynamic generation**: The system computes forbidden terms, system prompt, era style,
   and reasoning rules from the cutoff date alone
3. **RAG filtering**: Documents are retrieved only if their metadata date <= the cutoff date
4. **Validation**: Output is checked against dynamically generated forbidden term patterns

No profile files. No YAML config. No code changes.

---

## Examples

| Cutoff | Prompt | Behavior |
|--------|--------|----------|
| 1931-01-01 | "Explain computing" | Mechanical calculators, Babbage, pre-transistor |
| 1900-01-01 | "Explain communication" | Telegraph, telephone, no radio/broadcast |
| 2000-01-01 | "Explain the internet" | ARPANET, pre-web, no social media |
| 1800-01-01 | "Explain power" | Steam, water wheels, no electricity |
| 1965-01-01 | "Explain computers" | Mainframes, vacuum tubes, no microprocessors |

---

## Strictness Levels

| Level | Behavior |
|-------|----------|
| low | Permissive filtering, allows near-boundary terms |
| medium | Balanced filtering (default) |
| high | Strict filtering, forbids everything within 10 years of cutoff |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | System status |
| GET | /temporal/context | Inspect current temporal context |
| POST | /temporal/context | Set and inspect any cutoff |
| POST | /chat | Chat with cutoff-constrained reasoning |
| POST | /rag/search | Search metadata-filtered documents |
| GET | /rag/stats | RAG collection statistics |
| GET | /benchmark | Run performance benchmarks |

### Chat Request

```json
{  "cutoff_date": "1931-01-01",
   "strictness": "medium",
   "prompt": "Explain steam engines",
   "temperature": 0.3,
   "max_tokens": 300,
   "use_rag": true,
   "constrain_temporal": true
}
```

### Chat Response

```json
{  "response": "...",
   "tokens_per_second": 11.2,
   "temporal_context": { "cutoff_date": "1931-01-01", ... },
   "temporal_filtered": false,
   "temporal_violations": []
}
```

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB | 20 GB |

CPU-only at ~11.2 tok/s with Qwen 2.5 7B Q4_K_M GGUF.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| TEMPORAL_CUTOFF | 1931-01-01 | Default temporal boundary date |
| MODEL_PATH | /app/models/Qwen2.5-7B-Instruct-Q4_K_M.gguf | GGUF model path |
| LLAMA_CPP_THREADS | 4 | CPU threads for inference |
| DEVICE | cpu | Inference device (cpu/cuda) |
| CHROMA_PERSIST_DIR | /app/rag/vectorstore | Vector database path |

---

## Architecture

```
  User / API Client
         |
    HTTP :8000
         |
  FastAPI Server (cutoff-driven)
   |          |               |
 Inference  RAG Manager   TemporalContext
  Engine    (metadata-      (unified)
   |         filtered by   generates rules,
 llama.cpp   date <=        terms, prompts,
 (Qwen 7B)   cutoff)        era style)
```

---

## Reproducibility

```bash
git clone https://github.com/paulrydberg/temporal-rag-framework.git
cd temporal-rag-framework
docker compose build --no-cache
./scripts/download_model.sh
docker compose up -d
```

## License

MIT

*Built with llama.cpp, Qwen 2.5, ChromaDB, and a single cutoff_date.*
