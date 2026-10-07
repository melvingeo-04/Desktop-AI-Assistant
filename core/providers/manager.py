"""
AI Provider Manager for JARVIS.

Orchestrates AUTO, ONLINE, and OFFLINE modes with non-blocking cached connectivity checks,
graceful fallbacks, and state transition signals for the UI.
"""
from __future__ import annotations

import asyncio
import socket
import time
from typing import Callable, Optional

from memory.config_manager import (
    get_ai_mode,
    save_ai_mode,
)
from .base import AIProvider, ProviderStatus
from .online_provider import GeminiProvider
from .offline_provider import OllamaProvider


class ProviderManager:
    """Manages AI provider switching, health checking, and mode transitions."""

    def __init__(self, on_status_change: Optional[Callable[[str, str, str], None]] = None):
        """
        on_status_change callback signature:
            callback(mode: str, active_provider: str, status_text: str)
        """
        self._online_provider = GeminiProvider()
        self._offline_provider = OllamaProvider()
        self._on_status_change = on_status_change

        self._active_mode: str = get_ai_mode()  # "AUTO" | "ONLINE" | "OFFLINE"
        self._resolved_provider_name: str = "ollama" if self._active_mode == "OFFLINE" else "gemini"

        # Cooldown & caching for connectivity checks
        self._last_conn_check_time: float = 0.0
        self._cached_internet_available: bool = True
        self._cached_gemini_healthy: bool = True
        self._cached_ollama_healthy: bool = False
        self._check_cooldown: float = 15.0  # seconds between background checks
        self._status_text: str = "Initializing..."
        self._update_state()

    @property
    def active_mode(self) -> str:
        return self._active_mode

    @property
    def active_provider_name(self) -> str:
        return self._resolved_provider_name

    @property
    def active_provider(self) -> AIProvider:
        if self._active_mode == "OFFLINE" or self._resolved_provider_name == "ollama":
            return self._offline_provider
        return self._online_provider

    @property
    def is_currently_offline(self) -> bool:
        return self._resolved_provider_name == "ollama"

    def set_mode(self, mode: str) -> None:
        """Switch mode manually to AUTO, ONLINE, or OFFLINE."""
        m = mode.strip().upper()
        if m in ("AUTO", "ONLINE", "OFFLINE"):
            self._active_mode = m
            save_ai_mode(m)
            # Invalidate cache to force immediate evaluation
            self._last_conn_check_time = 0.0
            self._update_state()

    def _quick_check_internet(self, timeout: float = 2.0) -> bool:
        """Lightweight socket check to a public DNS server (1.1.1.1:53)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(("1.1.1.1", 53))
            sock.close()
            return True
        except Exception:
            return False

    async def check_connectivity(self, force: bool = False) -> tuple[bool, ProviderStatus, ProviderStatus]:
        """
        Non-blocking health & connectivity assessment with caching.
        Returns: (internet_ok, gemini_status, ollama_status)
        """
        now = time.monotonic()
        if not force and (now - self._last_conn_check_time) < self._check_cooldown:
            return (
                self._cached_internet_available,
                ProviderStatus(self._cached_gemini_healthy, "gemini", ""),
                ProviderStatus(self._cached_ollama_healthy, "ollama", ""),
            )

        self._last_conn_check_time = now
        loop = asyncio.get_running_loop()

        # 1. Internet socket check in executor
        internet_ok = await loop.run_in_executor(None, self._quick_check_internet)
        self._cached_internet_available = internet_ok

        # 2. Check providers
        gemini_status = await self._online_provider.check_health() if internet_ok else ProviderStatus(
            available=False, provider="gemini", model="", details="No internet connection", error="Offline"
        )
        self._cached_gemini_healthy = gemini_status.available

        ollama_status = await self._offline_provider.check_health()
        self._cached_ollama_healthy = ollama_status.available

        self._update_state(gemini_status, ollama_status)
        return internet_ok, gemini_status, ollama_status

    def _update_state(
        self,
        gemini_status: Optional[ProviderStatus] = None,
        ollama_status: Optional[ProviderStatus] = None,
    ) -> None:
        """Resolve which provider should be active based on mode and health."""
        mode = self._active_mode
        g_avail = gemini_status.available if gemini_status else self._cached_gemini_healthy
        o_avail = ollama_status.available if ollama_status else self._cached_ollama_healthy
        net_ok = self._cached_internet_available

        if mode == "ONLINE":
            self._resolved_provider_name = "gemini"
            if not net_ok:
                self._status_text = "ONLINE ⚠ No internet connection"
            elif not g_avail:
                self._status_text = "ONLINE ⚠ Gemini API unavailable"
            else:
                self._status_text = "ONLINE ● Gemini Connected"

        elif mode == "OFFLINE":
            self._resolved_provider_name = "ollama"
            if o_avail:
                self._status_text = f"OFFLINE ● Local Ollama ({self._offline_provider.model})"
            else:
                self._status_text = "OFFLINE ⚠ Ollama not running"

        else:  # AUTO
            if net_ok and g_avail:
                self._resolved_provider_name = "gemini"
                self._status_text = "AUTO ● Online (Gemini Live)"
            elif o_avail:
                self._resolved_provider_name = "ollama"
                reason = "No internet" if not net_ok else "Gemini offline"
                self._status_text = f"AUTO ● Fallback to Ollama ({reason})"
            else:
                self._resolved_provider_name = "gemini"
                self._status_text = "AUTO ⚠ Both Gemini & Ollama unavailable"

        if self._on_status_change:
            try:
                self._on_status_change(self._active_mode, self._resolved_provider_name, self._status_text)
            except Exception:
                pass

    def get_status_summary(self) -> dict:
        return {
            "mode": self._active_mode,
            "active_provider": self._resolved_provider_name,
            "status_text": self._status_text,
            "internet_ok": self._cached_internet_available,
            "gemini_ok": self._cached_gemini_healthy,
            "ollama_ok": self._cached_ollama_healthy,
        }
