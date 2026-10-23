"""Gemma 4 via the Gemini API: one screenshot in, one Hindi step + scam verdict out."""
from __future__ import annotations

import os

from .parsing import extract_json, normalize_reply
from .skills import get_skill, scam_skills

MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

_client = None


def available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))


def _get_client():
    global _client
    if _client is None:
        from google import genai
        from google.genai import types

        _client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            http_options=types.HttpOptions(timeout=60_000),
        )
    return _client


def build_prompt(goal: str, history: list[str], parent_name: str, child_name: str) -> str:
    guide = get_skill("phone-guide-hindi")
    scam_lines = []
    for s in scam_skills():
        signals = "; ".join(" + ".join(r) for r in s.signals[:8])
        scam_lines.append(f'- "{s.name}" ({s.severity}): {s.description} Typical text: {signals}')
    done_steps = "\n".join(f"{i + 1}. {h}" for i, h in enumerate(history)) or "(none yet - this is the first screenshot)"

    return f"""You are "Beta Bol", a phone guardian for an elderly Indian parent.
The image is a screenshot of the parent's phone. Do two jobs and reply with ONE JSON object only.

JOB 1 - SCAM KAVACH (always first). Check the screenshot against these scam skills:
{chr(10).join(scam_lines)}
Flag a scam only if the screen really shows that pattern. A normal UPI payment the parent started,
a normal chat, or a normal app screen is NOT a scam.

JOB 2 - GUIDE. Parent's goal: "{goal}"
Parent: {parent_name or "माँ/पापा"}. Child: {child_name or "बेटा"}.
Steps already given:
{done_steps}
Give the ONE next step following this style guide:
{guide.body if guide else ""}

Reply with exactly this JSON (no markdown, no extra text):
{{
  "screen_text": "all readable text on the screen, in reading order",
  "app": "which app/screen this is, e.g. WhatsApp chat",
  "scam": {{"flag": false, "skill": "<one of the scam skill names or empty>", "reason_hi": "<one short Hindi sentence why, or empty>"}},
  "step_hi": "<the ONE next step in Hindi, max 20 words>",
  "target": {{"x": 0, "y": 0}},
  "target_label": "<short English label of the element to tap>",
  "done": false,
  "confidence": 0.0
}}
Rules for "target": x and y are the CENTER of the element to tap, on a 0-1000 scale
(x from the left edge, y from the top edge of the image). Use null if nothing needs tapping.
"confidence" is 0-1: how sure you are this step is right for this exact screen."""


def analyze(image_bytes: bytes, mime: str, goal: str, history: list[str],
            parent_name: str = "", child_name: str = "") -> dict:
    from google.genai import types

    prompt = build_prompt(goal, history, parent_name, child_name)
    resp = _get_client().models.generate_content(
        model=MODEL,
        contents=[types.Part.from_bytes(data=image_bytes, mime_type=mime), prompt],
        config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=2048),
    )
    text = resp.text or ""
    data = extract_json(text)
    if not data:
        raise ValueError(f"Model reply had no JSON: {text[:200]!r}")
    return normalize_reply(data)
