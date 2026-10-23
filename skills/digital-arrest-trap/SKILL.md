---
name: digital-arrest-trap
description: Detects "digital arrest" scams, where fake CBI, police, customs, ED or TRAI officers on a video or voice call claim a parcel, SIM or bank account is linked to a crime and demand money to avoid arrest. Use on every screenshot of calls, video calls and chat.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# Digital Arrest Trap

Scammers in fake uniforms video-call the victim, show fake warrants, keep them on camera
for hours ("you are under digital arrest") and make them transfer money to "verify" it.

## Signals

- digital arrest
- arrest warrant
- money laundering
- narcotics
- crime branch
- cbi && call
- cbi && officer
- police && video call
- customs && parcel
- parcel && drugs
- sim && illegal activities
- trai && disconnected
- डिजिटल अरेस्ट
- गिरफ्तार
- गिरफ़्तार

## Warning

रुकिए! पुलिस या CBI कभी वीडियो कॉल पर गिरफ्तार नहीं करती, न पैसे माँगती है। फोन अभी काट दीजिए।

## Explanation

"डिजिटल अरेस्ट" जैसी कोई चीज़ कानून में नहीं है। ऐसे कॉल ठगों के होते हैं। फोन काटिए और बेटे-बेटी को बताइए।

## Example

WhatsApp video call — CBI Officer Mumbai. Your Aadhaar is linked to money laundering case. You are under digital arrest. Do not disconnect the call.
