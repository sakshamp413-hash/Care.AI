---
name: lottery-prize-trap
description: Detects fake lottery, KBC, lucky-draw and prize messages or calls that ask the victim to pay a "fee", "tax" or "processing charge" to receive winnings. Use on what the person says in voice chat and on SMS, WhatsApp and call screenshots.
license: MIT
metadata:
  version: "1.0"
  kind: scam
  severity: high
---

# Lottery / Prize Trap

"Congratulations, you won ₹25 lakh in the KBC lottery! Pay ₹5,000 processing fee to claim."
Real prizes never ask you to pay first.

## Signals

- lottery && fee
- lottery && pay
- lottery && tax
- lottery && charge
- lottery lagi
- lucky draw && fee
- kbc && lottery
- kbc && prize
- won && prize && fee
- prize && processing fee
- inaam && fee
- लॉटरी
- इनाम && फीस
- लकी ड्रॉ

## Warning

रुकिए! लॉटरी या इनाम के लिए कभी पैसे नहीं भरने पड़ते। यह धोखा है — एक भी रुपया मत भेजिए।

## Explanation

आपने कोई लॉटरी खरीदी ही नहीं, तो इनाम कैसे? "फीस भरो, इनाम पाओ" वाले हमेशा ठग होते हैं।

## Warning (English)

Stop! You never have to pay to receive a lottery prize. This is a scam - do not send a single rupee.

## Explanation (English)

You never bought a lottery ticket, so how can you win? "Pay a fee to get your prize" is always a scam.

## Example

Mujhe lottery lagi hai, 25 lakh ka inaam, fee bharne ko bol rahe hain.
