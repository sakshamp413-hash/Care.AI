"""Tolerant JSON parsing of Gemma replies."""
from app.parsing import extract_json, normalize_reply

GOOD = '{"screen_text": "WhatsApp", "step_hi": "हरा बटन दबाइए", "target": {"x": 500, "y": 900}, "done": false, "confidence": 0.9, "scam": {"flag": false}}'


def test_plain_json():
    assert extract_json(GOOD)["step_hi"] == "हरा बटन दबाइए"


def test_code_fence_and_chatter():
    raw = "Sure! Here you go:\n```json\n" + GOOD + "\n```\nHope this helps."
    assert extract_json(raw)["target"] == {"x": 500, "y": 900}


def test_trailing_comma():
    raw = '{"step_hi": "दबाइए", "done": false,}'
    assert extract_json(raw)["step_hi"] == "दबाइए"


def test_picks_object_with_expected_keys():
    raw = 'thinking {"note": 1} final: ' + GOOD
    assert "step_hi" in extract_json(raw)


def test_garbage_returns_empty():
    assert extract_json("no json here") == {}
    assert extract_json("") == {}


def test_normalize_defaults_and_types():
    r = normalize_reply({"step_hi": " दबाइए ", "done": "true", "confidence": 85})
    assert r["step_hi"] == "दबाइए"
    assert r["done"] is True
    assert r["confidence"] == 0.85
    assert r["target"] is None
    assert r["scam"] == {"flag": False, "skill": "", "reason_hi": ""}


def test_normalize_target_clamped_and_list_form():
    assert normalize_reply({"target": {"x": 1500, "y": -20}})["target"] == {"x": 1000, "y": 0}
    assert normalize_reply({"target": [250, 750]})["target"] == {"x": 250, "y": 750}
    assert normalize_reply({"target": {"x": 0.5, "y": 0.25}})["target"] == {"x": 500, "y": 250}
    assert normalize_reply({"target": {"x": None, "y": 3}})["target"] is None


def test_normalize_scam_flag_string():
    r = normalize_reply({"scam": {"flag": "yes", "skill": "remote-app-trap"}})
    assert r["scam"]["flag"] is True and r["scam"]["skill"] == "remote-app-trap"
