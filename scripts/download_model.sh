#!/bin/bash
# Download Qwen 2.5 7B Instruct Q4_K_M GGUF
set -e

MODEL_DIR="${1:-./models}"
mkdir -p "$MODEL_DIR"

MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
MODEL_FILE="$MODEL_DIR/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

if [ -f "$MODEL_FILE" ]; then
    echo "Model already exists at $MODEL_FILE"
    ls -lh "$MODEL_FILE"
    exit 0
fi

echo "Downloading Qwen 2.5 7B Q4_K_M GGUF..."
wget -c --timeout=120 --tries=50 --retry-connrefused \
    "$MODEL_URL" -O "$MODEL_FILE"

echo "Download complete."
ls -lh "$MODEL_FILE"
