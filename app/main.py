import os
import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.inference import HistoricalInference
from app.rag_manager import RAGManager
from app.temporal_profile import ProfileRegistry
from app.prompt_builder import build_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Temporal RAG Framework",
    description="Generalized temporal constraint intelligence framework",
    version="1.0.0",
)

inference = None
rag_manager = None
profile_registry = ProfileRegistry()


class ChatRequest(BaseModel):
    prompt: str
    profile: str = ""
    temperature: float = 0.3
    max_tokens: int = 300
    use_rag: bool = True
    constrain_temporal: bool = True


class ChatResponse(BaseModel):
    response: str
    tokens_per_second: float
    profile_used: str
    rag_docs: list[str] = []
    temporal_filtered: bool = False
    temporal_violations: list[str] = []


class SearchRequest(BaseModel):
    query: str
    profile: str = ""
    top_k: int = 5


class SearchResponse(BaseModel):
    results: list[str]
    query: str
    profile: str
    total_docs: int


class ProfileCreateRequest(BaseModel):
    name: str
    label: str = ""
    cutoff_year: int = 1931
    cutoff_date: str = ""
    forbidden_terms: list[str] = []
    forbidden_concepts: list[str] = []
    system_prompt: str = ""
    historical_style: str = "neutral"


class ProfileInfo(BaseModel):
    name: str
    label: str
    description: str
    cutoff_year: int
    cutoff_date: str
    forbidden_terms_count: int
    historical_style: str


@app.on_event("startup")
async def startup():
    global inference, rag_manager
    logger.info("Starting Temporal RAG Framework...")
    model_path = os.environ.get("MODEL_PATH", "/app/models/Qwen2.5-7B-Instruct-Q4_K_M.gguf")
    n_threads = int(os.environ.get("LLAMA_CPP_THREADS", "4"))
    if os.path.exists(model_path):
        inference = HistoricalInference(model_path, n_threads)
        logger.info(f"Inference loaded from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}")
    rag_manager = RAGManager()
    profiles = profile_registry.list_profiles()
    logger.info(f"Loaded {len(profiles)} temporal profiles")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": inference is not None,
        "rag_loaded": rag_manager is not None and rag_manager.is_ready(),
        "profiles_loaded": len(profile_registry.profiles),
        "profiles": [p["name"] for p in profile_registry.list_profiles()],
        "default_profile": profile_registry.default_profile_name,
    }


@app.get("/profiles", response_model=list[ProfileInfo])
async def list_profiles():
    return profile_registry.list_profiles()


@app.get("/profiles/{name}", response_model=ProfileInfo)
async def get_profile(name: str):
    profile = profile_registry.get(name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{name}' not found")
    return profile.to_dict()


@app.post("/profiles/create")
async def create_profile(req: ProfileCreateRequest):
    if profile_registry.get(req.name):
        raise HTTPException(status_code=409, detail=f"Profile '{req.name}' already exists")
    data = req.dict()
    if not data.get("cutoff_date"):
        data["cutoff_date"] = f"{data['cutoff_year']}-01-01"
    if not data.get("label"):
        data["label"] = data["name"]
    try:
        profile = profile_registry.create_profile(data)
        return {"status": "created", "profile": profile.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {e}")


@app.post("/profiles/reload")
async def reload_profiles():
    profile_registry.reload()
    return {"status": "reloaded", "profiles": len(profile_registry.profiles)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    profile_name = request.profile or profile_registry.default_profile_name
    profile = profile_registry.get(profile_name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_name}' not found")

    rag_docs = []
    if request.use_rag and rag_manager and rag_manager.is_ready():
        rag_docs = rag_manager.search(request.prompt, profile_name=profile_name, top_k=3)

    prompt = build_prompt(request.prompt, profile, rag_docs)

    t0 = time.time()
    response = inference.generate(prompt, temperature=request.temperature, max_tokens=request.max_tokens)
    elapsed = time.time() - t0
    tokens = len(response.split())
    tok_s = tokens / elapsed if elapsed > 0 else 0

    violations = []
    filtered = False
    if request.constrain_temporal:
        violations = profile.check_all(response)
        if violations:
            logger.warning(f"Temporal violations in response: {violations}")
            filtered = True

    return ChatResponse(
        response=response,
        tokens_per_second=tok_s,
        profile_used=profile_name,
        rag_docs=rag_docs,
        temporal_filtered=filtered,
        temporal_violations=violations,
    )


@app.post("/rag/search", response_model=SearchResponse)
async def rag_search(request: SearchRequest):
    if rag_manager is None or not rag_manager.is_ready():
        raise HTTPException(status_code=503, detail="RAG not initialized")
    profile_name = request.profile or profile_registry.default_profile_name
    results = rag_manager.search(request.query, profile_name=profile_name, top_k=request.top_k)
    stats = rag_manager.get_stats(profile_name)
    return SearchResponse(
        results=results,
        query=request.query,
        profile=profile_name,
        total_docs=stats.get("documents", 0),
    )


@app.get("/rag/stats")
async def rag_stats():
    if rag_manager is None:
        return {"error": "RAG not initialized"}
    stats = []
    for name in profile_registry.profiles:
        stats.append(rag_manager.get_stats(name))
    return {"collections": stats}


@app.get("/benchmark")
async def benchmark():
    if inference is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return inference.benchmark()
