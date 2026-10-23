"""End-to-end API checks in mock mode (no API keys needed)."""
import json
import os

os.environ["MOCK"] = "1"
os.environ.pop("ELEVENLABS_API_KEY", None)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def guide(filename="screen.png", goal="बेटे को WhatsApp पर फोटो भेजनी है", history=()):
    return client.post(
        "/api/guide",
        files={"image": (filename, PNG, "image/png")},
        data={"goal": goal, "history": json.dumps(list(history)),
              "person": json.dumps({"parent_name": "शांति", "child_name": "राहुल"})},
    ).json()


def test_health():
    h = client.get("/api/health").json()
    assert h["status"] == "ok" and h["mode"] == "mock"
    assert h["model"] == "gemma-4-26b-a4b-it" and h["skills"] == 7


def test_skills_endpoint():
    names = {s["name"] for s in client.get("/api/skills").json()}
    assert "upi-collect-trap" in names


def test_guide_first_step_has_target():
    r = guide()
    assert r["step_hi"] and r["target"] and r["done"] is False
    assert r["scam"]["flag"] is False
    assert set(r) >= {"screen_text", "app", "scam", "step_hi", "target", "target_label", "done", "confidence"}


def test_guide_progresses_and_finishes():
    assert guide(history=["a"])["step_hi"] != guide()["step_hi"]
    assert guide(history=["s"] * 20)["done"] is True


def test_scam_screenshot_blocks_guidance():
    r = guide(filename="demopay-collect-scam.svg")
    assert r["scam"]["flag"] and r["scam"]["severity"] == "high"
    assert r["scam"]["skill"] == "upi-collect-trap"
    assert r["target"] is None and r["step_hi"] == r["scam"]["warning_hi"]


def test_otp_is_caution_and_guidance_continues():
    r = guide(filename="otp-sms.svg")
    assert r["scam"]["severity"] == "caution"
    assert r["target"] is not None


def test_tts_falls_back_to_browser():
    assert client.post("/api/tts", json={"text": "नमस्ते"}).status_code == 204


def test_frontend_served():
    r = client.get("/")
    assert r.status_code == 200 and "बेटा बोल" in r.text


def chat(text, lang="hi"):
    return client.post("/api/chat", json={"text": text, "lang": lang, "history": []}).json()


def test_chat_flags_caller_asking_for_otp():
    r = chat("Bank wale ka call aaya hai, OTP maang rahe hain.")
    assert r["scam"]["severity"] == "high" and r["scam"]["skill"] == "fake-caller-trap"
    assert r["reply"].startswith("रुकिए")


def test_chat_normal_question_is_not_a_scam():
    r = chat("WhatsApp par photo kaise bhejte hain?")
    assert r["scam"]["flag"] is False and r["reply"] and r["mode"] == "mock"


def test_chat_rejects_empty_text():
    assert client.post("/api/chat", json={"text": "  "}).status_code == 400


def test_voice_ui_served():
    r = client.get("/voice/")
    assert r.status_code == 200 and "Beta Bol se baat kijiye" in r.text
