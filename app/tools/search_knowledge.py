"""search_knowledge tool: RAG over a Qdrant collection."""
import logging
from app.tools.base import Tool
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


def run(inputs: dict, config: dict) -> dict:
    """Search the configured Qdrant collection for the query.

    inputs: {"query": str}
    config: {"qdrant": {"collection": str, "top_k": int}}
    returns: {"chunks": [{"text": str, "source": str, "score": float}, ...]}
             or {"chunks": [], "error": "qdrant_unavailable"} on failure
    """
    query = inputs.get("query", "").strip()
    qdrant_cfg = config.get("qdrant", {})
    collection = qdrant_cfg.get("collection")
    top_k = qdrant_cfg.get("top_k", 5)

    if not query or not collection:
        return {"chunks": []}

    try:
        embedding = embedding_service.generate_embedding(query)
        hits = qdrant_service.search(
            collection_name=collection,
            query_vector=embedding,
            top_k=top_k,
        )
    except Exception as e:
        logger.warning(f"search_knowledge: qdrant search failed: {e}")
        return {"chunks": [], "error": "qdrant_unavailable"}

    chunks = []
    for hit in hits:
        payload = getattr(hit, "payload", {}) or {}
        chunks.append({
            "text": payload.get("text", ""),
            "source": payload.get("source", ""),
            "score": getattr(hit, "score", 0.0),
        })
    return {"chunks": chunks}


TOOL = Tool(
    name="search_knowledge",
    description=(
        "Search SageRock's knowledge base for information relevant to the user's question. "
        "Use when the user asks about SageRock's services, history, pricing approach, or any "
        "specific product. Returns ranked text chunks with source URLs."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A search query phrased like a question or topic.",
            }
        },
        "required": ["query"],
    },
    run=run,
)
