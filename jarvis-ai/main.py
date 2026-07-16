import re
import sys

from assistant import JarvisAssistant
from config import REQUIRE_WAKE_WORD, WAKE_WORD, api_key_is_valid
from voice import listen, speak


def contains_wake_word(text: str) -> bool:
    return WAKE_WORD in text.lower()


def strip_wake_word(text: str) -> str:
    cleaned = re.sub(rf"\b{re.escape(WAKE_WORD)}\b", "", text, flags=re.IGNORECASE)
    return cleaned.strip(" ,.!?")


def get_command(heard: str) -> str | None:
    if REQUIRE_WAKE_WORD and not contains_wake_word(heard):
        print(f"Wake word '{WAKE_WORD}' nahi mila - ignore.")
        return None

    command = strip_wake_word(heard) if contains_wake_word(heard) else heard
    return command.strip() or None


def run_voice_mode() -> None:
    if not api_key_is_valid():
        msg = (
            "OpenAI API key set nahi hai. "
            "Dot env file mein apni key daalein, phir dubara chalayein."
        )
        print(msg)
        speak(msg)
        return

    assistant = JarvisAssistant()
    if REQUIRE_WAKE_WORD:
        speak(f"JARVIS online. Pehle {WAKE_WORD} bolkar command dijiye.")
    else:
        speak("JARVIS online. Seedha boliye, main sun raha hoon.")

    print("Voice mode chalu. Ctrl+C se band karein.")

    while True:
        heard = listen(timeout=10, phrase_limit=15)
        if not heard:
            continue

        command = get_command(heard)
        if not command:
            continue

        if any(word in command.lower() for word in ("band karo", "exit", "quit", "goodbye", "alvida")):
            speak("Theek hai, band kar raha hoon. Alvida!")
            break

        try:
            print("Soch raha hoon...")
            reply = assistant.ask(command)
            speak(reply)
        except Exception as exc:
            err = f"Maaf kijiye, error aaya: {exc}"
            print(err)
            speak("Maaf kijiye, kuch gadbad ho gayi. Terminal mein error dekhein.")


def run_text_mode() -> None:
    if not api_key_is_valid():
        print("OpenAI API key missing. .env file mein OPENAI_API_KEY set karein.")
        return

    assistant = JarvisAssistant()
    print("Text mode. Type 'exit' to quit.")
    while True:
        user_text = input("\nYou: ").strip()
        if user_text.lower() in {"exit", "quit", "band"}:
            print("Bye.")
            break
        reply = assistant.ask(user_text)
        print(f"JARVIS: {reply}")


def main() -> None:
    mode = "voice"
    if len(sys.argv) > 1 and sys.argv[1] == "--text":
        mode = "text"

    if mode == "text":
        run_text_mode()
    else:
        run_voice_mode()


if __name__ == "__main__":
    main()
