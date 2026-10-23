"""Generate the FICTIONAL demo screenshots in static/demo/ (360x780 SVG).

Layouts line up with the mock-mode ring positions, so the demo works offline too.
Run:  python scripts/make_demo_images.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "demo"

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="780" viewBox="0 0 360 780" ' \
       'font-family="Roboto, Noto Sans Devanagari, Nirmala UI, Arial, sans-serif">'
STATUS = ('<rect width="360" height="28" fill="#000" opacity=".85"/>'
          '<text x="14" y="19" fill="#fff" font-size="13">10:42</text>'
          '<text x="296" y="19" fill="#fff" font-size="13">4G 78%</text>')
FOOT = ('<text x="180" y="772" text-anchor="middle" font-size="9" fill="#888">'
        'DEMO SCREENSHOT · काल्पनिक · Care.AI</text></svg>')

SCREENS = {}

SCREENS["whatsapp-home.svg"] = """
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3b5bdb"/><stop offset="1" stop-color="#862e9c"/></linearGradient></defs>
<rect width="360" height="780" fill="url(#g)"/>{status}
<text x="180" y="110" text-anchor="middle" fill="#fff" font-size="54" font-weight="300">10:42</text>
<text x="180" y="140" text-anchor="middle" fill="#fff" font-size="15">Thursday, 23 October</text>
<g font-size="12" fill="#fff" text-anchor="middle">
<rect x="34" y="320" width="58" height="58" rx="16" fill="#fff"/><text x="63" y="357" fill="#e03131" font-size="22">▶</text><text x="63" y="396">YouTube</text>
<rect x="114" y="320" width="58" height="58" rx="16" fill="#fff"/><text x="143" y="358" fill="#1971c2" font-size="24">☎</text><text x="143" y="396">Phone</text>
<rect x="194" y="320" width="58" height="58" rx="16" fill="#fff"/><text x="223" y="358" fill="#f08c00" font-size="24">✉</text><text x="223" y="396">Messages</text>
<rect x="274" y="320" width="58" height="58" rx="16" fill="#fff"/><text x="303" y="358" fill="#495057" font-size="24">⚙</text><text x="303" y="396">Settings</text>
<rect x="74" y="455" width="58" height="58" rx="16" fill="#fff"/><circle cx="103" cy="484" r="14" fill="none" stroke="#2f9e44" stroke-width="4"/><text x="103" y="531">Camera</text>
<rect x="151" y="455" width="58" height="58" rx="16" fill="#25d366"/><circle cx="180" cy="483" r="16" fill="none" stroke="#fff" stroke-width="3.5"/><path d="M167 494 l-5 11 11 -4z" fill="#fff"/><text x="180" y="531">WhatsApp</text>
<rect x="228" y="455" width="58" height="58" rx="16" fill="#fff"/><rect x="242" y="470" width="30" height="26" rx="4" fill="#5f3dc4"/><text x="257" y="531">Gallery</text>
</g>
<rect x="40" y="650" width="280" height="44" rx="22" fill="#fff" opacity=".9"/><text x="66" y="678" font-size="14" fill="#666">G   Search</text>
"""

SCREENS["whatsapp-chats.svg"] = """
<rect width="360" height="780" fill="#fff"/>{status}
<text x="16" y="68" font-size="24" font-weight="700" fill="#25a35a">WhatsApp</text>
<text x="300" y="68" font-size="20" fill="#333">⋮</text>
<rect x="14" y="100" width="332" height="40" rx="20" fill="#f1f3f5"/><text x="34" y="125" font-size="14" fill="#888">Ask Meta AI or Search</text>
<g font-size="15">
<circle cx="40" cy="180" r="24" fill="#74c0fc"/><text x="40" y="186" text-anchor="middle" fill="#fff" font-weight="700">R</text>
<text x="76" y="174" font-weight="700" fill="#111">Rahul Beta</text><text x="76" y="196" font-size="13" fill="#666">Mummy photo bhejna ghar ki</text><text x="300" y="174" font-size="12" fill="#25a35a">10:30</text>
<circle cx="40" cy="250" r="24" fill="#ffa94d"/><text x="40" y="256" text-anchor="middle" fill="#fff" font-weight="700">P</text>
<text x="76" y="244" font-weight="700" fill="#111">Priya Didi</text><text x="76" y="266" font-size="13" fill="#666">Jai Shri Krishna</text><text x="300" y="244" font-size="12" fill="#888">09:12</text>
<circle cx="40" cy="320" r="24" fill="#8ce99a"/><text x="40" y="326" text-anchor="middle" fill="#fff" font-weight="700">F</text>
<text x="76" y="314" font-weight="700" fill="#111">Family Group</text><text x="76" y="336" font-size="13" fill="#666">Sunita: Good morning</text><text x="286" y="314" font-size="12" fill="#888">Yesterday</text>
</g>
<circle cx="316" cy="680" r="28" fill="#25d366"/><text x="316" y="689" text-anchor="middle" fill="#fff" font-size="26">+</text>
<g font-size="12" fill="#333" text-anchor="middle"><text x="45" y="745" font-weight="700">Chats</text><text x="135" y="745">Updates</text><text x="225" y="745">Communities</text><text x="315" y="745">Calls</text></g>
"""

SCREENS["whatsapp-chat.svg"] = """
<rect width="360" height="780" fill="#efe7dd"/>{status}
<rect y="28" width="360" height="58" fill="#fff"/><text x="12" y="64" font-size="22" fill="#333">←</text>
<circle cx="56" cy="57" r="18" fill="#74c0fc"/><text x="56" y="63" text-anchor="middle" fill="#fff" font-weight="700">R</text>
<text x="84" y="55" font-size="16" font-weight="700" fill="#111">Rahul Beta</text><text x="84" y="73" font-size="11" fill="#666">online</text>
<rect x="262" y="48" width="22" height="16" rx="3" fill="none" stroke="#333" stroke-width="2"/><path d="M284 52 l8 -4 v16 l-8 -4z" fill="#333"/>
<text x="312" y="64" font-size="20" fill="#333">☎</text>
<rect x="40" y="120" width="250" height="56" rx="10" fill="#fff"/><text x="52" y="144" font-size="14" fill="#111">Mummy ghar ki photo bhejna</text><text x="52" y="164" font-size="14" fill="#111">naye parde wali</text>
<rect x="210" y="190" width="120" height="36" rx="10" fill="#d9fdd3"/><text x="224" y="213" font-size="14" fill="#111">Haan beta</text>
<rect x="10" y="704" width="290" height="44" rx="22" fill="#fff"/><text x="26" y="732" font-size="18" fill="#666">☺</text><text x="54" y="731" font-size="15" fill="#999">Message</text>
<g transform="translate(252 726) rotate(-40)"><rect x="-4" y="-11" width="8" height="22" rx="4" fill="none" stroke="#555" stroke-width="2"/></g>
<rect x="270" y="718" width="20" height="15" rx="3" fill="none" stroke="#555" stroke-width="2"/>
<circle cx="328" cy="726" r="22" fill="#25d366"/><rect x="324" y="714" width="8" height="15" rx="4" fill="#fff"/>
"""

SCREENS["whatsapp-attach.svg"] = """
<rect width="360" height="780" fill="#efe7dd"/>{status}
<rect y="28" width="360" height="58" fill="#fff"/><text x="12" y="64" font-size="22" fill="#333">←</text><text x="48" y="62" font-size="16" font-weight="700" fill="#111">Rahul Beta</text>
<rect x="14" y="470" width="332" height="220" rx="18" fill="#fff"/>
<g font-size="12" fill="#333" text-anchor="middle">
<circle cx="70" cy="523" r="26" fill="#7950f2"/><text x="70" y="566">Document</text>
<circle cx="180" cy="523" r="26" fill="#f03e3e"/><text x="180" y="566">Camera</text>
<circle cx="290" cy="523" r="26" fill="#f76707"/><text x="290" y="566">Audio</text>
<circle cx="70" cy="608" r="26" fill="#1c7ed6"/><text x="70" y="651">Location</text>
<circle cx="180" cy="593" r="28" fill="#be4bdb"/><rect x="167" y="582" width="26" height="22" rx="4" fill="#fff"/><text x="180" y="638" font-weight="700">Gallery</text>
<circle cx="290" cy="608" r="26" fill="#0ca678"/><text x="290" y="651">Contact</text>
</g>
<rect x="10" y="704" width="290" height="44" rx="22" fill="#fff"/><text x="54" y="731" font-size="15" fill="#999">Message</text>
<circle cx="328" cy="726" r="22" fill="#25d366"/>
"""

SCREENS["demopay-collect-scam.svg"] = """
<rect width="360" height="780" fill="#f4f6fb"/>{status}
<rect y="28" width="360" height="60" fill="#3b2bb5"/><text x="16" y="66" font-size="20" font-weight="700" fill="#fff">DemoPay</text><text x="226" y="66" font-size="11" fill="#d0c8ff">FICTIONAL DEMO APP</text>
<rect x="16" y="108" width="328" height="380" rx="16" fill="#fff" stroke="#e0e3ef"/>
<text x="180" y="142" text-anchor="middle" font-size="14" fill="#666">Collect request from</text>
<circle cx="180" cy="186" r="28" fill="#ffd43b"/><text x="180" y="196" text-anchor="middle" font-size="26" fill="#7a5a00">★</text>
<text x="180" y="240" text-anchor="middle" font-size="17" font-weight="700" fill="#111">Lucky Draw Winner Dept.</text>
<text x="180" y="260" text-anchor="middle" font-size="12" fill="#888">luckydraw.prize@demopay</text>
<text x="180" y="312" text-anchor="middle" font-size="40" font-weight="700" fill="#111">₹5,000</text>
<rect x="30" y="332" width="300" height="66" rx="10" fill="#ebfbee"/>
<text x="180" y="358" text-anchor="middle" font-size="14" fill="#2b8a3e" font-weight="700">Congratulations! You have won cashback</text>
<text x="180" y="382" text-anchor="middle" font-size="13" fill="#2b8a3e">Enter UPI PIN to receive money in your account</text>
<text x="180" y="430" text-anchor="middle" font-size="12" fill="#888">Request expires in 04:59</text>
<rect x="36" y="520" width="136" height="54" rx="27" fill="#fff" stroke="#adb5bd"/><text x="104" y="553" text-anchor="middle" font-size="16" fill="#495057">Decline</text>
<rect x="188" y="520" width="136" height="54" rx="27" fill="#3b2bb5"/><text x="256" y="553" text-anchor="middle" font-size="16" fill="#fff" font-weight="700">Pay ₹5,000</text>
<text x="180" y="620" text-anchor="middle" font-size="12" fill="#888">Paying from Savings A/c XX4821</text>
<rect x="20" y="680" width="320" height="56" rx="10" fill="#fff3bf"/>
<text x="180" y="704" text-anchor="middle" font-size="11" fill="#5c4400">FICTIONAL SCAM SCREEN FOR HACKATHON DEMO</text>
<text x="180" y="724" text-anchor="middle" font-size="11" fill="#5c4400">यह स्क्रीन काल्पनिक है — DemoPay असली ऐप नहीं है</text>
"""

SCREENS["kyc-sms-scam.svg"] = """
<rect width="360" height="780" fill="#fff"/>{status}
<rect y="28" width="360" height="58" fill="#f8f9fa"/><text x="12" y="64" font-size="22" fill="#333">←</text><text x="48" y="56" font-size="16" font-weight="700" fill="#111">VM-DMBANK</text><text x="48" y="74" font-size="11" fill="#888">Not in contacts</text>
<rect x="14" y="120" width="300" height="190" rx="16" fill="#f1f3f5"/>
<text x="28" y="148" font-size="14" fill="#111">Dear Customer, your DemoBank account</text>
<text x="28" y="170" font-size="14" fill="#111">will be blocked today as your KYC has</text>
<text x="28" y="192" font-size="14" fill="#111">expired. Click the link to update KYC</text>
<text x="28" y="214" font-size="14" fill="#111">immediately:</text>
<text x="28" y="240" font-size="14" fill="#1c7ed6" text-decoration="underline">http://demobank-kyc-update.example</text>
<text x="28" y="266" font-size="14" fill="#111">Call officer: 98XXX XXXXX</text>
<text x="28" y="294" font-size="11" fill="#888">10:31 AM</text>
<rect x="20" y="640" width="320" height="44" rx="10" fill="#fff3bf"/><text x="180" y="667" text-anchor="middle" font-size="11" fill="#5c4400">FICTIONAL SCAM SMS FOR DEMO · काल्पनिक</text>
<rect x="10" y="704" width="340" height="44" rx="22" fill="#f1f3f5"/><text x="30" y="731" font-size="14" fill="#999">Text message</text>
"""

SCREENS["otp-sms.svg"] = """
<rect width="360" height="780" fill="#fff"/>{status}
<rect y="28" width="360" height="58" fill="#f8f9fa"/><text x="12" y="64" font-size="22" fill="#333">←</text><text x="48" y="62" font-size="16" font-weight="700" fill="#111">AX-DEMOBK</text>
<rect x="14" y="120" width="300" height="110" rx="16" fill="#f1f3f5"/>
<text x="28" y="150" font-size="15" fill="#111">482913 is your OTP for login to</text>
<text x="28" y="173" font-size="15" fill="#111">DemoBank. Do not share it with anyone.</text>
<text x="28" y="196" font-size="15" fill="#111">Valid for 5 minutes.</text>
<text x="28" y="218" font-size="11" fill="#888">10:44 AM</text>
<rect x="10" y="704" width="340" height="44" rx="22" fill="#f1f3f5"/><text x="30" y="731" font-size="14" fill="#999">Text message</text>
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, body in SCREENS.items():
        (OUT / name).write_text(HEAD + body.format(status=STATUS) + FOOT, encoding="utf-8")
        print("wrote", OUT / name)
