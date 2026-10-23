"""Layer 2 keyword rules + the two-layer merge in Scam Kavach."""
import pytest

from app import kavach
from app.skills import best_rule_hit, term_in

SCAM_SCREENS = [
    ("upi-collect-trap", "Collect request: Enter your UPI PIN to receive ₹2,000 refund"),
    ("upi-collect-trap", "पैसे पाने के लिए अपना पिन डालें"),
    ("kyc-sms-trap", "Your account will be blocked today. Update PAN"),
    ("kyc-sms-trap", "प्रिय उपभोक्ता आज रात 9:30 बजे आपकी बिजली काट दी जाएगी"),
    ("remote-app-trap", "Install TeamViewer QuickSupport from Play Store"),
    ("digital-arrest-trap", "Mumbai Crime Branch: your parcel contains drugs"),
    ("otp-share-trap", "Your OTP is 4821. Valid for 10 mins"),
]

SAFE_SCREENS = [
    "WhatsApp Chats Rahul Beta Good morning Family Group",
    "Your carbon footprint report is ready",            # 'otp' inside 'footprint'
    "Pay ₹200 to Sharma Kirana. Enter UPI PIN",          # normal outgoing payment
    "Received ₹500 from Rahul. Balance updated",
    "Settings > Display > Font size",
    "Photos Gallery Camera Screenshots",
    "Shopping cart: notebook, pencil box",               # 'otp' / 'pin' not at word start
]


@pytest.mark.parametrize("skill,text", SCAM_SCREENS)
def test_scam_screens_are_flagged(skill, text):
    hit = best_rule_hit(text)
    assert hit and hit[0].name == skill


@pytest.mark.parametrize("text", SAFE_SCREENS)
def test_safe_screens_not_flagged(text):
    assert best_rule_hit(text) is None


def test_word_start_matching():
    assert term_in("otp", "your otp: 1234")
    assert not term_in("otp", "footprint")
    assert term_in("kyc", "e-kyc pending")
    assert term_in("upi pin", "enter upi   pin")


def test_high_beats_caution_in_rules():
    text = "Enter UPI PIN to receive money. Your OTP is 1234"
    assert best_rule_hit(text)[0].name == "upi-collect-trap"


def test_model_only_flag_still_warns():
    v = kavach.judge({"flag": True, "skill": "digital-arrest-trap", "reason_hi": "नकली पुलिस"}, "")
    assert v["flag"] and v["severity"] == "high" and v["source"] == "gemma"
    assert v["reason_hi"] == "नकली पुलिस"


def test_rules_only_flag_still_warns():
    v = kavach.judge({"flag": False}, "Download AnyDesk now")
    assert v["skill"] == "remote-app-trap" and v["source"] == "rules"
    assert v["warning_hi"].startswith("रुकिए")


def test_both_layers_agree():
    v = kavach.judge({"flag": True, "skill": "remote-app-trap"}, "AnyDesk")
    assert v["source"] == "gemma+rules"


def test_high_from_rules_beats_caution_from_model():
    v = kavach.judge({"flag": True, "skill": "otp-share-trap"}, "Enter UPI PIN to receive cashback")
    assert v["skill"] == "upi-collect-trap" and v["severity"] == "high"


def test_unknown_model_skill_is_ignored():
    v = kavach.judge({"flag": True, "skill": "made-up-skill"}, "hello")
    assert v["flag"] is False


def test_severity_comes_from_skill_not_model():
    v = kavach.judge({"flag": True, "skill": "otp-share-trap", "severity": "high"}, "")
    assert v["severity"] == "caution"
