# mem0-mcp

A Model Context Protocol (MCP) server that wraps [mem0ai](https://github.com/mem0ai/mem0) with a local [Qdrant](https://qdrant.tech) vector store, exposing long-term memory tools (`add_memory`, `search_memory`, `list_memories`, `delete_memory`) to any MCP-aware client over HTTP. Built with [FastMCP](https://gofastmcp.com) on Python 3.11 and shipped as a Docker image.

## Website

- [English](https://cocodedk.github.io/mem0-mcp/)
- [فارسی (Persian)](https://cocodedk.github.io/mem0-mcp/fa/)

## Docker

The fastest way to run mem0-mcp is via `docker compose`. It launches Qdrant and the MCP server side-by-side, binding to `127.0.0.1:8888`.

```bash
cp .env.example .env        # then edit OPENAI_API_KEY
docker compose up -d
```

The MCP endpoint is then reachable at `http://127.0.0.1:8888/mcp`.

Prebuilt images are published to GHCR on every push to `main`:

```bash
docker pull ghcr.io/cocodedk/mem0-mcp:latest
```

## Features

- Persistent semantic memory via mem0ai + Qdrant
- MCP HTTP server exposing four tools: add, search, list, delete
- Per-user (`user_id`) and per-project (`project`) scoping of memories
- Configurable LLM and embedding models (OpenAI by default)
- Runs fully local — only outbound call is to the configured LLM/embedder
- 100% test coverage enforced in CI

## Build from Source

Requirements: Python 3.11, Docker (optional, for the full stack).

```bash
git clone https://github.com/cocodedk/mem0-mcp.git
cd mem0-mcp
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest --cov
```

Tests stub `mem0` and `fastmcp` via `sys.modules` so they run fully offline. The `pyproject.toml` enforces `fail_under = 100` on coverage.

To run the server locally without Docker, install the runtime dependencies from `app/requirements.txt` and launch `python app/server.py`.

## Architecture

```
mem0-mcp/
├── app/
│   ├── server.py          # FastMCP tool definitions
│   ├── Dockerfile         # Python 3.11-slim runtime image
│   └── requirements.txt   # Runtime deps (mem0ai, fastmcp, qdrant-client)
├── tests/                 # Offline test suite (sys.modules stubs)
├── docker-compose.yml     # Qdrant + MCP server
└── pyproject.toml         # pytest + coverage config
```

Stack: Python 3.11 · FastMCP · mem0ai · Qdrant · Docker

## Configuration

Configuration comes from environment variables, typically loaded via `.env`.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Required. API key used by mem0 for LLM + embeddings. |
| `MEM0_LLM_MODEL` | `gpt-4o-mini` | OpenAI chat model used for memory extraction. |
| `MEM0_EMBED_MODEL` | `text-embedding-3-small` | OpenAI embedding model. |
| `MEM0_COLLECTION` | `mem0_memories` | Qdrant collection name. |
| `QDRANT_HOST` | `localhost` | Qdrant host (`qdrant` in compose). |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port. |

See `.env.example` for a template.

## Security

The MCP endpoint is unauthenticated. Keep the `127.0.0.1:` prefix in `docker-compose.yml`. Never expose port 8888 publicly. If remote access is needed, put the server behind an authenticating reverse proxy (Caddy, Traefik, or similar) on a private network.

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## Author

**Babak Bandpey** — [cocode.dk](https://cocode.dk) | [LinkedIn](https://linkedin.com/in/babakbandpey) | [GitHub](https://github.com/cocodedk)

## License

Apache-2.0 | © 2026 [Cocode](https://cocode.dk) | Created by [Babak Bandpey](https://linkedin.com/in/babakbandpey)
