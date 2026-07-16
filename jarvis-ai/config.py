import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMP_AUDIO = BASE_DIR / "temp_response.mp3"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
WAKE_WORD = os.getenv("JARVIS_WAKE_WORD", "jarvis").lower()
REQUIRE_WAKE_WORD = os.getenv("JARVIS_REQUIRE_WAKE_WORD", "false").lower() == "true"

PLACEHOLDER_KEY = "your_openai_api_key_here"


def api_key_is_valid() -> bool:
    key = OPENAI_API_KEY.strip()
    return bool(key) and key != PLACEHOLDER_KEY

# Hindi + English voices (edge-tts)
VOICE_EN = "en-IN-PrabhatNeural"
VOICE_HI = "hi-IN-MadhurNeural"

SYSTEM_PROMPT = """You are JARVIS, a helpful voice assistant on a Windows laptop.
You speak naturally in Hindi, English, or Hinglish depending on what the user uses.
Keep spoken replies short (1-3 sentences) unless the user asks for detail.
When the user wants laptop actions, use the available tools.
Confirm before destructive actions like shutdown or deleting files.
If a request is unclear, ask one brief follow-up question.
"""
