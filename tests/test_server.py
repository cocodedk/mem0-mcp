"""Full line + branch coverage for app/server.py."""
from __future__ import annotations

import json
import runpy
import sys
from datetime import datetime
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# _scope
# ---------------------------------------------------------------------------
def test_scope_without_project(server):
    assert server._scope("alice", None) == {"user_id": "alice"}


def test_scope_with_project(server):
    assert server._scope("alice", "proj") == {
        "user_id": "alice",
        "agent_id": "proj",
    }


def test_scope_with_empty_project_falsy(server):
    # Empty string is falsy → agent_id must NOT be set.
    assert server._scope("alice", "") == {"user_id": "alice"}


# ---------------------------------------------------------------------------
# add_memory
# ---------------------------------------------------------------------------
def test_add_memory_default(server, mock_memory):
    mock_memory.add.return_value = {"id": "m1", "event": "ADD"}
    result = server.add_memory("hello world")
    mock_memory.add.assert_called_once_with("hello world", user_id="default")
    assert json.loads(result) == {"id": "m1", "event": "ADD"}


def test_add_memory_with_project(server, mock_memory):
    mock_memory.add.return_value = [{"id": "m2"}]
    result = server.add_memory("note", user_id="bb", project="mem0-mcp")
    mock_memory.add.assert_called_once_with(
        "note", user_id="bb", agent_id="mem0-mcp"
    )
    assert json.loads(result) == [{"id": "m2"}]


def test_add_memory_non_json_safe_return(server, mock_memory):
    # Datetime is not JSON serializable → exercises `default=str`.
    mock_memory.add.return_value = {"at": datetime(2026, 1, 1, 12, 0, 0)}
    result = server.add_memory("hello")
    payload = json.loads(result)
    assert payload["at"].startswith("2026-01-01")


# ---------------------------------------------------------------------------
# search_memory
# ---------------------------------------------------------------------------
def test_search_memory_default(server, mock_memory):
    mock_memory.search.return_value = {"results": []}
    result = server.search_memory("needle")
    mock_memory.search.assert_called_once_with(
        query="needle", top_k=5, filters={"user_id": "default"}
    )
    assert json.loads(result) == {"results": []}


def test_search_memory_with_project_and_top_k(server, mock_memory):
    mock_memory.search.return_value = [{"id": "x"}]
    result = server.search_memory(
        "needle", user_id="bb", project="proj", top_k=7
    )
    mock_memory.search.assert_called_once_with(
        query="needle",
        top_k=7,
        filters={"user_id": "bb", "agent_id": "proj"},
    )
    assert json.loads(result) == [{"id": "x"}]


def test_search_memory_non_json_safe_return(server, mock_memory):
    mock_memory.search.return_value = {"ts": datetime(2026, 4, 18)}
    result = server.search_memory("q")
    assert "2026-04-18" in json.loads(result)["ts"]


# ---------------------------------------------------------------------------
# list_memories
# ---------------------------------------------------------------------------
def test_list_memories_default(server, mock_memory):
    mock_memory.get_all.return_value = []
    result = server.list_memories()
    mock_memory.get_all.assert_called_once_with(
        filters={"user_id": "default"}, top_k=50
    )
    assert json.loads(result) == []


def test_list_memories_with_project_and_top_k(server, mock_memory):
    mock_memory.get_all.return_value = [{"id": 1}]
    result = server.list_memories(user_id="bb", project="p", top_k=3)
    mock_memory.get_all.assert_called_once_with(
        filters={"user_id": "bb", "agent_id": "p"}, top_k=3
    )
    assert json.loads(result) == [{"id": 1}]


# ---------------------------------------------------------------------------
# delete_memory
# ---------------------------------------------------------------------------
def test_delete_memory(server, mock_memory):
    result = server.delete_memory("abc-123")
    mock_memory.delete.assert_called_once_with("abc-123")
    assert result == "Deleted memory abc-123"


# ---------------------------------------------------------------------------
# Module-level config construction
# ---------------------------------------------------------------------------
def test_config_defaults(server):
    cfg = server.config
    assert cfg["vector_store"]["config"]["host"] == "localhost"
    assert cfg["vector_store"]["config"]["port"] == 6333
    assert cfg["vector_store"]["config"]["collection_name"] == "mem0_memories"
    assert cfg["llm"]["config"]["model"] == "gpt-4o-mini"
    assert cfg["llm"]["config"]["temperature"] == 0.1
    assert cfg["embedder"]["config"]["model"] == "text-embedding-3-small"
    assert cfg["history_db_path"] == "/app/history/history.db"
    assert server.mcp.name == "mem0-memory"


def test_config_env_overrides(fresh_server):
    module, _mem, _mcp = fresh_server(
        env={
            "QDRANT_HOST": "qdrant.internal",
            "QDRANT_PORT": "7001",
            "MEM0_COLLECTION": "custom_mem",
            "MEM0_LLM_MODEL": "gpt-5",
            "MEM0_EMBED_MODEL": "text-embedding-4",
        }
    )
    cfg = module.config
    assert cfg["vector_store"]["config"]["host"] == "qdrant.internal"
    assert cfg["vector_store"]["config"]["port"] == 7001
    assert cfg["vector_store"]["config"]["collection_name"] == "custom_mem"
    assert cfg["llm"]["config"]["model"] == "gpt-5"
    assert cfg["embedder"]["config"]["model"] == "text-embedding-4"


# ---------------------------------------------------------------------------
# `if __name__ == "__main__"` block
# ---------------------------------------------------------------------------
def test_main_block_invokes_mcp_run(monkeypatch):
    """Execute server.py as __main__ to cover the entrypoint line."""
    # Re-install stubs (conftest helper is scoped to fixtures, so inline here).
    import types
    from unittest.mock import MagicMock

    mem0_mod = types.ModuleType("mem0")
    memory_cls = MagicMock()
    memory_cls.from_config.side_effect = lambda _cfg: MagicMock()
    mem0_mod.Memory = memory_cls
    sys.modules["mem0"] = mem0_mod

    fastmcp_mod = types.ModuleType("fastmcp")
    captured = {}

    class CapturingFastMCP:
        def __init__(self, name):
            self.name = name
            captured["instance"] = self

        def tool(self):
            return lambda fn: fn

        def run(self, **kwargs):
            captured["run_kwargs"] = kwargs

    fastmcp_mod.FastMCP = CapturingFastMCP
    sys.modules["fastmcp"] = fastmcp_mod

    # Drop any cached import so runpy re-executes from source.
    sys.modules.pop("server", None)
    sys.modules.pop("app.server", None)

    runpy.run_module("server", run_name="__main__")

    assert captured["run_kwargs"] == {
        "transport": "http",
        "host": "0.0.0.0",
        "port": 8080,
    }
