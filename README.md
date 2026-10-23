# बेटा बोल · Beta Bol

> **Har bujurg ke paas smartphone hai. Ab har smartphone ke paas ek beta hai.**

Beta Bol is a phone guardian for elderly Indians. It guides them through their phone **one screenshot at a time**, in **Hindi**, in **their own child's voice**, and **stops them the moment a scam appears**.

Built in one day at **MLH Hacktoberfest Hack Day Lucknow × BBDITM** (23 Oct 2026).

- 🧠 **AI:** Gemma 4 (`gemma-4-26b-a4b-it`), an open-weight model, called through the **Gemini API**. The model name also shows in the app's status bar.
- 🛡️ **Scam Kavach:** two-layer scam detection on *every* screenshot.
- 🧩 **Agent Skills:** every scam pattern is a [`SKILL.md`](skills/) file ([agentskills.io](https://agentskills.io) open standard), so anyone can add one with a pull request.
- 🔊 **Voice:** ElevenLabs `eleven_multilingual_v2` Instant Voice Clone of the child (with their consent). If that's unavailable, it falls back to the browser's Hindi voice.
- 📜 **License:** MIT.

---

## The problem

Elderly parents in India are new to smartphones. Every day they call their children: *"Beta, phone mein ye kya aa gaya? Ye button kahan hai?"* Explaining a screen over a phone call is hard.

Scammers target these same elders most: UPI collect-request fraud, fake KYC / account-blocked SMS, remote-access apps (AnyDesk, TeamViewer) pushed by fake "customer care", and "digital arrest" video calls from fake CBI or police officers.

## How it works

1. The parent opens the Hindi web app (it can be installed to the home screen) and picks a goal: *"बेटे को WhatsApp पर फोटो भेजनी है"*, *"वीडियो कॉल करना है"*, *"UPI से पैसे भेजने हैं"*. They can also speak the goal in Hindi.
2. They send a **screenshot** of their current screen.
3. **Gemma 4** reads it and returns the **one next step** in simple Hindi, plus the x/y position (0–1000 scale) of the button to tap.
4. The app draws a **pulsing red ring** on the screenshot at that spot and **speaks the step in the child's cloned voice**.
5. The parent taps the button, sends the next screenshot, and repeats until the goal is done. Then the app shows a **"शाबाश!"** celebration.
6. **Scam Kavach** checks every screenshot first. If it finds a high-severity scam, the whole screen turns red, the phone vibrates, a Hindi warning is spoken, and one tap sends the child a **WhatsApp alert**. An OTP on screen gets a gentle yellow caution instead, and guidance continues.
7. If the parent taps **"समझ नहीं आया"** twice, or Gemma's confidence is low, a button sends the child a WhatsApp message with the goal and the exact step the parent is stuck on.

## Scam Kavach: two layers, so a warning never fails silently

| Layer | What it does |
|---|---|
| 1. Gemma 4 | Judges the screenshot against every scam skill and extracts all visible screen text |
| 2. Deterministic rules | Runs the keyword rules from each skill's `## Signals` on that text. `&&` means all terms must appear (AND). Terms match at the **start of a word**, so `otp` does not match "footprint" |

If **either** layer flags the screen, the app warns. High severity beats caution. The severity level and the spoken warning always come from the `SKILL.md` file, never from the model.

## Agent Skills

| Skill | Severity | Catches |
|---|---|---|
| [`upi-collect-trap`](skills/upi-collect-trap/SKILL.md) | high | "Enter UPI PIN to receive money" collect requests |
| [`kyc-sms-trap`](skills/kyc-sms-trap/SKILL.md) | high | Fake KYC, account-blocked, and "electricity cut tonight" messages |
| [`remote-app-trap`](skills/remote-app-trap/SKILL.md) | high | AnyDesk, TeamViewer, QuickSupport, and screen-share prompts |
| [`digital-arrest-trap`](skills/digital-arrest-trap/SKILL.md) | high | Fake CBI, police, or customs video calls |
| [`fake-caller-trap`](skills/fake-caller-trap/SKILL.md) | high | A caller asking for an OTP, PIN or card details (said in voice chat) |
| [`otp-share-trap`](skills/otp-share-trap/SKILL.md) | caution | An OTP visible on screen |
| [`phone-guide-hindi`](skills/phone-guide-hindi/SKILL.md) | guide | The guidance style: one action per step, at most 20 words, respectful Hindi, never asks for a PIN or OTP |

### Add a new scam (no code change)

1. Create `skills/<your-scam-name>/SKILL.md`. Copy an existing skill as a template.
2. Fill in the frontmatter (`name` must match the folder name; `license: MIT`; `metadata` with `version`, `kind: scam`, and `severity: high|caution`). Then add these sections: `## Signals`, `## Warning` (one Hindi sentence that gets spoken), `## Explanation`, and `## Example` (sample screen text).
3. Run `pytest`. The tests check the spec, and they check that **your rules catch your own example**.
4. Open a pull request. 🎉

## Run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your keys (optional, see below)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 for the screenshot guide, or http://localhost:8000/voice/ for the voice chat UI.

- **No keys?** The app runs in **mock mode** with canned steps, and the status bar shows `MOCK`. The keyword rules still run, so loading the demo scam screenshot still triggers Scam Kavach.
- **`GEMINI_API_KEY`** turns on Gemma 4. Get a key at https://aistudio.google.com/apikey.
- **`ELEVENLABS_API_KEY` + `ELEVENLABS_VOICE_ID`** turn on the child's voice. Make an *Instant Voice Clone* from a 1–2 minute recording of the child, **with their consent**. Then run `python scripts/pregen_warnings.py` to pre-cache the scam warnings so they play instantly.
- **On a real phone:** microphone input and installing to the home screen need HTTPS. Expose the server with `cloudflared tunnel --url http://localhost:8000` (or ngrok) and open the HTTPS URL on the phone.

### Tests

```bash
pytest -q
```

The tests cover skill spec validation, every skill catching its own example, false positives (`footprint`, normal UPI payments, normal chats), the two-layer merge, tolerant JSON parsing, and the API end to end in mock mode.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/guide` | multipart: `image`, `goal`, `history` (JSON list of previous steps), `person` (JSON `{parent_name, child_name}`) → `{screen_text, app, scam{flag, skill, severity, warning_hi, reason_hi, source}, step_hi, target{x,y}, target_label, done, confidence, mode, model}` |
| `POST` | `/api/chat` | `{text, lang, history, person}` → `{reply, scam{...}, mode, model, error}` (voice chat; rules also run on the parent's words) |
| `POST` | `/api/tts` | `{text}` → `audio/mpeg`, or `204` (use the browser voice) |
| `GET` | `/api/health` | mode, model, voice, skill count |
| `GET` | `/api/skills` | all loaded skills |

## Project layout

```
app/        FastAPI backend (main, gemma, kavach, skills, parsing, tts, mock)
skills/     Agent Skills: one folder + SKILL.md per scam pattern / guide style
static/     Single-page Hindi PWA (index.html, manifest, service worker, demo screenshots)
scripts/    Demo image, icon and voice-cache generators
tests/      pytest suite
```

## Why not just Gemini Live?

Gemini Live can already share your screen in Hindi, and some apps and research prototypes guide seniors step by step. Beta Bol's difference is the combination:

1. **Zero setup:** one big button. There is no "open app → Live → share screen" sequence for an elder to remember.
2. **The child's own voice:** the guidance comes with emotional trust attached.
3. **Proactive, two-layer scam protection on every screen,** with India-specific patterns (UPI collect requests, digital arrest, KYC SMS).
4. **Family loop:** it escalates to the real child, with context.
5. **Open source,** with scam patterns as community-editable Agent Skills.

## Safety & privacy

- Screenshots are processed in memory and **never stored or logged**.
- The voice clone is made **only with the child's consent**.
- The guide **never** asks anyone to share a PIN, OTP, or password, and **never** guides them to install remote-access apps.
- When a high-severity scam is detected, guidance stops.
- Family settings (names and the WhatsApp number) stay in the phone's own `localStorage`.
- The demo scam screenshots (e.g. "DemoPay") are **fictional** and labelled as such.

## Roadmap

A warranty and bill tracker, an AI that waits on customer-care IVR hold for you, a WhatsApp bot, on-device Gemma E2B/E4B, and more Indian languages.

## License

[MIT](LICENSE)
