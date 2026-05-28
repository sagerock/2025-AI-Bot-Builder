"""Base class and types for bot tools.

A tool is a callable the LLM can invoke via Anthropic's tool-use protocol.
Each tool exports:
  - name: str (matches tool_use.name from Anthropic API)
  - schema: dict (JSON Schema for tool input, including a description)
  - run(input_dict, tool_config) -> dict (executes the tool, returns the result)

Tools are pure functions of (input, config). They do NOT touch the database
or session directly. The chat service is responsible for invocation.
"""
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    run: Callable[[dict, dict], dict]

    def to_anthropic_schema(self) -> dict:
        """Return the dict shape Anthropic's tools= parameter expects."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }
