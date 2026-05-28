"""Tests for chat_service tool-use loop."""
from unittest.mock import patch, MagicMock
from app.services.chat_service import ChatService


def _stub_message(content_blocks, stop_reason="end_turn"):
    """Build a fake Anthropic response object."""
    m = MagicMock()
    m.content = content_blocks
    m.stop_reason = stop_reason
    return m


def _text_block(text):
    b = MagicMock()
    b.type = "text"
    b.text = text
    return b


def _tool_use_block(tool_id, name, inputs):
    b = MagicMock()
    b.type = "tool_use"
    b.id = tool_id
    b.name = name
    b.input = inputs
    return b


def test_no_tools_passes_through_to_simple_chat(fake_bot_no_tools):
    """A bot with empty tools_enabled returns a single text response."""
    fake_response = _stub_message([_text_block("Hello!")])

    with patch("app.services.chat_service.Anthropic") as MockAnthropic:
        client = MockAnthropic.return_value
        client.messages.create.return_value = fake_response

        result = ChatService.chat_with_anthropic(fake_bot_no_tools, "hi", [], None, None)

    assert result == "Hello!"
    # tools= should NOT have been passed
    call_kwargs = client.messages.create.call_args.kwargs
    assert "tools" not in call_kwargs or call_kwargs.get("tools") is None


def test_tool_use_loop_executes_tool_and_loops(fake_bot_with_tools):
    """When stop_reason=tool_use, run the tool, send the result back, loop until end_turn."""
    # First call: model wants to call search_knowledge
    first = _stub_message(
        [_tool_use_block("tool_1", "search_knowledge", {"query": "schools"})],
        stop_reason="tool_use",
    )
    # Second call: model returns final text
    second = _stub_message([_text_block("SageRock builds AI for schools.")])

    fake_tool_result = {"chunks": [{"text": "demo", "source": "x", "score": 0.9}]}

    with patch("app.services.chat_service.Anthropic") as MockAnthropic, \
         patch("app.services.chat_service.TOOL_REGISTRY") as mock_registry:
        client = MockAnthropic.return_value
        client.messages.create.side_effect = [first, second]

        mock_tool = MagicMock()
        mock_tool.name = "search_knowledge"
        mock_tool.run.return_value = fake_tool_result
        mock_registry.__getitem__.return_value = mock_tool
        mock_registry.__contains__.return_value = True

        result = ChatService.chat_with_anthropic(
            fake_bot_with_tools, "what about schools?", [], None, None
        )

    assert result == "SageRock builds AI for schools."
    assert client.messages.create.call_count == 2
    mock_tool.run.assert_called_once_with(
        {"query": "schools"},
        fake_bot_with_tools.tool_config,
    )


def test_tool_use_loop_caps_at_max_iterations(fake_bot_with_tools):
    """If the model keeps calling tools forever, we cap at 10 and return what we have."""
    tool_block = _tool_use_block("tool_1", "search_knowledge", {"query": "x"})
    forever = _stub_message([tool_block], stop_reason="tool_use")
    # 11 of these — should hit the cap and stop
    responses = [forever] * 11

    with patch("app.services.chat_service.Anthropic") as MockAnthropic, \
         patch("app.services.chat_service.TOOL_REGISTRY") as mock_registry:
        client = MockAnthropic.return_value
        client.messages.create.side_effect = responses

        mock_tool = MagicMock()
        mock_tool.name = "search_knowledge"
        mock_tool.run.return_value = {"chunks": []}
        mock_registry.__getitem__.return_value = mock_tool
        mock_registry.__contains__.return_value = True

        result = ChatService.chat_with_anthropic(
            fake_bot_with_tools, "loop please", [], None, None
        )

    # Should stop without crashing; result is a graceful fallback string
    assert "couldn't finish" in result.lower() or "trouble" in result.lower()
    assert client.messages.create.call_count == 10
