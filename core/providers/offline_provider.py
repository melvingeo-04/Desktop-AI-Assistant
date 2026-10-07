"""
Offline AI Provider using Ollama for local LLM inference.

Provides non-blocking connectivity checks, model verification, tool-calling support,
and graceful degradation without ever crashing the assistant.
"""
from __future__ import annotations

import asyncio
import json
import re
import urllib.parse
from typing import AsyncGenerator, Optional

import requests

from memory.config_manager import (
    get_ollama_host,
    get_ollama_model,
)
from .base import AIProvider, ProviderResponse, ProviderStatus, ToolCallRequest


class OllamaProvider(AIProvider):
    """Local offline AI provider communicating with Ollama REST API."""

    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        self._host = (host or get_ollama_host()).rstrip("/")
        self._explicit_model = model
        self._model = model or get_ollama_model()

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def is_offline(self) -> bool:
        return True

    @property
    def host(self) -> str:
        return (get_ollama_host() or self._host).rstrip("/")

    @property
    def model(self) -> str:
        if self._explicit_model:
            return self._explicit_model
        return get_ollama_model() or self._model

    async def check_health(self) -> ProviderStatus:
        """
        Check:
        1. Ollama server is reachable on host/port
        2. Configured model is pulled
        3. Returns clean actionable status
        """
        loop = asyncio.get_running_loop()
        url = self.host
        model = self.model

        def _check():
            # 1. Ping /api/tags
            try:
                resp = requests.get(f"{url}/api/tags", timeout=3)
                if resp.status_code != 200:
                    return ProviderStatus(
                        available=False,
                        provider="ollama",
                        model=model,
                        details="Ollama responded with error",
                        error=f"HTTP {resp.status_code}",
                    )
            except requests.exceptions.ConnectionError:
                return ProviderStatus(
                    available=False,
                    provider="ollama",
                    model=model,
                    details="Offline AI unavailable — Ollama is not running",
                    error="Start Ollama to use Offline mode.",
                )
            except Exception as e:
                return ProviderStatus(
                    available=False,
                    provider="ollama",
                    model=model,
                    details=f"Ollama unreachable: {e}",
                    error=str(e),
                )

            # 2. Check model existence
            try:
                models_data = resp.json().get("models", [])
                pulled_names = [m.get("name", "") for m in models_data]
                base_model = model.split(":")[0].lower().replace(" ", "").replace(".", "")

                matched_model = None
                for m in pulled_names:
                    m_clean = m.lower().replace(" ", "").replace(".", "")
                    if (
                        m.lower() == model.lower()
                        or m.lower().startswith(model.lower())
                        or base_model in m_clean
                        or m_clean in base_model
                    ):
                        matched_model = m
                        break

                if not matched_model and pulled_names:
                    # Auto-fallback to first available model installed in Ollama
                    matched_model = pulled_names[0]
                    print(f"[Ollama] Model '{model}' not found, auto-selected installed '{matched_model}'")

                if not matched_model:
                    avail_str = ", ".join(pulled_names) if pulled_names else "none"
                    return ProviderStatus(
                        available=False,
                        provider="ollama",
                        model=model,
                        details="No suitable model found in Ollama",
                        error=f"Available: {avail_str}. Run 'ollama pull {model}'.",
                    )

                self._model = matched_model
                return ProviderStatus(
                    available=True,
                    provider="ollama",
                    model=matched_model,
                    details=f"Local Ollama ready ({matched_model})",
                )
            except Exception:
                pass

        return await loop.run_in_executor(None, _check)

    def _convert_tools_for_ollama(self, tools: list[dict]) -> list[dict]:
        """Convert standard Gemini/OpenAI tool format into Ollama /api/chat tool schema."""
        ollama_tools = []
        for t in tools:
            name = t.get("name", "")
            desc = t.get("description", "")
            params = t.get("parameters", {})
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": desc,
                    "parameters": params,
                }
            })
        return ollama_tools

    def _parse_content_for_tools(self, text: str) -> tuple[str, list[ToolCallRequest]]:
        """
        Fallback parser for local models that output markdown code blocks with JSON
        like: ```json {"tool": "open_app", "arguments": {"app_name": "notepad"}} ```
        """
        tool_calls: list[ToolCallRequest] = []
        clean_text = text

        patterns = [
            r"```(?:json)?\s*(\{\s*\"tool\"\s*:\s*\"[^\"]+\".*?\})\s*```",
            r"```(?:json)?\s*(\{\s*\"function\"\s*:\s*\"[^\"]+\".*?\})\s*```",
            r"(\{\s*\"tool\"\s*:\s*\"[a-zA-Z_0-9]+\"\s*,\s*\"arguments\"\s*:\s*\{.*?\}\s*\})",
        ]

        for pat in patterns:
            for match in re.finditer(pat, clean_text, re.DOTALL):
                try:
                    data = json.loads(match.group(1))
                    t_name = data.get("tool") or data.get("function")
                    t_args = data.get("arguments", {})
                    if t_name:
                        tool_calls.append(ToolCallRequest(name=t_name, arguments=t_args))
                        clean_text = clean_text.replace(match.group(0), "").strip()
                except Exception:
                    continue

        return clean_text, tool_calls

    async def generate_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 45.0,
    ) -> ProviderResponse:
        """Call Ollama /api/chat with optional tools and system instruction."""
        loop = asyncio.get_running_loop()
        url = self.host
        model = self.model

        messages = []
        if system_instruction:
            # Instruct local model about structured tool calling format
            tool_guide = (
                "\nWhen executing actions, call the appropriate tool. "
                "Do not simulate actions or make up command output."
            )
            messages.append({"role": "system", "content": system_instruction + tool_guide})
        messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": 400,
                "temperature": 0.3,
            },
        }

        if tools:
            payload["tools"] = self._convert_tools_for_ollama(tools)

        def _request():
            try:
                resp = requests.post(f"{url}/api/chat", json=payload, timeout=timeout_s)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.ConnectionError:
                return {"error": "Ollama server connection failed."}
            except requests.exceptions.Timeout:
                return {"error": "Ollama request timed out."}
            except Exception as e:
                return {"error": str(e)}

        data = await loop.run_in_executor(None, _request)

        if "error" in data:
            return ProviderResponse(
                content=f"Sir, offline AI failed: {data['error']}",
                raw=data,
            )

        msg = data.get("message", {})
        raw_text = (msg.get("content") or "").strip()
        raw_tools = msg.get("tool_calls") or []

        tool_calls: list[ToolCallRequest] = []
        for rt in raw_tools:
            fn = rt.get("function", {})
            name = fn.get("name", "")
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    args = {}
            if name:
                tool_calls.append(ToolCallRequest(name=name, arguments=args))

        # If thinking consumed tokens and content is empty, extract final spoken phrase
        if not raw_text and not tool_calls and msg.get("thinking"):
            thinking_text = msg.get("thinking", "").strip()
            quotes = re.findall(r'"([^"\n]{4,150})"', thinking_text)
            if quotes:
                raw_text = quotes[-1]
            else:
                lines = [l.strip() for l in thinking_text.splitlines() if l.strip()]
                if lines:
                    raw_text = lines[-1]

        # Check for inline text tool blocks if native tool calls were empty
        if not tool_calls and raw_text:
            raw_text, extracted = self._parse_content_for_tools(raw_text)
            tool_calls.extend(extracted)

        return ProviderResponse(content=raw_text, tool_calls=tool_calls, raw=data)

    async def stream_response(
        self,
        prompt: str,
        system_instruction: str = "",
        tools: Optional[list[dict]] = None,
        timeout_s: float = 60.0,
    ) -> AsyncGenerator[dict, None]:
        """Stream chunks from Ollama /api/chat."""
        url = self.host
        model = self.model

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"num_predict": 300},
        }
        if tools:
            payload["tools"] = self._convert_tools_for_ollama(tools)

        def _start_stream():
            return requests.post(f"{url}/api/chat", json=payload, stream=True, timeout=timeout_s)

        loop = asyncio.get_running_loop()
        try:
            resp = await loop.run_in_executor(None, _start_stream)
            resp.raise_for_status()
        except Exception as e:
            yield {
                "text": f"Sir, offline AI is currently unreachable: {e}",
                "tool_calls": [],
                "is_final": True,
            }
            return

        accumulated_text = ""
        accumulated_tools: list[dict] = []

        try:
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    msg = chunk.get("message", {})
                    token = msg.get("content", "")
                    done = chunk.get("done", False)

                    t_calls = msg.get("tool_calls", [])
                    if t_calls:
                        for tc in t_calls:
                            fn = tc.get("function", {})
                            accumulated_tools.append({
                                "name": fn.get("name", ""),
                                "arguments": fn.get("arguments", {}),
                            })

                    if token:
                        accumulated_text += token
                        yield {
                            "text": token,
                            "tool_calls": [],
                            "is_final": done,
                        }

                    if done:
                        # Final check for inline tool blocks
                        if not accumulated_tools and accumulated_text:
                            _, extracted = self._parse_content_for_tools(accumulated_text)
                            for tc in extracted:
                                accumulated_tools.append({
                                    "name": tc.name,
                                    "arguments": tc.arguments,
                                })

                        yield {
                            "text": "",
                            "tool_calls": accumulated_tools,
                            "is_final": True,
                        }
                        break
                except Exception:
                    continue
        except Exception as e:
            yield {
                "text": f"\n[Stream interrupted: {e}]",
                "tool_calls": [],
                "is_final": True,
            }
