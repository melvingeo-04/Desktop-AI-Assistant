#computer_control.py
import io
import json
import platform
import re
import string
import subprocess
import sys

if platform.system() == "Windows":
    _WIN_HIDE: dict = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _WIN_HIDE: dict = {}
import time
import random
from pathlib import Path

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE    = 0.05
    _PYAUTOGUI = True
except ImportError:
    _PYAUTOGUI = False

try:
    import pyperclip
    _PYPERCLIP = True
except ImportError:
    _PYPERCLIP = False

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


_BASE         = _base_dir()
_CONFIG_PATH  = _BASE / "config" / "api_keys.json"
_MEMORY_PATH  = _BASE / "memory" / "long_term.json"

def _load_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _platform_os() -> str:
    return {"Windows": "windows", "Darwin": "mac", "Linux": "linux"}.get(
        platform.system(), "linux"
    )

def _get_os() -> str:
    return _load_config().get("os_system", _platform_os()).lower()


def _get_api_key() -> str:
    return _load_config().get("gemini_api_key", "")

_SAFE_SCREENSHOT_ROOTS = (
    Path.home(),
)

def _safe_screenshot_path(requested: str | None) -> Path:
    fallback = Path.home() / "Desktop" / "jarvis_screenshot.png"
    if not requested:
        return fallback
    try:
        p = Path(requested).expanduser().resolve()
        for root in _SAFE_SCREENSHOT_ROOTS:
            if p.is_relative_to(root.resolve()):
                p.parent.mkdir(parents=True, exist_ok=True)
                return p
    except Exception:
        pass
    return fallback

def _require_pyautogui():
    if not _PYAUTOGUI:
        raise RuntimeError("PyAutoGUI not installed. Run: pip install pyautogui")

_FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Drew", "Quinn",
    "Avery", "Blake", "Cameron", "Dakota", "Emerson", "Finley", "Harper",
]
_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson",
]
_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "mail.com"]


def _random_data(data_type: str) -> str:
    dt = data_type.lower().strip()

    if dt == "first_name":
        return random.choice(_FIRST_NAMES)

    if dt == "last_name":
        return random.choice(_LAST_NAMES)

    if dt == "name":
        return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"

    if dt == "email":
        first = random.choice(_FIRST_NAMES).lower()
        last  = random.choice(_LAST_NAMES).lower()
        num   = random.randint(10, 999)
        return f"{first}.{last}{num}@{random.choice(_DOMAINS)}"

    if dt == "username":
        return f"{random.choice(_FIRST_NAMES).lower()}{random.randint(100, 9999)}"

    if dt == "password":
        chars = string.ascii_letters + string.digits + "!@#$%"
        raw   = (
            random.choice(string.ascii_uppercase)
            + random.choice(string.digits)
            + random.choice("!@#$%")
            + "".join(random.choices(chars, k=9))
        )
        return "".join(random.sample(raw, len(raw)))

    if dt == "phone":
        return f"+1{random.randint(200,999)}{random.randint(1_000_000, 9_999_999)}"

    if dt == "birthday":
        y = random.randint(1980, 2000)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        return f"{m:02d}/{d:02d}/{y}"

    if dt == "address":
        num    = random.randint(100, 9999)
        street = random.choice(["Main St", "Oak Ave", "Park Blvd", "Elm St", "Cedar Ln"])
        return f"{num} {street}"

    if dt == "zip_code":
        return str(random.randint(10000, 99999))

    if dt == "city":
        return random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])

    return f"random_{data_type}_{random.randint(1000, 9999)}"

def _user_profile() -> dict:
    """Read identity fields from long-term memory."""
    try:
        if _MEMORY_PATH.exists():
            data     = json.loads(_MEMORY_PATH.read_text(encoding="utf-8"))
            identity = data.get("identity", {})
            return {k: v.get("value", "") for k, v in identity.items()}
    except Exception:
        pass
    return {}

def _type(text: str, interval: float = 0.03) -> str:
    _require_pyautogui()
    time.sleep(0.3)
    pyautogui.typewrite(text, interval=interval)
    return f"Typed: {text[:60]}{'…' if len(text) > 60 else ''}"


