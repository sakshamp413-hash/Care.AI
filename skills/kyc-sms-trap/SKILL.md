---
name: kyc-sms-trap
description: Detects fake KYC, "account blocked", PAN-update and "electricity will be cut tonight" SMS or WhatsApp messages that push the victim to click a link or call a number. Use on every screenshot of SMS, WhatsApp or email.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# KYC / Account-Block SMS Trap

Fake messages create panic ("your account will be blocked today", "electricity will be
disconnected at 9:30 pm") and ask the person to click a link or call "the officer".

## Signals

- kyc && blocked
- kyc && block
- kyc && suspend
- kyc && expire
- kyc && update && link
- kyc && click
- account will be blocked
- account has been blocked && click
- account && suspended && click
- pan && update && link
- pan card && blocked
- electricity && disconnect
- electricity && tonight
- power && disconnected && call
- बिजली && कट
- बिजली && काट
- केवाईसी
- खाता && बंद
- खाता && ब्लॉक

## Warning

रुकिए! बैंक या बिजली वाले कभी ऐसे मैसेज से लिंक नहीं भेजते। इस लिंक को मत छूइए, और इस नंबर पर फोन मत कीजिए।

## Explanation

यह नकली मैसेज है जो डर दिखाकर लिंक दबवाता है। असली बैंक KYC के लिए शाखा में बुलाता है, मैसेज के लिंक से नहीं।

## Warning (English)

Stop! Banks and electricity offices never send links like this. Do not tap the link and do not call this number.

## Explanation (English)

This is a fake message that scares you into tapping a link. A real bank asks you to visit the branch for KYC, not a link in an SMS.

## Example

Dear customer your SBI account will be blocked today. Your KYC has expired. Click http://sbi-kyc-update.example to update KYC immediately.
