# Temporal Refactor Plan

## Audit: Hardcoded Pre-1931 References Found

The following files contained hardcoded references to 1931 or 1930:

| File | Issue | Status |
|------|-------|--------|
| app/temporal_filter.py | FORBIDDEN_TERMS hardcoded, date patterns 1980-2099 | Removed, replaced by profiles |
| app/main.py | build_prompt() hardcoded before 1931 | Refactored to use profile |
| app/inference.py | No profile awareness | Still standalone (subprocess-based) |
| prompts/pre1931_system.txt | Entire file hardcoded to 1931 | Kept as example, replaced by profile system |
| scripts/run_historical.sh | Contains hardcoded prompt text | Updated to use profile |
| README.md | Multiple pre-1931 references | Rewritten as Temporal Framework |

## Refactoring Applied

1. Created config/temporal_profiles/ with 5 YAML profiles (pre_1931, pre_1965, victorian, pre_internet, cold_war)
2. Created app/temporal_profile.py with TemporalProfile + ProfileRegistry classes
3. Created app/prompt_builder.py for dynamic prompt construction from any profile
4. Created app/rag_manager.py with profile-partitioned vectorstores
5. Refactored app/main.py with profile-driven API (/profiles/, /chat with profile parameter)
6. Removed app/temporal_filter.py (hardcoded terms)
7. Updated Dockerfile and docker-compose.yml for new structure
8. Rewrote README.md as Temporal Intelligence Framework
9. Created tests/ (9 tests, all passing)
10. Created benchmark templates

## Naming Decision

Repository renamed from **historical-rag-agent** to **temporal-rag-framework**.

Rationale:
- Temporal reflects the generalized time-bound constraint paradigm
- RAG preserves the retrieval component
- Framework implies extensibility beyond a single agent
