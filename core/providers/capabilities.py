"""
Capability detection and classification for JARVIS tools.

Ensures that tools requiring internet connectivity fail gracefully when in OFFLINE mode
with informative, respectful feedback instead of crashing or hanging on network requests.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class CapabilityType(Enum):
    LOCAL = "LOCAL"
    ONLINE_REQUIRED = "ONLINE_REQUIRED"
    HYBRID = "HYBRID"


# Categorization of all 17 auto-discovered actions + inline tools
TOOL_CAPABILITIES: dict[str, CapabilityType] = {
    # ── Fully Local Tools ────────────────────────────────────────────────────
    "open_app": CapabilityType.LOCAL,
    "computer_control": CapabilityType.LOCAL,
    "computer_settings": CapabilityType.LOCAL,
    "desktop_control": CapabilityType.LOCAL,
    "file_controller": CapabilityType.LOCAL,
    "file_processor": CapabilityType.LOCAL,
    "code_helper": CapabilityType.LOCAL,
    "reminder": CapabilityType.LOCAL,
    "system_status": CapabilityType.LOCAL,
    "screen_process": CapabilityType.LOCAL,
    "close_camera": CapabilityType.LOCAL,
    "save_memory": CapabilityType.LOCAL,
    "recall_memory": CapabilityType.LOCAL,
    "undo": CapabilityType.LOCAL,
    "video_player": CapabilityType.LOCAL,  # Local file playback
    "shutdown_jarvis": CapabilityType.LOCAL,

    # ── Online-Required Tools ────────────────────────────────────────────────
    "web_search": CapabilityType.ONLINE_REQUIRED,
    "weather_report": CapabilityType.ONLINE_REQUIRED,
    "flight_finder": CapabilityType.ONLINE_REQUIRED,
    "game_updater": CapabilityType.ONLINE_REQUIRED,
    "youtube_video": CapabilityType.ONLINE_REQUIRED,
    "send_message": CapabilityType.ONLINE_REQUIRED,  # WhatsApp / Telegram Web
    "manage_monitor": CapabilityType.ONLINE_REQUIRED,

    # ── Hybrid Tools ─────────────────────────────────────────────────────────
    "dev_agent": CapabilityType.HYBRID,  # Local shell commands + optional web search
}

_TOOL_FRIENDLY_NAMES: dict[str, str] = {
    "web_search": "Live web search",
    "weather_report": "Weather forecasting",
    "flight_finder": "Flight searching",
    "game_updater": "Game patch news",
    "youtube_video": "YouTube playback",
    "send_message": "Messaging",
    "manage_monitor": "Background news monitor",
}


def get_tool_capability(tool_name: str) -> CapabilityType:
    """Return CapabilityType for a tool. Defaults to LOCAL if unknown."""
    return TOOL_CAPABILITIES.get(tool_name, CapabilityType.LOCAL)


def is_tool_allowed_offline(tool_name: str) -> tuple[bool, Optional[str]]:
    """
    Check if a tool can run in OFFLINE mode.
    Returns (True, None) if allowed, or (False, reason) if internet is required.
    """
    cap = get_tool_capability(tool_name)
    if cap == CapabilityType.ONLINE_REQUIRED:
        friendly = _TOOL_FRIENDLY_NAMES.get(tool_name, tool_name.replace("_", " "))
        msg = (
            f"Sir, {friendly} requires an active internet connection. "
            "Please switch to Online mode or enable Auto mode to use this feature."
        )
        return False, msg
    return True, None
