#!/bin/bash
# Run the pre-1931 historical agent directly with llama.cpp
set -e

MODEL="models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
PROMPT="${1:-"Explain what electricity is."}"
TEMP="${2:-0.3}"
TOKENS="${3:-200}"

if [ ! -f "$MODEL" ]; then
    echo "Error: Model not found at $MODEL"
    echo "Run ./scripts/download_model.sh first"
    exit 1
fi

LLAMA_CLI="llama-cli"
if [ -f "./llama.cpp/build/bin/llama-cli" ]; then
    LLAMA_CLI="./llama.cpp/build/bin/llama-cli"
fi

SYSTEM_PROMPT="You are a historical reasoning model. Your knowledge is limited to the period before 1931. Do NOT reference events, inventions, or knowledge after 1930. Do NOT use modern terminology such as: computer, internet, AI, transistor, quantum computing, nuclear weapon, smartphone, machine learning, digital, semiconductor, satellite, GPS. Prefer 19th and early 20th century framing for all explanations. If a concept lies outside pre-1931 knowledge, say: This matter lies beyond the knowledge available in the present era."

FULL_PROMPT="$SYSTEM_PROMPT

User query: $PROMPT

Historical analysis:"

echo "=== Model: Qwen 2.5 7B Q4_K_M ==="
echo "=== Temperature: $TEMP ==="
echo "=== Max tokens: $TOKENS ==="
echo ""
echo "Query: $PROMPT"
echo "---"

$LLAMA_CLI \
    -m "$MODEL" -n "$TOKENS" -ngl 0 \
    --no-conversation --temp "$TEMP" \
    -p "$FULL_PROMPT" \
    2>/dev/null | strings | grep -vE '^\s*>\s*$|^$|build:|model |modalities|available|/exit|/regen|/clear|/read|Prompt:|Generation:|Exiting'
