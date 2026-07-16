"""Quick mic + voice test. Run: python test_mic.py"""

from voice import listen, speak


def main() -> None:
    speak("Mic test shuru. Kuch boliye.")
    text = listen(timeout=12, phrase_limit=10)
    if text:
        speak(f"Mujhe sunai diya: {text}")
        print("Mic theek hai.")
    else:
        speak("Kuch sunai nahi diya. Mic ya internet check karein.")
        print("Mic test fail.")


if __name__ == "__main__":
    main()
