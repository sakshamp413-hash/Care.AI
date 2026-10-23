"""Load Agent Skills (skills/*/SKILL.md) and run the deterministic Scam Kavach rules.

Each scam skill lists keyword rules under "## Signals", one per bullet.
"&&" joins terms that must ALL appear. Terms match at the START of a word,
so "otp" matches "OTP:" but not "footprint".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

SEVERITY_RANK = {"none": 0, "caution": 1, "high": 2}

# Letters, digits and Devanagari count as "inside a word".
_WORD_CHARS = r"0-9a-zऀ-ॿ"


@dataclass
class Skill:
    name: str
    description: str
    kind: str  # "scam" | "guide"
    severity: str  # "high" | "caution" | "none"
    version: str
    license: str
    body: str
    sections: dict[str, str]
    signals: list[list[str]] = field(default_factory=list)
    path: Path | None = None

    @property
    def warning_hi(self) -> str:
        return self.sections.get("warning", "").strip()

    @property
    def explanation_hi(self) -> str:
        return self.sections.get("explanation", "").strip()

    def warning(self, lang: str = "hi") -> str:
        """Spoken warning in the user's language (English section optional, falls back to Hindi)."""
        if lang == "en":
            return self.sections.get("warning (english)", "").strip() or self.warning_hi
        return self.warning_hi

    def explanation(self, lang: str = "hi") -> str:
        if lang == "en":
            return self.sections.get("explanation (english)", "").strip() or self.explanation_hi
        return self.explanation_hi

    @property
    def example(self) -> str:
        return self.sections.get("example", "").strip()

    def public(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "severity": self.severity,
            "version": self.version,
            "warning_hi": self.warning_hi,
            "warning_en": self.warning("en"),
            "signals": [" && ".join(s) for s in self.signals],
        }


def split_frontmatter(text: str) -> tuple[dict, str]:
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Unterminated YAML frontmatter")
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return meta, parts[2]


def parse_sections(body: str) -> dict[str, str]:
    """Map lower-cased '## Heading' -> section text."""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip().lower(), []
        elif current:
            buf.append(line)
    if current:
        sections[current] = "\n".join(buf).strip()
    return sections


def parse_signals(section: str) -> list[list[str]]:
    rules = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith(("-", "*")):
            continue
        terms = [t.strip().strip("`\"'").lower() for t in line[1:].split("&&")]
        terms = [t for t in terms if t]
        if terms:
            rules.append(terms)
    return rules


def load_skill(path: Path) -> Skill:
    meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
    md = meta.get("metadata") or {}
    sections = parse_sections(body)
    return Skill(
        name=str(meta.get("name", "")),
        description=str(meta.get("description", "")).strip(),
        kind=str(md.get("kind", "")),
        severity=str(md.get("severity", "none")),
        version=str(md.get("version", "")),
        license=str(meta.get("license", "")),
        body=body.strip(),
        sections=sections,
        signals=parse_signals(sections.get("signals", "")),
        path=path,
    )


@lru_cache(maxsize=1)
def load_skills() -> tuple[Skill, ...]:
    return tuple(load_skill(p) for p in sorted(SKILLS_DIR.glob("*/SKILL.md")))


def scam_skills() -> list[Skill]:
    return [s for s in load_skills() if s.kind == "scam"]


def get_skill(name: str) -> Skill | None:
    return next((s for s in load_skills() if s.name == name), None)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower())


@lru_cache(maxsize=1024)
def _term_regex(term: str) -> re.Pattern:
    words = [re.escape(w) for w in term.split()]
    return re.compile(rf"(?<![{_WORD_CHARS}])" + r"\s+".join(words))


def term_in(term: str, text: str) -> bool:
    return bool(_term_regex(term).search(text))


def match_rules(text: str, skills: list[Skill] | None = None) -> list[tuple[Skill, list[str]]]:
    """Return every (skill, matched_rule) whose rule fires on the text."""
    norm = normalize(text)
    hits = []
    for skill in skills if skills is not None else scam_skills():
        for rule in skill.signals:
            if all(term_in(t, norm) for t in rule):
                hits.append((skill, rule))
                break
    return hits


def best_rule_hit(text: str) -> tuple[Skill, list[str]] | None:
    hits = match_rules(text)
    if not hits:
        return None
    return max(hits, key=lambda h: SEVERITY_RANK.get(h[0].severity, 0))
