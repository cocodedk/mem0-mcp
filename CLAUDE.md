# CLAUDE.md — mem0-mcp

## Project Overview

mem0-mcp is a Model Context Protocol (MCP) server that exposes mem0ai-backed long-term memory over HTTP. It wraps a local Qdrant vector store and an OpenAI LLM/embedder, presenting four tools — `add_memory`, `search_memory`, `list_memories`, `delete_memory` — to any MCP client.

- **Language / Runtime**: Python 3.11
- **Framework**: FastMCP 2.x + mem0ai + Qdrant
- **Architecture**: single-module MCP server — `app/server.py` owns tool definitions; `tests/` owns the coverage harness with `sys.modules` stubs for `mem0` and `fastmcp` so tests run fully offline.
- **Package / Namespace**: top-level `server` module under `app/`

---

## Required Skills — ALWAYS Invoke These

These skills **must** be invoked when the relevant situation arises. Never skip them.

| Situation | Skill |
|-----------|-------|
| Before any new feature or screen | `superpowers:brainstorming` |
| Planning multi-step changes | `superpowers:writing-plans` |
| Writing or fixing core logic | `superpowers:test-driven-development` |
| First sign of a bug or failure | `superpowers:systematic-debugging` |
| Before completing a feature branch | `superpowers:requesting-code-review` |
| Before claiming any task done | `superpowers:verification-before-completion` |
| Working on UI / frontend | `frontend-design:frontend-design` |
| After implementing — reviewing quality | `simplify` |

---

## Architecture

```
mem0-mcp/
├── app/
│   ├── server.py          # FastMCP tool definitions (<=200 lines)
│   ├── Dockerfile         # Python 3.11-slim runtime image
│   └── requirements.txt   # Runtime deps: mem0ai, fastmcp, openai, qdrant-client
├── tests/
│   ├── conftest.py        # sys.modules stubs for mem0 and fastmcp
│   └── test_server.py     # offline coverage suite (100% enforced)
├── docker-compose.yml     # Qdrant + MCP server, bound to 127.0.0.1
├── pyproject.toml         # pytest + coverage config (fail_under = 100)
└── version.txt            # MAJOR.MINOR.PATCH
```

### Layer Rules

- `app/server.py` must stay under 200 lines. Split helpers out if growth is needed.
- Tests never hit the network — all third-party imports are stubbed in `tests/conftest.py`.
- CI installs only `requirements-dev.txt`. Runtime deps (`mem0ai`, `fastmcp`, `qdrant-client`) are not needed for tests and are deliberately skipped.

---

## Coding Conventions

- [ ] Use type hints on all public functions.
- [ ] Prefer pure helpers; keep side-effectful code (mem0, network) at the edges.
- [ ] No hardcoded strings for configuration — read from env with safe defaults.
- [ ] No absolute host paths (`/home/...`) in tracked files.
- [ ] Follow PEP 8; format with whatever tool the project standardises on (none required today).

---

## Engineering Principles

### File Size

- **200-line maximum per file** — extract a module or helper when approaching the limit.

### DRY · SOLID · KISS · YAGNI

- Extract shared logic into named utilities; never copy-paste.
- Single Responsibility: one function does one thing.
- Don't add features not yet needed.
- Delete dead code immediately.

### TDD

- Write the failing test first, make it pass, then refactor.
- Tests stub `mem0` / `fastmcp` via `sys.modules`; keep that pattern when adding new third-party integrations.
- 100% branch coverage is enforced in `pyproject.toml` (`fail_under = 100`). A drop will fail CI.

### Commit hygiene

- Follow Conventional Commits: `feat: ...` / `fix: ...` / `chore: ...`.
- The `commit-msg` hook enforces this automatically.

---

## Build Commands

```bash
.venv/bin/python -m pytest --cov --cov-branch     # run tests + coverage (smoke)
.venv/bin/python -m pytest -q                      # quick run without coverage
docker compose up -d                                # run the full stack locally
docker compose build                                # rebuild the server image
```

---

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file — project conventions and session startup |
| `version.txt` | Semantic version (MAJOR.MINOR.PATCH) |
| `app/server.py` | FastMCP tool definitions — the entire server |
| `app/Dockerfile` | Runtime image (Python 3.11-slim) |
| `docker-compose.yml` | Qdrant + MCP server wiring, bound to 127.0.0.1 |
| `pyproject.toml` | pytest + coverage config (100% threshold) |
| `tests/conftest.py` | sys.modules stubs that keep tests offline |
| `.github/workflows/ci.yml` | PR + push verification (pytest + coverage) |
| `.github/workflows/publish-container.yml` | Builds and pushes to `ghcr.io/cocodedk/mem0-mcp` |
| `.githooks/pre-commit` | Runs pytest before every commit |
| `.githooks/commit-msg` | Enforces Conventional Commits |
| `scripts/install-hooks.sh` | One-time hook installer |
| `scripts/setup-repo.sh` | One-time branch-protection + merge-settings applier |

---

## Starting a New Session

1. Read this file.
2. Run `.venv/bin/python -m pytest --cov --cov-branch` to confirm everything passes.
3. Invoke `superpowers:brainstorming` before touching any feature.
4. Follow the Required Skills table — every skill is mandatory, not optional.
