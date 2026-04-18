"""Stub out `mem0` and `fastmcp` so importing `server` does not touch the network."""
from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import MagicMock

import pytest


def _install_stub_modules() -> MagicMock:
    """Install dummy `mem0` and `fastmcp` modules in sys.modules.

    Returns the `Memory` class mock so callers can inspect the instance
    produced by `Memory.from_config(...)`.
    """
    # --- mem0 stub ---
    mem0_mod = types.ModuleType("mem0")
    memory_cls = MagicMock(name="MemoryClass")
    # Each call to `Memory.from_config(...)` returns a fresh mock instance
    # so tests can assert against `.add / .search / .get_all / .delete`.
    memory_cls.from_config.side_effect = lambda _cfg: MagicMock(name="MemoryInstance")
    mem0_mod.Memory = memory_cls
    sys.modules["mem0"] = mem0_mod

    # --- fastmcp stub ---
    fastmcp_mod = types.ModuleType("fastmcp")

    class FakeFastMCP:
        def __init__(self, name: str) -> None:
            self.name = name
            self.run = MagicMock(name="FakeFastMCP.run")
            self.registered: list = []

        def tool(self):
            def decorator(fn):
                self.registered.append(fn)
                return fn

            return decorator

    fastmcp_mod.FastMCP = FakeFastMCP
    sys.modules["fastmcp"] = fastmcp_mod
    return memory_cls


@pytest.fixture
def fresh_server(monkeypatch):
    """Import `server` fresh with optional env overrides.

    Returns a (server_module, memory_instance, fastmcp_instance) tuple.
    """

    def _factory(env: dict[str, str] | None = None):
        for key, value in (env or {}).items():
            monkeypatch.setenv(key, value)
        _install_stub_modules()
        sys.modules.pop("server", None)
        sys.modules.pop("app.server", None)
        module = importlib.import_module("server")
        return module, module.memory, module.mcp

    return _factory


@pytest.fixture
def server(fresh_server):
    """Default server import using default env vars."""
    module, mem, mcp = fresh_server()
    return module


@pytest.fixture
def mock_memory(server):
    """Expose the memory mock attached to the imported server module."""
    return server.memory
