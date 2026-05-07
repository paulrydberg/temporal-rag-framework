# Temporal Refactor Plan

## Phase 2: Cutoff-Driven Architecture (May 2026)

Previous state: Multi-profile YAML system (5+ files)
New state: Single TemporalContext class driven by cutoff_date

### What Changed

1. **core/temporal/** module replaces app/temporal_profile.py
   - context.py -> TemporalContext(cutoff_date, strictness)
   - rules_engine.py -> dynamic forbidden term generation from concept->year mapping
   - prompt_enforcer.py -> system prompt from cutoff + era style
   - vocabulary_builder.py -> alternative milestone-based term generation

2. **Config** simplification
   - config/temporal_defaults.yaml (single file)
   - Removed: config/temporal_profiles/ directory (5 YAML files)

3. **RAG** simplification
   - Removed profile-based vectorstore partitioning
   - Single unified collection with document_date metadata
   - Metadata filter: document_date <= cutoff_date

4. **API** simplification
   - Replaced: /profiles/ endpoints
   - Added: /temporal/context (GET + POST)
   - New /chat: accepts cutoff_date + strictness instead of profile

5. **Backward compatibility**
   - Legacy profile names (pre_1931, victorian, etc.) resolve to cutoff_date
   - /profiles endpoint returns preset info (no-op)

### File Changes
...
