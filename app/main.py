"""Historical RAG Agent — FastAPI application."""

import os, time, logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.inference import HistoricalInference
from app.rag_retriever import RAGRetriever
from app.temporal_filter import TemporalFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Historical RAG Agent",
    description="Pre-1931 knowledge-constrained reasoning with RAG",
    version="0.1.0",
)

inference = None
retriever = None
temporal_filter = TemporalFilter()


class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.3
    max_tokens: int = 300
    use_rag: bool = True
    constrain_temporal: bool = True


class ChatResponse(BaseModel):
    response: str
    tokens_per_second: float
    rag_docs: list[str] = []
    temporal_filtered: bool = False


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResponse(BaseModel):
    results: list[str]
    query: str


@app.on_event("startup")
async def startup():
    global inference, retriever
    logger.info("Starting Historical RAG Agent...")
    model_path = os.environ.get("MODEL_PATH", "/app/models/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
    n_threads = int(os.environ.get("LLAMA_CPP_THREADS", "4"))
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", "/app/rag/vectorstore")
    if os.path.exists(model_path):
        inference = HistoricalInference(model_path, n_threads)
        logger.info(f"Inference engine loaded from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}. Inference disabled.")
    retriever = RAGRetriever(persist_dir)
    logger.info(f"RAG retriever initialized with persist_dir={persist_dir}")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": inference is not None,
        "rag_loaded": retriever is not None and retriever.is_ready(),
        "temporal_filter": temporal_filter is not None,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    rag_docs = []
    if request.use_rag and retriever and retriever.is_ready():
        rag_docs = retriever.search(request.prompt, top_k=3)
    prompt = build_prompt(request.prompt, rag_docs, request.constrain_temporal)
    t0 = time.time()
    response = inference.generate(prompt, temperature=request.temperature, max_tokens=request.max_tokens)
    elapsed = time.time() - t0
    tokens = len(response.split())
    tok_s = tokens / elapsed if elapsed > 0 else 0
    filtered = False
    if request.constrain_temporal:
        violation = temporal_filter.check(response)
        if violation:
            logger.warning(f"Temporal constraint violation detected: {violation}")
            filtered = True
    return ChatResponse(
        response=response,
        tokens_per_second=tok_s,
        rag_docs=rag_docs,
        temporal_filtered=filtered,
    )


@app.post("/rag/search", response_model=SearchResponse)
async def rag_search(request: SearchRequest):
    if retriever is None or not retriever.is_ready():
        raise HTTPException(status_code=503, detail="RAG not initialized")
    results = retriever.search(request.query, top_k=request.top_k)
    return SearchResponse(results=results, query=request.query)


@app.get("/benchmark")
async def benchmark():
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return inference.benchmark()


def build_prompt(user_prompt: str, rag_context: list[str], constrain: bool) -> str:
    system = (
        "You are a historical reasoning model. Your knowledge is limited to the period before 1931.\n"
        "Do NOT reference events, inventions, or knowledge after 1930.\n"
        "Do NOT use modern terminology such as: computer, internet, AI, transistor, quantum, "
        "nuclear weapon, smartphone, machine learning, digital, semiconductor, satellite, GPS.\n"
        "Prefer 19th and early 20th century framing. Use classical physics, industrial-era analogies.\n"
        "If a concept lies outside pre-1931 knowledge, say: "
        '"This matter lies beyond the knowledge available in the present era."\n'
    )
    if rag_context:
        system += "\nRelevant historical sources:\n"
        for i, doc in enumerate(rag_context, 1):
            system += f"{i}. {doc[:500]}\n"
    return f"{system}\n\nUser query: {user_prompt}\n\nHistorical analysis:"
