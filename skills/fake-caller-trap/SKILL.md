---
name: fake-caller-trap
description: Detects when the person says a caller (fake bank officer, customer care, delivery agent) is asking them for an OTP, UPI PIN or card details. Use on what the person says in voice chat and on call or chat screenshots.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# Fake Caller Trap

Seeing an OTP on screen is normal. Someone *asking* for it on a call is always a scam.
This skill fires on what the elder tells Beta Bol: "bank wale OTP maang rahe hain".

## Signals

- otp && maang
- otp && mang
- otp && pooch
- otp && मांग
- otp && माँग
- ओटीपी && मांग
- ओटीपी && माँग
- ओटीपी && पूछ
- pin && maang
- pin && pooch
- पिन && मांग
- asking for otp
- asking for my otp
- asking for pin
- card number && maang
- cvv && maang

## Warning

रुकिए! बैंक कभी फोन पर OTP या PIN नहीं माँगता। यह धोखा है — फोन अभी काट दीजिए।

## Explanation

असली बैंक, पुलिस या कस्टमर केयर कभी OTP, PIN या कार्ड नंबर नहीं पूछते। जो पूछे, वह ठग है।

## Warning (English)

Stop! Banks never ask for your OTP or PIN on a phone call. This is a scam - hang up now.

## Explanation (English)

Real banks, police or customer care never ask for your OTP, PIN or card number. Whoever asks is a fraudster.

## Example

Bank wale ka call aaya hai, OTP maang rahe hain.
