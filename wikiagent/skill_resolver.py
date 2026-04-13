from __future__ import annotations

from wikiagent.skill_loader import SkillInfo, get_skills_summary
from wikiagent.agent import Agent, AgentResult
from wikiagent.llm import LLMClient
from wikiagent.tool import ToolRegistry

SKILL_MATCHER_SYSTEM_PROMPT = (
    "You are a skill matcher agent. Your ONLY job is to determine which skills "
    "(if any) are relevant to the user's task.\n"
    "## Instructions\n"
    "- You will be given a list of available skills with their names and descriptions.\n"
    "- You will be given a user task description.\n"
    "- Determine which skill(s) are relevant.\n"
    "- Respond with ONLY the matching skill name(s), one per line.\n"
    "- If no skill matches, respond with ONLY the word 'none'.\n"
    "- Do NOT explain your reasoning. Just output skill name(s) or 'none'.\n"
)


def resolve_skills(
    user_prompt: str,
    skills: list[SkillInfo],
    llm: LLMClient,
) -> tuple[list[SkillInfo], AgentResult | None]:
    if not skills:
        return [], None

    summary = get_skills_summary(skills)

    matcher_prompt = (
        "## Available Skills\n{}\n\n"
        "## User Task\n{}\n\n"
        "Which skill(s) are relevant to this task? "
        "Reply with skill name(s) one per line, or 'none'."
    ).format(summary, user_prompt)

    print("\n" + chr(9472) * 50)
    print("  \U0001f3af Skill Resolver: matching skills...")
    print(chr(9472) * 50)

    matcher = Agent(
        llm=llm,
        tool_registry=ToolRegistry(),
        system_prompt=SKILL_MATCHER_SYSTEM_PROMPT,
        max_rounds=1,
        enable_logging=False,
    )
    matcher_result = matcher.run(matcher_prompt)

    raw_output = matcher_result.content.strip().lower()

    print("\n" + chr(9472) * 50)
    print("  \U0001f3af Skill Resolver result: {}".format(raw_output))
    print(chr(9472) * 50)

    if raw_output == "none" or not raw_output:
        return [], matcher_result

    matched = []
    output_lines = [line.strip().lower() for line in raw_output.split("\n") if line.strip()]
    for s in skills:
        name_lower = s.name.lower()
        for line in output_lines:
            if name_lower == line or name_lower in line or line in name_lower:
                matched.append(s)
                break

    return matched, matcher_result


def build_skill_prompt_section(matched_skills: list[SkillInfo]) -> str:
    if not matched_skills:
        return ""

    parts = [
        "\n## Activated Skills",
        "The following skills have been matched to the user's task. "
        "You MUST follow the instructions and workflows defined in these skills "
        "when they are relevant to the task at hand.\n",
    ]

    for s in matched_skills:
        parts.append("### Skill: {}".format(s.name))
        parts.append("**Description**: {}\n".format(s.description))
        parts.append(s.content)
        parts.append("")

    return "\n".join(parts)
