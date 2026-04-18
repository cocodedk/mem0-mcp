import json
import os

from fastmcp import FastMCP
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": int(os.getenv("QDRANT_PORT", "6333")),
            "collection_name": os.getenv("MEM0_COLLECTION", "mem0_memories"),
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": os.getenv("MEM0_LLM_MODEL", "gpt-4o-mini"),
            "temperature": 0.1,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": os.getenv("MEM0_EMBED_MODEL", "text-embedding-3-small"),
        },
    },
    "history_db_path": "/app/history/history.db",
}

memory = Memory.from_config(config)
mcp = FastMCP("mem0-memory")


def _scope(user_id: str, project: str | None) -> dict:
    scope = {"user_id": user_id}
    if project:
        scope["agent_id"] = project
    return scope


@mcp.tool()
def add_memory(content: str, user_id: str = "default", project: str | None = None) -> str:
    """Store a fact in long-term memory. Pass `project` to isolate per project."""
    result = memory.add(content, **_scope(user_id, project))
    return json.dumps(result, default=str)


@mcp.tool()
def search_memory(
    query: str,
    user_id: str = "default",
    project: str | None = None,
    top_k: int = 5,
) -> str:
    """Semantic search over stored memories. Filter by `project` for per-project results."""
    results = memory.search(query=query, top_k=top_k, filters=_scope(user_id, project))
    return json.dumps(results, default=str)


@mcp.tool()
def list_memories(
    user_id: str = "default",
    project: str | None = None,
    top_k: int = 50,
) -> str:
    """List stored memories for a user, optionally filtered by project."""
    results = memory.get_all(filters=_scope(user_id, project), top_k=top_k)
    return json.dumps(results, default=str)


@mcp.tool()
def delete_memory(memory_id: str) -> str:
    """Delete a specific memory by its id."""
    memory.delete(memory_id)
    return f"Deleted memory {memory_id}"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)
