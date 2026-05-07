# Temporal RAG Framework

**A Generalized Temporal Constraint Intelligence Framework**

Configurable knowledge-boundary enforcement with retrieval-augmented generation,
supporting any historical cutoff year, era, or temporal worldview.

---

## Quick Start

```bash
git clone https://github.com/paulrydberg/temporal-rag-framework.git
cd temporal-rag-framework
./scripts/download_model.sh
docker compose build
docker compose up -d
docker compose --profile ingest run ingest

# Chat with pre-1931 profile (default)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"profile": "pre_1931", "prompt": "Explain electricity"}'

# Switch to Victorian era
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"profile": "victorian", "prompt": "Describe steam engines"}'
```

---

## Architecture

```
  User / API Client
         |
    HTTP :8000
         |
  FastAPI Server
   |          |            |          |
 Inference   RAG       Temporal    Profile
  Engine   Manager    Validator    Registry
   |          |            |          |
 llama.cpp  ChromaDB    Profile-    YAML files
 (Qwen 7B) (partitioned  driven    (5 built-in)
            by era)      regex
```

---

## Built-in Profiles

| Profile | Cutoff | Description |
|---------|--------|-------------|
| pre_1931 | 1931 | Pre-1931 historical reasoning |
| pre_1965 | 1965 | Mid-century, vacuum tubes, early computing |
| victorian | 1901 | Victorian era natural philosophy |
| pre_internet | 1995 | Pre-web, analog media era |
| cold_war | 1991 | Cold War strategic analysis |

Use any profile via `"profile": "name"` in requests. Default: `pre_1931`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | System status with loaded profiles |
| GET | /profiles | List all temporal profiles |
| GET | /profiles/{name} | Get profile details |
| POST | /profiles/create | Create new temporal profile |
| POST | /profiles/reload | Hot-reload profiles from disk |
| POST | /chat | Chat with profile-constrained inference |
| POST | /rag/search | Search era-partitioned RAG |
| GET | /rag/stats | RAG collection statistics |
| GET | /benchmark | Run performance benchmarks |

---

## Creating Custom Profiles

### Via API

```bash
curl -X POST http://localhost:8000/profiles/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "pre_wwi",
    "label": "Pre-World War I",
    "cutoff_year": 1914,
    "forbidden_terms": ["airplane", "radio", "television"],
    "system_prompt": "You are a pre-WWI reasoning model."
  }'
```

### Via YAML

Add a file to `config/temporal_profiles/` and call POST /profiles/reload.

---

## Performance

| Metric | Value |
|--------|-------|
| Prompt eval | 53.5 tok/s |
| Generation | 11.2 tok/s |
| RAG latency | ~50ms |
| Filter latency | <1ms |
| Profile switch | <10ms |

---

## Use Cases

- **Historical simulation** — roleplay historical figures with period-accurate knowledge
- **Educational** — teach historical scientific understanding without modern framing
- **Alternate worldview simulation** — reason within pre-modern frameworks
- **Research** — analyze how historical thinkers approach modern questions
- **Content creation** — period-accurate dialogue, writing, or explanations

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Disk | 10 GB | 20 GB |
| GPU | Not required | RTX 3070+ |

CPU-only at ~11.2 tok/s (Qwen 2.5 7B Q4_K_M GGUF).

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

---

*Built with llama.cpp, Qwen 2.5, ChromaDB, and public domain historical sources.*