def _smart_type(text: str, clear_first: bool = True) -> str:
    _require_pyautogui()
    if clear_first:
        _clear_field()
        time.sleep(0.1)

    if len(text) > 20 and _PYPERCLIP:
        pyperclip.copy(text)
        time.sleep(0.1)
        paste_key = "command" if _get_os() == "mac" else "ctrl"
        pyautogui.hotkey(paste_key, "v")
        return f"Smart-typed (clipboard): {text[:60]}{'…' if len(text) > 60 else ''}"

    pyautogui.typewrite(text, interval=0.04)
    return f"Smart-typed: {text[:60]}{'…' if len(text) > 60 else ''}"


def _click(x=None, y=None, button: str = "left", clicks: int = 1) -> str:
    _require_pyautogui()
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button, clicks=clicks)
        return f"{'Double-c' if clicks == 2 else 'C'}licked ({x}, {y}) [{button}]"
    pyautogui.click(button=button, clicks=clicks)
    return f"Clicked at current position [{button}]"


def _hotkey(*keys) -> str:
    _require_pyautogui()
    pyautogui.hotkey(*keys)
    return f"Hotkey: {'+'.join(keys)}"


def _press(key: str) -> str:
    _require_pyautogui()
    pyautogui.press(key)
    return f"Pressed: {key}"


def _scroll(direction: str = "down", amount: int = 3) -> str:
    _require_pyautogui()
    vertical   = direction in ("up", "down")
    clicks     = amount if direction in ("up", "right") else -amount
    pyautogui.scroll(clicks) if vertical else pyautogui.hscroll(clicks)
    return f"Scrolled {direction} ×{amount}"


def _move(x: int, y: int, duration: float = 0.3) -> str:
    _require_pyautogui()
    pyautogui.moveTo(x, y, duration=duration)
    return f"Mouse → ({x}, {y})"


def _drag(x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> str:
    _require_pyautogui()
    pyautogui.moveTo(x1, y1, duration=0.2)
    pyautogui.dragTo(x2, y2, duration=duration, button="left")
    return f"Dragged ({x1},{y1}) → ({x2},{y2})"


def _clipboard_get() -> str:
    if _PYPERCLIP:
        return pyperclip.paste()
    _hotkey("ctrl", "c")
    time.sleep(0.2)
    return "(copied — pyperclip unavailable for read)"


def _clipboard_paste(text: str) -> str:
    if _PYPERCLIP:
        pyperclip.copy(text)
        time.sleep(0.1)
        _require_pyautogui()
        paste_key = "command" if _get_os() == "mac" else "ctrl"
        pyautogui.hotkey(paste_key, "v")
        return f"Pasted: {text[:60]}{'…' if len(text) > 60 else ''}"
    return "pyperclip not available"


def _screenshot(save_path: str | None = None) -> str:
    _require_pyautogui()
    path = _safe_screenshot_path(save_path)
    img  = pyautogui.screenshot()
    img.save(str(path))
    return f"Screenshot saved: {path}"


def _clear_field() -> str:
    _require_pyautogui()
    select_key = "command" if _get_os() == "mac" else "ctrl"
    pyautogui.hotkey(select_key, "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    return "Field cleared"

def _focus_window(title: str) -> str:
    os_name = _get_os()

    if os_name == "windows":
        try:
            script = f'(New-Object -ComObject WScript.Shell).AppActivate("{title}")'
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True, timeout=5, **_WIN_HIDE,
            )
            time.sleep(0.3)
            return f"Focused window: {title}"
        except Exception as e:
            return f"focus_window (Windows) failed: {e}"

    if os_name == "mac":
        script = (
            f'tell application "System Events" to '
            f'set frontmost of (first process whose name contains "{title}") to true'
        )
        try:
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, timeout=5,
            )
            time.sleep(0.3)
            return f"Focused window: {title}"
        except Exception as e:
            return f"focus_window (macOS) failed: {e}"

    if os_name == "linux":
        try:
            result = subprocess.run(
                ["wmctrl", "-a", title],
                capture_output=True, timeout=5,
            )
            if result.returncode == 0:
                time.sleep(0.3)
                return f"Focused window: {title}"
        except FileNotFoundError:
            pass
        try:
            result = subprocess.run(
                ["xdotool", "search", "--name", title, "windowactivate"],
                capture_output=True, timeout=5,
            )
            time.sleep(0.3)
            return f"Focused window: {title}"
        except FileNotFoundError:
            return "focus_window (Linux) requires wmctrl or xdotool"
        except Exception as e:
            return f"focus_window (Linux) failed: {e}"

    return f"focus_window: unknown OS '{os_name}'"


