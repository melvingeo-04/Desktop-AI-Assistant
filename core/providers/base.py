"""
Abstract base class and data structures for AI providers.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional, Any


@dataclass
class ProviderStatus:
    available: bool
    provider: str
    model: str
    details: str = ""
    error: Optional[str] = None


@dataclass
class ToolCallRequest:
    name: str
    arguments: dict = field(default_factory=dict)
    id: str = ""


@dataclass
class ProviderResponse:
    content: str = ""
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    raw: Any = None


class AIProvider(ABC):
    """Base interface for all JARVIS AI providers (Online & Offline)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier: 'gemini' or 'ollama'."""
        pass

    @property
    @abstractmethod
    def is_offline(self) -> bool:
        """True if this provider runs fully locally without external network."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Name of the model in use."""
        pass

    @abstractmethod
    async def check_health(self) -> ProviderStatus:
        """Check if provider and model are currently reachable and responsive."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 30.0,
    ) -> ProviderResponse:
        """Generate a response, returning text and/or structured tool calls."""
        pass

    @abstractmethod
    async def stream_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 60.0,
    ) -> AsyncGenerator[dict, None]:
        """Stream chunks of response. Yields dicts with 'text' and/or 'tool_calls'."""
        pass
