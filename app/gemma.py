"""Gemma 4 via the Gemini API: one screenshot in, one Hindi step + scam verdict out."""
from __future__ import annotations

import os
import time

from .parsing import extract_json, normalize_reply
from .skills import get_skill, scam_skills

MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

_client = None
_client_key = None


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""


def available() -> bool:
    return bool(_api_key())


def _get_client():
    global _client, _client_key
    if _client is None or _client_key != _api_key():
        from google import genai
        from google.genai import types

        _client_key = _api_key()
        _client = genai.Client(api_key=_client_key, http_options=types.HttpOptions(timeout=100_000))
    return _client


def _generate(contents, config, attempts: int = 3):
    """generate_content with retries: the Gemini API intermittently returns 500/503/429."""
    import httpx
    from google.genai import errors

    for i in range(attempts):
        try:
            return _get_client().models.generate_content(model=MODEL, contents=contents, config=config)
        except errors.APIError as e:
            retryable = getattr(e, "code", None) in (429, 500, 502, 503, 504)
            if not retryable or i == attempts - 1:
                raise
            time.sleep(0.8 * (2 ** i))
        except httpx.TimeoutException:
            if i >= 1:  # one retry only: each attempt can already take ~100s
                raise


def _why_empty(resp) -> str:
    try:
        c = resp.candidates[0] if resp.candidates else None
        u = resp.usage_metadata
        return f"finish={c and c.finish_reason} thoughts={u.thoughts_token_count} out={u.candidates_token_count}"
    except Exception:
        return "no metadata"


LANG_OVERRIDE = """LANGUAGE OVERRIDE: the parent chose English. Write "step_hi" and "reason_hi" in simple,
warm, respectful English (same rules: one action, max 20 words, describe colour/shape/position).
Keep button names exactly as printed on screen. The JSON field names stay the same."""


def build_prompt(goal: str, history: list[str], parent_name: str, child_name: str, lang: str = "hi") -> str:
    guide = get_skill("phone-guide-hindi")
    scam_lines = []
    for s in scam_skills():
        signals = "; ".join(" + ".join(r) for r in s.signals[:8])
        scam_lines.append(f'- "{s.name}" ({s.severity}): {s.description} Typical text: {signals}')
    done_steps = "\n".join(f"{i + 1}. {h}" for i, h in enumerate(history)) or "(none yet - this is the first screenshot)"

    return f"""You are "Care.AI", a phone guardian for an elderly Indian parent.
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

{LANG_OVERRIDE if lang == "en" else ""}
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
            parent_name: str = "", child_name: str = "", lang: str = "hi") -> dict:
    from google.genai import types

    prompt = build_prompt(goal, history, parent_name, child_name, lang)
    resp = _generate(
        [types.Part.from_bytes(data=image_bytes, mime_type=mime), prompt],
        types.GenerateContentConfig(temperature=0.2, max_output_tokens=4096),
    )
    text = resp.text or ""
    data = extract_json(text)
    if not data:  # thinking can occasionally crowd out the answer; try once more
        resp = _generate([types.Part.from_bytes(data=image_bytes, mime_type=mime), prompt],
                         types.GenerateContentConfig(temperature=0.2, max_output_tokens=4096))
        text = resp.text or ""
        data = extract_json(text)
    if not data:
        raise ValueError(f"Model reply had no JSON ({_why_empty(resp)}): {text[:120]!r} … {text[-80:]!r}")
    return normalize_reply(data)


def build_chat_prompt(text: str, lang: str, history: list[dict], parent_name: str, child_name: str) -> str:
    scam_lines = "\n".join(f'- "{s.name}" ({s.severity}): {s.description}' for s in scam_skills())
    turns = "\n".join(f'{"Parent" if h.get("role") == "user" else "Care.AI"}: {h.get("text", "")}'
                      for h in history[-8:]) or "(start of conversation)"
    language = ("simple spoken Hindi in Devanagari script" if lang == "hi" else "simple, warm English")
    return f"""You are "Care.AI", a patient son/daughter-like voice assistant helping an elderly Indian parent
with their smartphone, and protecting them from scams.
Parent: {parent_name or "माँ/पापा"}. Child: {child_name or "बेटा"}.

Scam skills to check the parent's words against:
{scam_lines}

Conversation so far:
{turns}
Parent just said: "{text}"

Rules:
- Reply in {language}. Maximum 2 short sentences (35 words). Respectful ("आप").
- If the parent describes a scam (someone asking for OTP/PIN, KYC/account-block threat, lottery/prize,
  remote-access app, police/CBI "digital arrest"), start with "रुकिए!" (or "Stop!") and tell them exactly what to do.
- Never ask for or repeat a PIN, OTP or password. Never suggest installing AnyDesk/TeamViewer.
- For phone help, give only the ONE next step. If they need on-screen help, ask them to send a screenshot.

Reply with exactly this JSON (no markdown):
{{"reply": "<what Care.AI says>", "scam": {{"flag": false, "skill": "<scam skill name or empty>", "reason_hi": "<short Hindi reason or empty>"}}}}"""


def chat(text: str, lang: str, history: list[dict], parent_name: str = "", child_name: str = "") -> dict:
    from google.genai import types

    # Gemma 4 always "thinks" first (not configurable on this model), so leave room for it,
    # and retry once if the visible answer still comes back empty.
    for _ in range(2):
        resp = _generate(
            [build_chat_prompt(text, lang, history, parent_name, child_name)],
            types.GenerateContentConfig(temperature=0.3, max_output_tokens=3072),
        )
        raw = resp.text or ""
        data = extract_json(raw)
        reply = str(data.get("reply") or "").strip() if data else raw.strip()
        if reply:
            break
    if not reply:
        raise ValueError(f"Empty model reply ({_why_empty(resp)}): {raw[:200]!r}")
    scam = normalize_reply({"scam": data.get("scam")})["scam"] if data else {"flag": False, "skill": "", "reason_hi": ""}
    return {"reply": reply, "scam": scam}
