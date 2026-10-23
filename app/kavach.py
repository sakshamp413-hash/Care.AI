"""Scam Kavach: merge the model's verdict (layer 1) with keyword rules (layer 2).

If EITHER layer flags, we warn. High severity beats caution. Severity and the
spoken warning always come from the SKILL.md file, never from the model.
"""
from __future__ import annotations

from .skills import SEVERITY_RANK, best_rule_hit, get_skill

NO_SCAM = {"flag": False, "skill": "", "severity": "none", "warning_hi": "",
           "reason_hi": "", "source": "", "matched": ""}


def judge(model_scam: dict, screen_text: str) -> dict:
    model_skill = None
    if model_scam.get("flag"):
        s = get_skill(model_scam.get("skill", ""))
        if s and s.kind == "scam":
            model_skill = s

    rule_hit = best_rule_hit(screen_text)
    rule_skill = rule_hit[0] if rule_hit else None

    candidates = [s for s in (model_skill, rule_skill) if s]
    if not candidates:
        return dict(NO_SCAM)
    skill = max(candidates, key=lambda s: SEVERITY_RANK.get(s.severity, 0))

    sources = []
    if model_skill and model_skill.name == skill.name:
        sources.append("gemma")
    if rule_skill and rule_skill.name == skill.name:
        sources.append("rules")

    reason = model_scam.get("reason_hi") if "gemma" in sources else ""
    return {
        "flag": True,
        "skill": skill.name,
        "severity": skill.severity,
        "warning_hi": skill.warning_hi,
        "reason_hi": reason or skill.explanation_hi,
        "source": "+".join(sources),
        "matched": " && ".join(rule_hit[1]) if rule_hit and "rules" in sources else "",
    }
