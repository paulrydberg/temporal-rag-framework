"""Refactored main.py for cutoff-driven architecture."""

import os
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.inference import HistoricalInference
from app.rag_manager import RAGManager
from core.temporal import TemporalContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Time-Bound Reasoning Engine",
    description="Unified temporal constraint system driven by any cutoff_date",
    version="2.0.0",
)

inference = None
rag_manager = None


# --- Request/Response Models ---

class ChatRequest(BaseModel):
    prompt: str
    cutoff_date: str = ""
    strictness: str = "medium"
    temperature: float = 0.3
    max_tokens: int = 300
    use_rag: bool = True
    constrain_temporal: bool = True


class ChatResponse(BaseModel):
    response: str
    tokens_per_second: float
    temporal_context: dict
    rag_docs: list[str] = []
    temporal_filtered: bool = False
    temporal_violations: list[str] = []


class SearchRequest(BaseModel):
    query: str
    cutoff_date: str = ""
    top_k: int = 5


class SearchResponse(BaseModel):
    results: list[str]
    query: str
    cutoff_date: str
    total_docs: int


class TemporalContextRequest(BaseModel):
    cutoff_date: Optional[str] = None
    strictness: Optional[str] = "medium"


class TemporalContextResponse(BaseModel):
    cutoff_date: str
    cutoff_year: int
    strictness: str
    era_style: str
    forbidden_terms_count: int
    system_prompt_preview: str
    presets: list[str]
    strictness_options: list[str]


# --- Startup ---

@app.on_event("startup")
async def startup():
    global inference, rag_manager
    logger.info("Starting Time-Bound Reasoning Engine...")
    model_path = os.environ.get("MODEL_PATH", "/app/models/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
    n_threads = int(os.environ.get("LLAMA_CPP_THREADS", "4"))
    if os.path.exists(model_path):
        inference = HistoricalInference(model_path, n_threads)
        logger.info(f"Inference loaded from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}")
    rag_manager = RAGManager()
    default_cutoff = os.environ.get("TEMPORAL_CUTOFF", "1931-01-01")
    logger.info(f"Default temporal cutoff: {default_cutoff}")


# --- Health ---

@app.get("/health")
async def health():
    ctx = TemporalContext()
    return {
        "status": "healthy",
        "version": "2.0.0",
        "model_loaded": inference is not None,
        "rag_loaded": rag_manager is not None and rag_manager.is_ready(),
        "default_cutoff": ctx.cutoff_date.isoformat(),
        "presets": list(TemporalContext.presets().keys()),
        "strictness_options": TemporalContext.strictness_options(),
    }


# --- Temporal Context Endpoints ---

@app.get("/temporal/context", response_model=TemporalContextResponse)
async def get_temporal_context(cutoff_date: str = "", strictness: str = "medium"):
    ctx = TemporalContext(cutoff_date, strictness)
    return TemporalContextResponse(
        cutoff_date=ctx.cutoff_date.isoformat(),
        cutoff_year=ctx.cutoff_year,
        strictness=ctx.strictness,
        era_style=ctx.era_style,
        forbidden_terms_count=len(ctx.forbidden_terms),
        system_prompt_preview=ctx.system_prompt[:200] + "...",
        presets=list(TemporalContext.presets().keys()),
        strictness_options=TemporalContext.strictness_options(),
    )


@app.post("/temporal/context", response_model=TemporalContextResponse)
async def set_temporal_context(req: TemporalContextRequest):
    ctx = TemporalContext(req.cutoff_date, req.strictness)
    return TemporalContextResponse(
        cutoff_date=ctx.cutoff_date.isoformat(),
        cutoff_year=ctx.cutoff_year,
        strictness=ctx.strictness,
        era_style=ctx.era_style,
        forbidden_terms_count=len(ctx.forbidden_terms),
        system_prompt_preview=ctx.system_prompt[:200] + "...",
        presets=list(TemporalContext.presets().keys()),
        strictness_options=TemporalContext.strictness_options(),
    )


# --- Legacy Profile Compatibility ---

@app.get("/profiles")
async def list_profiles():
    """Legacy endpoint. Returns preset information."""
    presets = TemporalContext.presets()
    return [
        {"name": name, "cutoff_date": info["cutoff_date"], "label": info["label"]}
        for name, info in presets.items()
    ]


@app.post("/profiles/create")
async def create_profile():
    """Legacy stub — no longer needed. Use /temporal/context instead."""
    return {
        "message": "Profile system replaced by cutoff-driven architecture. "
                   "Use POST /temporal/context or pass cutoff_date directly to /chat."
    }


# --- Chat ---

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    ctx = TemporalContext(request.cutoff_date, request.strictness)

    rag_docs = []
    if request.use_rag and rag_manager and rag_manager.is_ready():
        rag_docs = rag_manager.search(
            request.prompt,
            cutoff_date=ctx.cutoff_date.isoformat(),
            top_k=3,
        )

    prompt = f"{ctx.system_prompt}\n\nUser query: {request.prompt}\n\nAnalysis:"
    if rag_docs:
        prompt = prompt.replace(
            ctx.system_prompt,
            ctx.system_prompt + "\n\nRelevant historical sources:\n"
            + "\n".join(f"{i+1}. {d[:500]}" for i, d in enumerate(rag_docs[:5]))
        )

    t0 = time.time()
    response = inference.generate(prompt, temperature=request.temperature, max_tokens=request.max_tokens)
    elapsed = time.time() - t0
    tokens = len(response.split())
    tok_s = tokens / elapsed if elapsed > 0 else 0

    violations = []
    filtered = False
    if request.constrain_temporal:
        violations = ctx.check_all(response)
        if violations:
            logger.warning(f"Temporal violations: {violations}")
            filtered = True

    return ChatResponse(
        response=response,
        tokens_per_second=tok_s,
        temporal_context=ctx.to_dict(),
        rag_docs=rag_docs,
        temporal_filtered=filtered,
        temporal_violations=violations,
    )


# --- RAG ---

@app.post("/rag/search", response_model=SearchResponse)
async def rag_search(request: SearchRequest):
    if rag_manager is None or not rag_manager.is_ready():
        raise HTTPException(status_code=503, detail="RAG not initialized")
    cutoff = request.cutoff_date or os.environ.get("TEMPORAL_CUTOFF", "1931-01-01")
    results = rag_manager.search(request.query, cutoff_date=cutoff, top_k=request.top_k)
    return SearchResponse(
        results=results,
        query=request.query,
        cutoff_date=cutoff,
        total_docs=len(results),
    )


@app.get("/rag/stats")
async def rag_stats():
    if rag_manager is None:
        return {"error": "RAG not initialized"}
    return rag_manager.get_stats()


# --- Benchmark ---

@app.get("/benchmark")
async def benchmark():
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return inference.benchmark()
