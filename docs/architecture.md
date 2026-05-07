# Architecture

## Overview

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

## Components

1. **Inference Engine** — llama.cpp subprocess, Qwen 2.5 7B Q4_K_M GGUF
2. **RAG Manager** — ChromaDB + sentence-transformers, partitioned vectorstores by era
3. **Temporal Validator** — Profile-driven regex checking, configurable per-profile forbidden terms
4. **Profile Registry** — YAML-based profile system, hot-reloadable at runtime
5. **Prompt Builder** — Dynamic system prompt construction from profile templates with {CUTOFF_YEAR} substitution

## Data Flow

1. Client sends POST /chat with "profile" and "message"
2. Profile loaded from config/temporal_profiles/{profile}.yaml
3. (Optional) RAG retrieves temporally-grounded documents from era-partitioned vectorstore
4. Prompt built from profile's system_prompt template + RAG context
5. llama.cpp generates response via subprocess
6. Temporal validator checks response for forbidden terms
7. Response returned with violation metadata
