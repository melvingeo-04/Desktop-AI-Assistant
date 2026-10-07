"""
Online AI Provider wrapping Google Gemini.

Wraps the existing robust Gemini implementation (Live API + 9-model ladder in core/gemini.py)
without altering its battle-tested cooldowns, fallbacks, or streaming logic.
"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Optional

from core import gemini as _gemini
from memory.config_manager import get_gemini_key
from .base import AIProvider, ProviderResponse, ProviderStatus, ToolCallRequest


class GeminiProvider(AIProvider):
    """Online Provider wrapping Gemini Live and the Gemini REST ladder."""

    def __init__(self):
        self._key = get_gemini_key() or ""

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_offline(self) -> bool:
        return False

    @property
    def model(self) -> str:
        return _gemini.live_model()

    async def check_health(self) -> ProviderStatus:
        """Check if Gemini API is reachable with the configured key."""
        key = get_gemini_key()
        if not key or len(key) < 15:
            return ProviderStatus(
                available=False,
                provider="gemini",
                model=_gemini.live_model(),
                details="API key not configured",
                error="Missing or invalid Gemini API key in config/api_keys.json",
            )

        # Quick lightweight check via fast tier in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        try:
            res = await loop.run_in_executor(
                None,
                lambda: _gemini.text("ping", tier=_gemini.FAST, timeout_ms=5000, key=key)
            )
            if res:
                return ProviderStatus(
                    available=True,
                    provider="gemini",
                    model=_gemini.live_model(),
                    details=f"Connected ({_gemini.live_model()})",
                )
            return ProviderStatus(
                available=False,
                provider="gemini",
                model=_gemini.live_model(),
                details="No response from Gemini API",
                error="Empty response from Gemini model ladder",
            )
        except Exception as e:
            return ProviderStatus(
                available=False,
                provider="gemini",
                model=_gemini.live_model(),
                details=f"Unreachable: {e}",
                error=str(e),
            )

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 30.0,
    ) -> ProviderResponse:
        """Generate response using the existing core.gemini multi-model ladder."""
        loop = asyncio.get_running_loop()
        timeout_ms = int(timeout_s * 1000)

        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        if tools:
            config["tools"] = [{"function_declarations": tools}]

        def _do_call():
            resp = _gemini.call(
                prompt,
                tier=_gemini.FAST,
                config=config,
                timeout_ms=timeout_ms,
                key=self._key or get_gemini_key(),
            )
            return resp

        resp = await loop.run_in_executor(None, _do_call)
        if resp is None:
            return ProviderResponse(content="I was unable to reach the Gemini service.", raw=None)

        # Extract text & function calls from google-genai response object
        content = getattr(resp, "text", "") or ""
        tool_calls: list[ToolCallRequest] = []

        try:
            if hasattr(resp, "function_calls") and resp.function_calls:
                for fc in resp.function_calls:
                    tool_calls.append(
                        ToolCallRequest(
                            name=getattr(fc, "name", ""),
                            arguments=dict(getattr(fc, "args", {}) or {}),
                            id=getattr(fc, "id", "") or "",
                        )
                    )
        except Exception:
            pass

        return ProviderResponse(content=content, tool_calls=tool_calls, raw=resp)

    async def stream_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 60.0,
    ) -> AsyncGenerator[dict, None]:
        """Gemini Live handles streaming directly; this provides text-fallback streaming."""
        resp = await self.generate_response(prompt, system_instruction, tools, timeout_s)
        yield {
            "text": resp.content,
            "tool_calls": [
                {"name": tc.name, "arguments": tc.arguments, "id": tc.id}
                for tc in resp.tool_calls
            ],
            "is_final": True,
        }
