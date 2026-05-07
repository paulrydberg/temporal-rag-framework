# Architecture

## Overview

```
  User / API Client
         |
    HTTP :8000
         |
  FastAPI Server (cutoff-driven)
   |          |               |
 Inference  RAG Manager   TemporalContext
  Engine    (metadata-      (unified: generates
   |         filtered by     forbidden terms,
 llama.cpp   date <=        system prompt,
 (Qwen 7B)   cutoff)        era style, rules)
```

## Key Change: Cutoff-Driven Architecture

Previous: 5+ hardcoded YAML profiles (pre_1931, victorian, etc.)
Now: Single `TemporalContext(cutoff_date, strictness)` class.

All reasoning derives dynamically from the cutoff_date:
- Forbidden terms: computed from concept->earliest_year mapping
- System prompt: generated with era-appropriate framing
- Era style: inferred from date ranges
- RAG filtering: document metadata date <= cutoff_date

## Data Flow

1. Client sends POST /chat with cutoff_date and prompt
2. TemporalContext created: cutoff_date -> forbidden terms + system prompt + era style
3. (Optional) RAG searches with metadata filter: document_date <= cutoff_date
4. Prompt built from TemporalContext system prompt + RAG context
5. llama.cpp generates response
6. TemporalContext validates output against dynamically computed forbidden terms
7. Response returned with context metadata
