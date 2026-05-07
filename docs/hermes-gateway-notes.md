# Hermes Gateway Notes

## Architecture (Mac Mini)
- Hermes agent: standalone container (debian:13.4, Python 3.11, uv)
- Entrypoint: docker/entrypoint.sh — dir structure, config bootstrap, privilege drop
- API: HTTP on port 8642 (Hermes API) and 8765 (Gateway)
- GitHub: SSH key auth (paulrydberg), gh CLI configured

## Patterns Reused
- Multi-stage Docker build
- docker-compose.yml at project root
- Python FastAPI (not Node.js)
- SSH key auth for GitHub
- Subprocess llama.cpp integration
