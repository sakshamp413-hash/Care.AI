"""Beta Bol (बेटा बोल) - FastAPI backend.

Run:  uvicorn app.main:app --reload
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from . import gemma, kavach, mock, tts  # noqa: E402
from .skills import load_skills  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
MAX_IMAGE_BYTES = 8 * 1024 * 1024

app = FastAPI(title="Beta Bol", version="1.0")


def mock_mode() -> bool:
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
    }


@app.get("/api/skills")
def skills():
    return [s.public() for s in load_skills()]


@app.post("/api/guide")
async def guide(
    image: UploadFile = File(...),
    goal: str = Form(...),
    history: str = Form("[]"),
    person: str = Form("{}"),
):
    # Screenshots are processed in memory only and never written to disk or logs.
    data = await image.read()
    if not data:
        raise HTTPException(400, "Empty image")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image too large")
    mime = image.content_type if (image.content_type or "").startswith("image/") else "image/jpeg"

    steps = [str(h) for h in _json_field(history, [])][-12:]
    who = _json_field(person, {})
    parent, child = str(who.get("parent_name", "")), str(who.get("child_name", ""))

    mode = "mock" if mock_mode() else "gemma"
    if mode == "gemma":
        try:
            reply = gemma.analyze(data, mime, goal, steps, parent, child)
        except Exception as e:  # keep the demo alive if the API hiccups
            print(f"[guide] Gemma failed, using mock fallback: {e}")
            reply, mode = mock.analyze(goal, steps, image.filename or ""), "mock-fallback"
    else:
        reply = mock.analyze(goal, steps, image.filename or "")

    scam = kavach.judge(reply["scam"], reply["screen_text"])
    reply["scam"] = scam
    if scam["severity"] == "high":
        # Never guide forward on a scam screen.
        reply.update(step_hi=scam["warning_hi"], target=None, target_label="", done=False)
    reply["mode"] = mode
    reply["model"] = gemma.MODEL if mode == "gemma" else "mock"
    return reply


class TTSRequest(BaseModel):
    text: str


@app.post("/api/tts")
def speak(req: TTSRequest):
    audio = tts.speak(req.text)
    if audio is None:
        return Response(status_code=204)
    return Response(content=audio, media_type="audio/mpeg",
                    headers={"Cache-Control": "public, max-age=86400"})


app.mount("/skills", StaticFiles(directory=STATIC_DIR.parent / "skills"), name="skills")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
