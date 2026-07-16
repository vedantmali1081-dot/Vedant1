import asyncio
import re
import subprocess
from pathlib import Path

import edge_tts
import speech_recognition as sr

from config import TEMP_AUDIO, VOICE_EN, VOICE_HI

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300
recognizer.pause_threshold = 0.8


def _has_devanagari(text: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", text))


def pick_voice(text: str) -> str:
    return VOICE_HI if _has_devanagari(text) else VOICE_EN


def _recognize(audio: sr.AudioData) -> str | None:
    for language in ("hi-IN", "en-IN", "en-US"):
        try:
            text = recognizer.recognize_google(audio, language=language)
            if text.strip():
                return text.strip()
        except sr.UnknownValueError:
            continue
        except sr.RequestError as exc:
            print(f"Speech API error ({language}): {exc}")
            return None
    print("Sunai nahi diya - dubara boliye.")
    return None


def listen(timeout: int = 8, phrase_limit: int = 15) -> str | None:
    try:
        with sr.Microphone() as source:
            print("Sun raha hoon... (boliye)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            except sr.WaitTimeoutError:
                print("Koi awaaz nahi aayi.")
                return None
    except OSError as exc:
        print(f"Microphone error: {exc}")
        print("Windows Settings > Privacy > Microphone check karein.")
        return None

    text = _recognize(audio)
    if text:
        print(f"Aap: {text}")
    return text


async def _speak_async(text: str, voice: str, output_path: Path) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))


def speak(text: str) -> None:
    if not text:
        return
    voice = pick_voice(text)
    print(f"JARVIS: {text}")
    try:
        asyncio.run(_speak_async(text, voice, TEMP_AUDIO))
        _play_audio(TEMP_AUDIO)
    except Exception as exc:
        print(f"Voice error: {exc}")


def _play_audio(path: Path) -> None:
    uri = path.resolve().as_uri()
    script = f"""
Add-Type -AssemblyName presentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open('{uri}')
$player.Volume = 1.0
$player.Play()
Start-Sleep -Milliseconds 500
$timeout = 30
while ($player.NaturalDuration.HasTimeSpan -eq $false -and $timeout -gt 0) {{
    Start-Sleep -Milliseconds 200
    $timeout--
}}
if ($player.NaturalDuration.HasTimeSpan) {{
    $secs = $player.NaturalDuration.TimeSpan.TotalSeconds + 0.5
    Start-Sleep -Seconds $secs
}}
$player.Close()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=False)
