"""Beta Bol (बेटा बोल) - FastAPI backend.

Run:  uvicorn app.main:app --reload
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from . import gemma, kavach, mock, tts  # noqa: E402
from .skills import load_skills  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
VOICE_DIR = ROOT / "frontend"
ENV_FILE = ROOT / ".env"
MAX_IMAGE_BYTES = 8 * 1024 * 1024

app = FastAPI(title="Care.AI", version="1.0")

# Honest answers when Gemma fails with a real key (mock steps are only for keyless demo mode).
GUIDE_RETRY = {
    "screen_text": "", "app": "", "scam": {"flag": False, "skill": "", "reason_hi": ""},
    "step_hi": "माफ़ कीजिए, यह स्क्रीन ठीक से पढ़ नहीं पाए। कृपया फिर से फोटो भेजिए।",
    "target": None, "target_label": "", "done": False, "confidence": 0.0,
}
GUIDE_RETRY_EN = "Sorry, I couldn't read this screen properly. Please send the screenshot again."
CHAT_RETRY = {"hi": "माफ़ कीजिए, अभी जवाब नहीं दे पाए। कृपया फिर से बोलिए।",
              "en": "Sorry, I couldn't answer just now. Please say that again."}
last_error = ""


def mock_mode() -> bool:
    # Re-read API keys from .env so adding a key takes effect without restarting the server.
    for k, v in dotenv_values(ENV_FILE).items():
        if k.endswith(("_API_KEY", "_VOICE_ID")) and v:
            os.environ[k] = v
    return os.getenv("MOCK", "").strip() == "1" or not gemma.available()


def _json_field(raw: str, default):
    try:
        val = json.loads(raw) if raw else default
    except json.JSONDecodeError:
        return default
    return val if isinstance(val, type(default)) else default


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "mock" if mock_mode() else "gemma",
        "model": gemma.MODEL,
        "voice": "elevenlabs" if tts.available() else "browser",
        "skills": len(load_skills()),
        "key_present": gemma.available(),
        "last_error": last_error,
    }


@app.get("/api/skills")
def skills():
    return [s.public() for s in load_skills()]


@app.post("/api/guide")
async def guide(
    image: UploadFile = File(...),
    goal: str = Form(...),
    lang: str = Form("hi"),
    history: str = Form("[]"),
    person: str = Form("{}"),
):
    # Screenshots are processed in memory only and never written to disk or logs.
    lang = "en" if lang == "en" else "hi"
    data = await image.read()
    if not data:
        raise HTTPException(400, "Empty image")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image too large")
    mime = image.content_type if (image.content_type or "").startswith("image/") else "image/jpeg"

    steps = [str(h) for h in _json_field(history, [])][-12:]
    who = _json_field(person, {})
    parent, child = str(who.get("parent_name", "")), str(who.get("child_name", ""))

    global last_error
    mode = "mock" if mock_mode() else "gemma"
    if mode == "gemma":
        try:
            reply = gemma.analyze(data, mime, goal, steps, parent, child, lang)
            last_error = ""
        except Exception as e:
            # Never guess on a real screen: canned steps could be wrong or miss a scam.
            last_error = f"{type(e).__name__}: {e}"[:300]
            print(f"[guide] Gemma failed: {last_error}")
            reply, mode = dict(GUIDE_RETRY), "error"
            if lang == "en":
                reply["step_hi"] = GUIDE_RETRY_EN
    else:
        reply = mock.analyze(goal, steps, image.filename or "", lang)

    scam = kavach.judge(reply["scam"], reply["screen_text"], lang)
    reply["scam"] = scam
    if scam["severity"] == "high":
        # Never guide forward on a scam screen.
        reply.update(step_hi=scam["warning_hi"], target=None, target_label="", done=False)
    reply["mode"] = mode
    reply["model"] = gemma.MODEL if mode == "gemma" else "mock"
    return reply


class ChatRequest(BaseModel):
    text: str
    lang: str = "hi"
    history: list[dict] = []
    person: dict = {}


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Voice chat: one thing the parent said in, Beta Bol's reply + Scam Kavach verdict out."""
    global last_error
    text = req.text.strip()[:500]
    if not text:
        raise HTTPException(400, "Empty text")
    lang = "en" if req.lang == "en" else "hi"
    parent, child = str(req.person.get("parent_name", "")), str(req.person.get("child_name", ""))

    mode = "mock" if mock_mode() else "gemma"
    if mode == "gemma":
        try:
            reply = gemma.chat(text, lang, req.history, parent, child)
            last_error = ""
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"[:300]
            print(f"[chat] Gemma failed: {last_error}")
            reply, mode = {"reply": CHAT_RETRY[lang], "scam": {"flag": False, "skill": "", "reason_hi": ""}}, "error"
    else:
        reply = mock.chat(text, lang)

    # Layer 2 rules run on the parent's own words.
    scam = kavach.judge(reply["scam"], text, lang)
    if scam["severity"] == "high" and "gemma" not in scam["source"]:
        reply["reply"] = scam["warning_hi"]  # model missed it; the skill's warning takes over
    return {"reply": reply["reply"], "scam": scam, "mode": mode,
            "model": gemma.MODEL if mode == "gemma" else "mock", "error": last_error if mode != "gemma" else ""}


class TTSRequest(BaseModel):
    text: str


@app.post("/api/tts")
def speak(req: TTSRequest):
    audio = tts.speak(req.text)
    if audio is None:
        return Response(status_code=204)
    return Response(content=audio, media_type="audio/mpeg",
                    headers={"Cache-Control": "public, max-age=86400"})


app.mount("/skills", StaticFiles(directory=ROOT / "skills"), name="skills")
app.mount("/voice", StaticFiles(directory=VOICE_DIR, html=True), name="voice")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