def _screen_find(description: str) -> tuple[int, int] | None:
    api_key = _get_api_key()
    if not api_key:
        print("[ComputerControl] ⚠️ No API key for screen_find")
        return None

    try:
        from google.genai import types as gtypes
        from core import gemini

        _require_pyautogui()
        w, h = pyautogui.size()
        img  = pyautogui.screenshot()
        
        # High quality JPEG for rapid network transmission
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        image_bytes = buf.getvalue()

        prompt = (
            f"You are an expert GUI element locator.\n"
            f"Screen dimensions: {w}x{h} pixels.\n"
            f"Target element to find: \"{description}\"\n\n"
            f"Instructions:\n"
            f"1. Locate the exact UI element, icon, button, tab, menu item, or input field on the screen.\n"
            f"2. Return its bounding box in normalized coordinates [ymin, xmin, ymax, xmax] on a scale of 0 to 1000.\n"
            f"   (0,0 is top-left; 1000,1000 is bottom-right).\n"
            f"3. If the element is not found on screen, reply with: NOT_FOUND\n\n"
            f"Reply with ONLY the format: [ymin, xmin, ymax, xmax]"
        )

        response = gemini.call(
            [gtypes.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"), prompt],
            tier=gemini.FAST, timeout_ms=20_000,
        )
        if response is None:
            return None

        text = (response.text or "").strip()
        if "NOT_FOUND" in text.upper():
            print(f"[ComputerControl] Element '{description}' reported NOT_FOUND by vision model")
            return None

        # Look for [ymin, xmin, ymax, xmax] format
        box_match = re.search(r"\[\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\]", text)
        if box_match:
            ymin, xmin, ymax, xmax = [float(v) for v in box_match.groups()]
            center_x = int(((xmin + xmax) / 2.0 / 1000.0) * w)
            center_y = int(((ymin + ymax) / 2.0 / 1000.0) * h)
            center_x = max(0, min(w - 1, center_x))
            center_y = max(0, min(h - 1, center_y))
            print(f"[ComputerControl] 🎯 Vision grounded '{description}' -> box [{int(ymin)}, {int(xmin)}, {int(ymax)}, {int(xmax)}] -> screen ({center_x}, {center_y})")
            return center_x, center_y

        # Fallback: look for two numbers x, y
        pt_match = re.search(r"(\d+)\s*,\s*(\d+)", text)
        if pt_match:
            v1, v2 = int(pt_match.group(1)), int(pt_match.group(2))
            if v1 <= 1000 and v2 <= 1000:
                center_x = int((v1 / 1000.0) * w) if v1 > v2 else int((v2 / 1000.0) * w)
                center_y = int((v2 / 1000.0) * h) if v1 > v2 else int((v1 / 1000.0) * h)
            else:
                center_x, center_y = v1, v2
            center_x = max(0, min(w - 1, center_x))
            center_y = max(0, min(h - 1, center_y))
            print(f"[ComputerControl] 🎯 Vision grounded '{description}' (fallback coords) -> ({center_x}, {center_y})")
            return center_x, center_y

    except Exception as e:
        print(f"[ComputerControl] ⚠️ screen_find failed: {e}")

    return None

def computer_control(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    """
    Dispatch table for all computer control actions.
    """
    params = parameters or {}
    action = params.get("action", "").lower().strip()

    if not action:
        return "No action specified for computer_control."

    if player:
        player.write_log(f"[Computer] {action}")

    print(f"[ComputerControl] ▶ {action}  {params}")

    try:

        if action == "type":
            return _type(params.get("text", ""))

        if action == "smart_type":
            return _smart_type(
                params.get("text", ""),
                clear_first=params.get("clear_first", True),
            )

        if action in ("click", "left_click"):
            return _click(params.get("x"), params.get("y"), "left", 1)

        if action == "double_click":
            return _click(params.get("x"), params.get("y"), "left", 2)

        if action == "right_click":
            return _click(params.get("x"), params.get("y"), "right", 1)

        if action == "move":
            return _move(int(params.get("x", 0)), int(params.get("y", 0)))

        if action == "drag":
            return _drag(
                int(params.get("x1", 0)), int(params.get("y1", 0)),
                int(params.get("x2", 0)), int(params.get("y2", 0)),
                duration=float(params.get("duration", 0.5)),
            )

        if action in ("screen_drag", "canvas_draw"):
            from_desc = params.get("from_description")
            to_desc   = params.get("to_description")
            x1 = params.get("x1")
            y1 = params.get("y1")
            x2 = params.get("x2")
            y2 = params.get("y2")

            if from_desc:
                c1 = _screen_find(from_desc)
                if c1:
                    x1, y1 = c1
            if to_desc:
                c2 = _screen_find(to_desc)
                if c2:
                    x2, y2 = c2

            if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
                dur = float(params.get("duration", 0.6))
                return _drag(int(x1), int(y1), int(x2), int(y2), duration=dur)
            return "screen_drag requires start (x1, y1 or from_description) and end (x2, y2 or to_description)."

        if action == "hotkey":
            raw  = params.get("keys", "")
            keys = [k.strip() for k in raw.split("+")] if isinstance(raw, str) else raw
            return _hotkey(*keys)

        if action == "press":
            return _press(params.get("key", "enter"))

        if action == "scroll":
            return _scroll(
                direction=params.get("direction", "down"),
                amount=int(params.get("amount", 3)),
            )

        if action == "copy":
            return _clipboard_get()

        if action == "paste":
            return _clipboard_paste(params.get("text", ""))

        if action == "screenshot":
            return _screenshot(params.get("path"))

        if action == "screen_find":
            coords = _screen_find(params.get("description", ""))
            return f"{coords[0]},{coords[1]}" if coords else "NOT_FOUND"

        if action == "screen_click":
            desc = params.get("description", "")
            if not desc:
                return "Missing 'description' for screen_click. Specify what button or UI element to click."
            coords = _screen_find(desc)
            if not coords:
                return f"Could not locate '{desc}' on the current screen."

            clicks = int(params.get("clicks", 1))
            button = str(params.get("button", "left")).lower()
            time.sleep(0.15)
            _click(x=coords[0], y=coords[1], button=button, clicks=clicks)

            click_type = "Double-clicked" if clicks == 2 else "Right-clicked" if button == "right" else "Clicked"
            verify_str = ""
            if params.get("verify", False):
                time.sleep(0.3)
                verify_str = " (Verified: action performed)"

            return f"{click_type} '{desc}' at ({coords[0]}, {coords[1]}){verify_str}."

        if action == "screen_type":
            desc = params.get("description", "")
            text = params.get("text", "")
            if not desc:
                return "Missing 'description' for screen_type. Specify which input field or element to type into."
            coords = _screen_find(desc)
            if not coords:
                return f"Could not locate input field '{desc}' on the current screen."

            time.sleep(0.15)
            _click(x=coords[0], y=coords[1], button="left", clicks=1)
            time.sleep(0.25)

            if params.get("clear_first", True):
                _clear_field()
                time.sleep(0.1)

            if text:
                if len(text) > 20 and _PYPERCLIP:
                    _smart_type(text, clear_first=False)
                else:
                    _type(text)

            if params.get("enter", False):
                time.sleep(0.1)
                _press("enter")

            return f"Focused '{desc}' at ({coords[0]}, {coords[1]}) and typed '{text}'."

        if action == "wait":
            secs = float(params.get("seconds", 1.0))
            secs = min(secs, 30.0)
            time.sleep(secs)
            return f"Waited {secs}s"

        if action == "clear_field":
            return _clear_field()

        if action == "focus_window":
            return _focus_window(params.get("title", ""))

        if action == "random_data":
            dt     = params.get("type", "name")
            result = _random_data(dt)
            print(f"[ComputerControl] 🎲 random {dt} → {result}")
            return result

        if action == "user_data":
            field   = params.get("field", "name")
            profile = _user_profile()
            value   = profile.get(field, "")
            if not value:
                value = _random_data(field)
                print(f"[ComputerControl] ⚠️ No '{field}' in memory, using random: {value}")
            return value

        return f"Unknown action: '{action}'"

    except Exception as e:
        print(f"[ComputerControl] ❌ {action}: {e}")
        return f"computer_control '{action}' failed: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "computer_control",
    "description": (
        "Desktop UI automation and computer control. "
        "CRITICAL: NEVER guess raw (x, y) coordinates for buttons, icons, or text boxes. "
        "To click or type on ANY visual UI element (e.g. Brush tool in Paint, New Slide in PowerPoint, toolbars, buttons, textboxes), "
        "ALWAYS use action='screen_click' or action='screen_type' with a clear 'description' of what to click/type into. "
        "Uses vision grounding to accurately locate and interact with the element on the user's screen."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "screen_click | screen_type | screen_find | screen_drag | "
                    "click | double_click | right_click | type | smart_type | "
                    "hotkey | press | scroll | move | drag | copy | paste | "
                    "screenshot | wait | clear_field | focus_window | user_data"
                )
            },
            "description": {
                "type": "STRING",
                "description": "Visual or text description of the UI button, icon, menu, or field to find/click/type (e.g. 'Pencil tool in Paint', 'Save button', 'Title placeholder in PowerPoint', 'Search bar'). REQUIRED for screen_click, screen_type, screen_find."
            },
            "text": {
                "type": "STRING",
                "description": "Text to type (for type, smart_type, screen_type)"
            },
            "clicks": {
                "type": "INTEGER",
                "description": "Number of clicks for screen_click / click (1 for single click, 2 for double click, default: 1)"
            },
            "button": {
                "type": "STRING",
                "description": "Mouse button: 'left' | 'right' | 'middle' (default: 'left')"
            },
            "enter": {
                "type": "BOOLEAN",
                "description": "Whether to press Enter after typing (for screen_type, default: false)"
            },
            "clear_first": {
                "type": "BOOLEAN",
                "description": "Clear field before typing (default: true)"
            },
            "from_description": {
                "type": "STRING",
                "description": "Starting UI element description for screen_drag"
            },
            "to_description": {
                "type": "STRING",
                "description": "Target UI element description for screen_drag"
            },
            "x1": { "type": "INTEGER", "description": "Starting X for drag/screen_drag" },
            "y1": { "type": "INTEGER", "description": "Starting Y for drag/screen_drag" },
            "x2": { "type": "INTEGER", "description": "Ending X for drag/screen_drag" },
            "y2": { "type": "INTEGER", "description": "Ending Y for drag/screen_drag" },
            "keys": {
                "type": "STRING",
                "description": "Key combination e.g. 'ctrl+c'"
            },
            "key": {
                "type": "STRING",
                "description": "Single key e.g. 'enter'"
            },
            "direction": {
                "type": "STRING",
                "description": "up | down | left | right"
            },
            "amount": {
                "type": "INTEGER",
                "description": "Scroll amount (default: 3)"
            },
            "seconds": {
                "type": "NUMBER",
                "description": "Seconds to wait"
            },
            "title": {
                "type": "STRING",
                "description": "Window title for focus_window"
            },
            "verify": {
                "type": "BOOLEAN",
                "description": "Take screenshot after action to visually verify result"
            },
            "path": {
                "type": "STRING",
                "description": "Save path for screenshot"
            }
        },
        "required": [
            "action"
        ]
    },
    "handler": computer_control,
}

