"""ElevenLabs text-to-speech in the child's cloned voice, with a disk cache.

Returns None when ElevenLabs is not configured or fails; the frontend then
falls back to the browser's Hindi voice.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import httpx

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "tts"
MODEL_ID = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")


def available() -> bool:
    return bool(os.getenv("ELEVENLABS_API_KEY") and os.getenv("ELEVENLABS_VOICE_ID"))


def cache_path(text: str, voice_id: str) -> Path:
    key = hashlib.sha1(f"{voice_id}|{MODEL_ID}|{text}".encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{key}.mp3"


def speak(text: str) -> bytes | None:
    text = (text or "").strip()[:500]
    if not text or not available():
        return None
    voice_id = os.environ["ELEVENLABS_VOICE_ID"]
    path = cache_path(text, voice_id)
    if path.exists():
        return path.read_bytes()
    try:
        r = httpx.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Accept": "audio/mpeg"},
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.85},
            },
            timeout=30,
        )
        r.raise_for_status()
    except httpx.HTTPError as e:
        print(f"[tts] ElevenLabs failed, browser voice fallback: {e}")
        return None
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(r.content)
    return r.content
