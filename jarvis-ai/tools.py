import os
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

import psutil
import pyautogui
import pyperclip

pyautogui.FAILSAFE = True

APP_ALIASES = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "chrome": "chrome",
    "browser": "chrome",
    "edge": "msedge",
    "explorer": "explorer",
    "file explorer": "explorer",
    "cmd": "cmd",
    "terminal": "wt",
    "paint": "mspaint",
    "settings": "ms-settings:",
    "vscode": "code",
    "code": "code",
    "cursor": "cursor",
}


def open_application(app_name: str) -> str:
    key = app_name.strip().lower()
    target = APP_ALIASES.get(key, app_name)
    try:
        if target.endswith(":"):
            os.startfile(target)
        else:
            subprocess.Popen(["cmd", "/c", "start", "", target], shell=False)
        return f"Opened {app_name}."
    except Exception as exc:
        return f"Could not open {app_name}: {exc}"


def open_website(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}."


def get_datetime() -> str:
    now = datetime.now()
    return now.strftime("Today is %A, %d %B %Y. Time is %I:%M %p.")


def take_screenshot(save_path: str = "") -> str:
    path = Path(save_path) if save_path else Path.home() / "Pictures" / f"jarvis_{datetime.now():%Y%m%d_%H%M%S}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image = pyautogui.screenshot()
    image.save(path)
    return f"Screenshot saved to {path}."


def type_text(text: str) -> str:
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    return "Typed the text."


def press_hotkey(keys: list[str]) -> str:
    pyautogui.hotkey(*keys)
    return f"Pressed {' + '.join(keys)}."


def set_volume(level: int) -> str:
    level = max(0, min(100, level))
    steps = round(level / 2)
    pyautogui.press("volumemute")
    for _ in range(50):
        pyautogui.press("volumedown")
    for _ in range(steps):
        pyautogui.press("volumeup")
    return f"Volume set to about {level}%."


def search_files(query: str, folder: str = "") -> str:
    root = Path(folder) if folder else Path.home()
    matches = []
    for path in root.rglob("*"):
        if query.lower() in path.name.lower():
            matches.append(str(path))
        if len(matches) >= 10:
            break
    if not matches:
        return f"No files found matching '{query}' in {root}."
    return "Found: " + "; ".join(matches)


def list_running_apps() -> str:
    names = sorted({p.info["name"] for p in psutil.process_iter(["name"]) if p.info.get("name")})
    preview = ", ".join(names[:25])
    return f"Running processes (sample): {preview}"


def close_application(app_name: str) -> str:
    closed = 0
    for proc in psutil.process_iter(["name"]):
        if proc.info.get("name", "").lower().startswith(app_name.lower()):
            try:
                proc.terminate()
                closed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    if closed:
        return f"Closed {closed} process(es) matching {app_name}."
    return f"No running process found for {app_name}."


def run_shell_command(command: str) -> str:
    blocked = ("format", "del /s", "rm -rf", "shutdown", "restart")
    lower = command.lower()
    if any(word in lower for word in blocked):
        return "That command is blocked for safety. Ask explicitly for shutdown/restart."
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
        output = (result.stdout or result.stderr or "Done.").strip()
        return output[:500]
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as exc:
        return f"Command failed: {exc}"


def lock_screen() -> str:
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
    return "Screen locked."


def system_power_action(action: str) -> str:
    mapping = {
        "shutdown": "/s /t 5",
        "restart": "/r /t 5",
        "sleep": "/h",
    }
    flag = mapping.get(action.lower())
    if not flag:
        return "Use shutdown, restart, or sleep."
    subprocess.run(["shutdown", *flag.split()], check=False)
    return f"{action.capitalize()} scheduled in 5 seconds. Run 'shutdown /a' to cancel."


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open a Windows application like notepad, chrome, calculator, settings.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string"}},
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Open a website in the default browser.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get current date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Capture a screenshot and save it.",
            "parameters": {
                "type": "object",
                "properties": {"save_path": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_hotkey",
            "description": "Press keyboard shortcuts like ctrl+c, alt+tab, win+d.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                    }
                },
                "required": ["keys"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Set system volume from 0 to 100.",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "integer"}},
                "required": ["level"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Search files by name in a folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "folder": {"type": "string"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_running_apps",
            "description": "List running applications/processes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close an application by process name.",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string"}},
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Run a safe shell command and return output.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Lock the Windows screen.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system_power_action",
            "description": "Shutdown, restart, or sleep the PC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["shutdown", "restart", "sleep"],
                    }
                },
                "required": ["action"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "open_application": open_application,
    "open_website": open_website,
    "get_datetime": get_datetime,
    "take_screenshot": take_screenshot,
    "type_text": type_text,
    "press_hotkey": press_hotkey,
    "set_volume": set_volume,
    "search_files": search_files,
    "list_running_apps": list_running_apps,
    "close_application": close_application,
    "run_shell_command": run_shell_command,
    "lock_screen": lock_screen,
    "system_power_action": system_power_action,
}
