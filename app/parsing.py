"""Tolerant parsing of the model's JSON reply into the /api/guide response shape."""
from __future__ import annotations

import json
import re

# strict=False: models often put raw newlines inside strings (e.g. multi-line screen_text).
_DECODER = json.JSONDecoder(strict=False)
_EXPECTED = {"step_hi", "screen_text", "scam", "target", "done"}


def _candidates(text: str):
    cleaned = re.sub(r"```(?:json)?", "", text)
    no_trailing_commas = re.sub(r",\s*([}\]])", r"\1", cleaned)
    for source in (cleaned, no_trailing_commas):
        for i, ch in enumerate(source):
            if ch != "{":
                continue
            try:
                obj, _ = _DECODER.raw_decode(source, i)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def extract_json(text: str) -> dict:
    """Find the most plausible JSON object in free-form model output."""
    if not text:
        return {}
    try:
        obj = json.loads(text, strict=False)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    best, best_score = {}, -1
    for obj in _candidates(text):
        score = len(_EXPECTED & obj.keys())
        if score > best_score:
            best, best_score = obj, score
    return best


def _bool(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"true", "yes", "1", "haan", "हाँ"}
    return bool(v)


def _num(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _target(raw) -> dict | None:
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        raw = {"x": raw[0], "y": raw[1]}
    if not isinstance(raw, dict):
        return None
    x, y = _num(raw.get("x")), _num(raw.get("y"))
    if x is None or y is None:
        return None
    # Some models answer on a 0-1 scale.
    if 0 <= x <= 1 and 0 <= y <= 1 and (x or y):
        x, y = x * 1000, y * 1000
    clamp = lambda v: int(round(min(max(v, 0), 1000)))
    return {"x": clamp(x), "y": clamp(y)}


def normalize_reply(data: dict) -> dict:
    scam = data.get("scam") if isinstance(data.get("scam"), dict) else {}
    conf = _num(data.get("confidence"), 0.5)
    if conf > 1:
        conf = conf / 100
    return {
        "screen_text": str(data.get("screen_text") or ""),
        "app": str(data.get("app") or ""),
        "scam": {
            "flag": _bool(scam.get("flag", False)),
            "skill": str(scam.get("skill") or ""),
            "reason_hi": str(scam.get("reason_hi") or ""),
        },
        "step_hi": str(data.get("step_hi") or "").strip(),
        "target": _target(data.get("target")),
        "target_label": str(data.get("target_label") or ""),
        "done": _bool(data.get("done", False)),
        "confidence": round(min(max(conf, 0.0), 1.0), 2),
    }
