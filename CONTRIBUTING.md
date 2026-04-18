# Contributing to mem0-mcp

## Local Setup

1. Install Python 3.11 (matches the runtime Docker image).
2. Clone the repository and create a virtual environment:
   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements-dev.txt
   ```
3. Optional: install `docker` and `docker compose` to run the full stack locally.
4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

## Install Git Hooks

Run once after cloning — this wires the pre-commit and commit-msg hooks under `.githooks/`:

```bash
./scripts/install-hooks.sh
```

## Local Git Setup

Run these once per clone for a saner workflow:

```bash
git config pull.rebase true          # rebase on pull instead of merge commit
git config core.autocrlf input       # normalize CRLF -> LF on commit (macOS/Linux)
git config push.autoSetupRemote true # git push without needing -u the first time
git config init.defaultBranch main   # default branch name for new repos
```

Windows contributors should use `core.autocrlf true` instead of `input`.

## Build and Test Commands

```bash
.venv/bin/python -m pytest --cov --cov-branch      # full test suite + coverage (100% enforced)
.venv/bin/python -m pytest -k <expr>               # run a subset of tests
docker compose up -d                                # run the full Qdrant + MCP stack
docker compose logs -f mem0-mcp                     # tail the server logs
docker compose down                                 # stop the stack
```

## Coding Style

- Follow PEP 8. Use type hints on all public functions.
- Keep files under 200 lines — split helpers into their own modules when approaching the limit.
- Prefer pure functions; isolate side effects (network, filesystem) at the edges.
- No hardcoded secrets, API keys, or absolute host paths in tracked files.
- Conventional Commits are enforced by the `commit-msg` hook.

## Branch Naming

Branch names use kebab-case with a prefix that matches the Conventional Commit type:

| Branch prefix | Conventional Commit type | Example |
|---|---|---|
| `feature/` | `feat:` | `feature/add-prune-tool` |
| `fix/` | `fix:` | `fix/qdrant-host-default` |
| `chore/` | `chore:` | `chore/update-dependencies` |
| `docs/` | `docs:` | `docs/clarify-scoping` |
| `refactor/` | `refactor:` | `refactor/split-scope-helper` |
| `ci/` | `ci:` | `ci/add-dependabot` |

Never commit directly to `main` — always open a PR.

## PR Checklist

- [ ] `pytest --cov` passes locally with 100% coverage.
- [ ] Docker image builds (`docker compose build`) if `app/` changed.
- [ ] Manual test completed for changed functionality.
- [ ] Docs updated if behaviour or configuration changed.
- [ ] No files exceed 200 lines.
