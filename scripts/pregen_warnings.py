"""Pre-generate the fixed Hindi scam warnings in the child's voice (ElevenLabs),
so Scam Kavach plays them instantly from the disk cache during the demo.

Run once after setting ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env:
    python scripts/pregen_warnings.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from app import tts  # noqa: E402
from app.skills import scam_skills  # noqa: E402

EXTRA = [
    "ठीक है। अब अपने फोन की स्क्रीन की फोटो भेजिए।",
    "बहुत अच्छा किया जो रुक गए।",
    "शाबाश! आपने खुद कर लिया। आपका बेटा बहुत खुश होगा।",
    "शाबाश! आपने खुद कर लिया। आपकी बेटी बहुत खुश होगी।",
]

if not tts.available():
    sys.exit("Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env first.")

for text in [s.warning_hi for s in scam_skills()] + EXTRA:
    ok = tts.speak(text) is not None
    print("OK  " if ok else "FAIL", text)
