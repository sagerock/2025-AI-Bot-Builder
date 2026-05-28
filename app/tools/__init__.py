"""Tool registry. Import this module to access all registered tools."""
from app.tools.base import Tool
from app.tools import search_knowledge  # noqa: F401

# As tools are added in later tasks, import them above this line and add to REGISTRY below.
TOOL_REGISTRY: dict[str, Tool] = {
    search_knowledge.TOOL.name: search_knowledge.TOOL,
}


def get_tools_for_bot(tool_names: list[str]) -> list[Tool]:
    """Return Tool objects for the given names, in registry order. Unknown names skipped."""
    return [TOOL_REGISTRY[n] for n in tool_names if n in TOOL_REGISTRY]


def get_anthropic_schemas(tool_names: list[str]) -> list[dict]:
    """Return Anthropic-shaped tool schemas for the given names."""
    return [t.to_anthropic_schema() for t in get_tools_for_bot(tool_names)]
