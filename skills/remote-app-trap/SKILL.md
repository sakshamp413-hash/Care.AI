---
name: remote-app-trap
description: Detects remote-access and screen-sharing apps (AnyDesk, TeamViewer, QuickSupport, RustDesk, AirDroid) and screen-share permission prompts that fake "customer care" agents ask victims to install. Use on every screenshot, especially Play Store and permission dialogs.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# Remote-Access App Trap

Fake "customer care" callers ask the victim to install AnyDesk or TeamViewer and read out
a code. The scammer then sees and controls the phone, including the banking app.

## Signals

- anydesk
- teamviewer
- quicksupport
- quick support
- rustdesk
- airdroid
- remote access
- remote control && allow
- screen share && customer care
- screen sharing && support
- visible on your screen && support
- एनीडेस्क
- टीमव्यूअर

## Warning

रुकिए! यह ऐप आपके फोन का पूरा कंट्रोल किसी और को दे देता है। इसे मत खोलिए, और कोई कोड किसी को मत बताइए।

## Explanation

कोई भी असली बैंक या कस्टमर केयर आपसे AnyDesk या TeamViewer जैसा ऐप नहीं डलवाता। इससे ठग आपकी स्क्रीन देखकर पैसे निकाल लेते हैं।

## Example

Google Play — AnyDesk Remote Desktop. Install. Your address: 123 456 789. Tell this code to the support agent.
