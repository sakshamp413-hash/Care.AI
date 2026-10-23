---
name: upi-collect-trap
description: Detects UPI "collect request" fraud, where a stranger sends a payment request and tells the victim to enter their UPI PIN to "receive" money, a prize, cashback or a refund. Use on every screenshot of a UPI / payment app.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# UPI Collect Trap

Scammers send a UPI *collect request* and say "enter your PIN to receive ₹5,000".
Entering a UPI PIN **always sends money out**. Nobody ever needs a PIN to receive money.

## Signals

- receive && upi pin
- to receive && pin
- receive money && pin
- पैसे पाने && पिन
- पैसे पाने && pin
- प्राप्त करने && पिन
- prize && upi pin
- cashback && upi pin
- refund && upi pin
- lottery && upi
- collect request && upi pin
- requesting && enter upi pin && won

## Warning

रुकिए! पैसे पाने के लिए कभी UPI PIN नहीं डालना पड़ता। यह धोखा है, PIN मत डालिए।

## Explanation

UPI PIN डालने से पैसे आपके खाते से जाते हैं, आते नहीं। कोई अनजान व्यक्ति "पैसे भेज रहा हूँ, PIN डालो" कहे तो वह ठग है।

## Example

DemoPay — Collect request from Lucky Draw Winner. You have won ₹5,000 cashback! Enter UPI PIN to receive money. Pay ₹5,000.
