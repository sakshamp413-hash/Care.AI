"""Canned responses so the app runs (and demos) with no API keys.

Screen text is guessed from the uploaded file name, so the real rules layer
still runs: upload demo/demopay-collect-scam.svg and Scam Kavach fires.
"""
from __future__ import annotations

FLOWS = {
    "whatsapp_photo": [
        ("हरे रंग का WhatsApp वाला निशान दबाइए।", {"x": 500, "y": 620}, "WhatsApp icon"),
        ("ऊपर जिसका नाम लिखा है, उस बेटे की चैट दबाइए।", {"x": 500, "y": 230}, "chat row"),
        ("नीचे लिखने वाली पट्टी में कागज़ की पिन जैसा निशान दबाइए।", {"x": 700, "y": 930}, "attach"),
        ("बैंगनी रंग का 'Gallery' वाला गोला दबाइए।", {"x": 500, "y": 760}, "Gallery"),
        ("जो फोटो भेजनी है, उस पर एक बार दबाइए।", {"x": 250, "y": 300}, "photo"),
        ("नीचे दाईं ओर हरा गोल तीर वाला बटन दबाइए।", {"x": 900, "y": 930}, "Send"),
    ],
    "video_call": [
        ("हरे रंग का WhatsApp वाला निशान दबाइए।", {"x": 500, "y": 620}, "WhatsApp icon"),
        ("बेटे के नाम वाली चैट दबाइए।", {"x": 500, "y": 230}, "chat row"),
        ("ऊपर दाईं ओर कैमरे जैसा निशान दबाइए।", {"x": 760, "y": 70}, "video call"),
    ],
    "upi_send": [
        ("अपना पैसे भेजने वाला ऐप खोलिए।", {"x": 500, "y": 600}, "UPI app"),
        ("'Pay contacts' या 'पैसे भेजें' वाला बटन दबाइए।", {"x": 250, "y": 400}, "Pay"),
        ("जिसे भेजना है उसका नाम दबाइए।", {"x": 500, "y": 300}, "contact"),
        ("रकम लिखिए, फिर नीला 'Pay' बटन दबाइए। PIN सिर्फ आप जानते हैं, खुद डालिए।", {"x": 500, "y": 900}, "Pay"),
    ],
}

MOCK_SCREEN_TEXT = {
    "collect": "DemoPay Collect request from Lucky Draw. You have won ₹5,000 cashback! Enter UPI PIN to receive money.",
    "upi-scam": "DemoPay Collect request. Enter UPI PIN to receive money.",
    "kyc": "Dear customer your account will be blocked today. KYC expired. Click link to update KYC.",
    "anydesk": "Google Play AnyDesk Remote Desktop Install",
    "arrest": "CBI Officer video call. You are under digital arrest. Money laundering case.",
    "otp": "482913 is your OTP for login to DemoBank. Do not share it with anyone.",
    "whatsapp": "WhatsApp Chats Rahul Beta",
}


def chat(text: str, lang: str) -> dict:
    reply = ("ठीक है। अपने फोन की स्क्रीन की फोटो भेजिए, मैं एक-एक कदम बताऊँगा।" if lang == "hi"
             else "Okay. Please send a screenshot of your phone screen and I'll guide you one step at a time.")
    return {"reply": reply, "scam": {"flag": False, "skill": "", "reason_hi": ""}}


def pick_flow(goal: str) -> str:
    g = (goal or "").lower()
    if "वीडियो" in g or "video" in g:
        return "video_call"
    if "upi" in g or "पैसे" in g or "pay" in g:
        return "upi_send"
    return "whatsapp_photo"


def screen_text_for(filename: str) -> str:
    f = (filename or "").lower()
    for key, text in MOCK_SCREEN_TEXT.items():
        if key in f:
            return text
    return ""


def analyze(goal: str, history: list[str], filename: str = "") -> dict:
    flow = FLOWS[pick_flow(goal)]
    i = len(history)
    if i >= len(flow):
        return {
            "screen_text": screen_text_for(filename), "app": "mock",
            "scam": {"flag": False, "skill": "", "reason_hi": ""},
            "step_hi": "शाबाश! हो गया।", "target": None, "target_label": "",
            "done": True, "confidence": 0.9,
        }
    step, target, label = flow[i]
    return {
        "screen_text": screen_text_for(filename), "app": "mock",
        "scam": {"flag": False, "skill": "", "reason_hi": ""},
        "step_hi": step, "target": target, "target_label": label,
        "done": False, "confidence": 0.8,
    }
