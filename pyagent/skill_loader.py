from __future__ import annotations

import os
import re
from dataclasses import dataclass


@dataclass
class SkillInfo:
    name: str
    description: str
    path: str
    content: str


def _parse_frontmatter(text: str) -> dict:
    match = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not match:
        return {}
    fm_text = match.group(1)
    result = {}
    current_key = None
    current_value_lines = []

    for line in fm_text.split('\n'):
        kv_match = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if kv_match:
            if current_key is not None:
                result[current_key] = ' '.join(current_value_lines).strip()
            current_key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val == '>':
                current_value_lines = []
            else:
                current_value_lines = [val]
        elif current_key is not None:
            current_value_lines.append(line.strip())

    if current_key is not None:
        result[current_key] = ' '.join(current_value_lines).strip()

    return result


def load_skills(skills_dir: str) -> list[SkillInfo]:
    skills = []
    if not os.path.isdir(skills_dir):
        return skills

    for entry in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, entry)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_file):
            continue

        try:
            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue

        fm = _parse_frontmatter(content)
        name = fm.get("name", entry)
        description = fm.get("description", "")

        if name and description:
            skills.append(SkillInfo(
                name=name,
                description=description,
                path=skill_file,
                content=content,
            ))

    return skills


def get_skills_summary(skills: list[SkillInfo]) -> str:
    if not skills:
        return "(No skills available)"
    lines = []
    for i, s in enumerate(skills, 1):
        lines.append("{}. {}: {}".format(i, s.name, s.description))
    return "\n".join(lines)
