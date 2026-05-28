"""Tests for search_knowledge tool."""
from unittest.mock import patch, MagicMock
from app.tools import search_knowledge


def test_returns_top_k_chunks():
    """search_knowledge calls qdrant and returns formatted chunks."""
    fake_hit = MagicMock()
    fake_hit.payload = {"text": "SageRock builds AI for schools.", "source": "schools.html"}
    fake_hit.score = 0.91

    with patch("app.tools.search_knowledge.qdrant_service") as mock_qdrant, \
         patch("app.tools.search_knowledge.embedding_service") as mock_embed:
        mock_embed.generate_embedding.return_value = [0.1] * 1536
        mock_qdrant.search.return_value = [fake_hit, fake_hit]

        result = search_knowledge.TOOL.run(
            {"query": "What does SageRock do for schools?"},
            {"qdrant": {"collection": "sagerock", "top_k": 3}},
        )

    assert result["chunks"] == [
        {"text": "SageRock builds AI for schools.", "source": "schools.html", "score": 0.91},
        {"text": "SageRock builds AI for schools.", "source": "schools.html", "score": 0.91},
    ]
    mock_qdrant.search.assert_called_once()
    call_kwargs = mock_qdrant.search.call_args.kwargs
    assert call_kwargs["collection_name"] == "sagerock"
    assert call_kwargs["top_k"] == 3


def test_returns_empty_on_qdrant_error():
    """If qdrant raises, tool returns empty chunks rather than crashing."""
    with patch("app.tools.search_knowledge.qdrant_service") as mock_qdrant, \
         patch("app.tools.search_knowledge.embedding_service") as mock_embed:
        mock_embed.generate_embedding.return_value = [0.1] * 1536
        mock_qdrant.search.side_effect = RuntimeError("qdrant down")

        result = search_knowledge.TOOL.run(
            {"query": "anything"},
            {"qdrant": {"collection": "sagerock", "top_k": 5}},
        )

    assert result == {"chunks": [], "error": "qdrant_unavailable"}
