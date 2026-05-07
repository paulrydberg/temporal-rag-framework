# Stage 1: llama.cpp build
FROM debian:bookworm-slim AS llama-builder

RUN apt-get update && apt-get install -y \
    build-essential cmake git wget \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch b4100 https://github.com/ggerganov/llama.cpp /opt/llama.cpp

WORKDIR /opt/llama.cpp
RUN mkdir build && cd build && cmake .. -DLLAMA_CUBLAS=OFF -DLLAMA_NATIVE=OFF -DCMAKE_BUILD_TYPE=Release && cmake --build . --config Release -j$(nproc) --target llama-cli llama-server

# Stage 2: Python runtime
FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y \
    wget git curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=llama-builder /opt/llama.cpp/build/bin/llama-cli /usr/local/bin/llama-cli
COPY --from=llama-builder /opt/llama.cpp/build/bin/llama-server /usr/local/bin/llama-server

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
COPY core/ /app/core/
COPY config/ /app/config/
COPY prompts/ /app/prompts/
COPY scripts/ /app/scripts/

RUN mkdir -p /app/data/raw /app/data/processed /app/rag/vectorstore /app/benchmarks/results

RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

ENV TEMPORAL_CUTOFF=1931-01-01

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
