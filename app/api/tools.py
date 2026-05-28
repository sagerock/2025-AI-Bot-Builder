"""Read-only tools registry endpoint for the admin Help panel."""
from fastapi import APIRouter
from app.tools import TOOL_REGISTRY

router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("")
def list_tools():
    """Return all registered tools with their Anthropic-shaped schema.

    Used by the admin Help panel to render a tool reference that stays in
    sync with whatever is actually registered. No auth required because this
    only exposes tool metadata, not credentials.
    """
    return [tool.to_anthropic_schema() for tool in TOOL_REGISTRY.values()]
