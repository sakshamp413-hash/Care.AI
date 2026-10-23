"""Every SKILL.md must follow the Agent Skills spec plus our Scam Kavach sections."""
import re

import pytest

from app.skills import SKILLS_DIR, load_skills, match_rules, split_frontmatter

SKILLS = load_skills()
SCAMS = [s for s in SKILLS if s.kind == "scam"]


def test_all_expected_skills_present():
    names = {s.name for s in SKILLS}
    assert {"upi-collect-trap", "kyc-sms-trap", "remote-app-trap", "digital-arrest-trap",
            "otp-share-trap", "phone-guide-hindi"} <= names


@pytest.mark.parametrize("skill", SKILLS, ids=lambda s: s.name)
def test_frontmatter_follows_agent_skills_spec(skill):
    meta, _ = split_frontmatter(skill.path.read_text(encoding="utf-8"))
    assert skill.name == skill.path.parent.name, "name must match folder name"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", skill.name) and len(skill.name) <= 64
    assert 20 <= len(skill.description) <= 1024
    assert meta.get("license") == "MIT"
    md = meta["metadata"]
    assert all(isinstance(v, str) for v in md.values()), "metadata values must be strings"
    assert md["kind"] in {"scam", "guide"}
    assert md["severity"] in {"high", "caution", "none"}
    assert md["version"]


@pytest.mark.parametrize("skill", SCAMS, ids=lambda s: s.name)
def test_scam_skill_has_required_sections(skill):
    for section in ("signals", "warning", "explanation", "example"):
        assert skill.sections.get(section), f"missing ## {section.title()}"
    assert skill.severity in {"high", "caution"}
    assert skill.signals, "needs at least one signal rule"
    assert re.search(r"[ऀ-ॿ]", skill.warning_hi), "warning must be in Hindi"


@pytest.mark.parametrize("skill", SCAMS, ids=lambda s: s.name)
def test_each_skill_catches_its_own_example(skill):
    hits = {s.name for s, _ in match_rules(skill.example)}
    assert skill.name in hits


def test_guide_skill_has_rules_and_forbids_pin():
    guide = next(s for s in SKILLS if s.name == "phone-guide-hindi")
    assert guide.kind == "guide"
    assert "PIN" in guide.sections["rules"] and "20" in guide.sections["rules"]


def test_skills_dir_has_no_stray_folders():
    for folder in SKILLS_DIR.iterdir():
        if folder.is_dir():
            assert (folder / "SKILL.md").exists(), f"{folder.name} has no SKILL.md"
