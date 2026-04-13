import os
import sys
import time

import yaml

from wikiagent.llm import LLMClient
from wikiagent.tools import create_default_registry, create_limited_registry
from wikiagent.agent import Agent, DEFAULT_SYSTEM_PROMPT
from wikiagent.subagents import SUBAGENT_CONFIGS
from wikiagent.skill_loader import load_skills
from wikiagent.skill_resolver import resolve_skills, build_skill_prompt_section


def _load_config():
    """Load LLM config from config.yaml, env vars, or fail with clear message.

    Priority (highest wins):
      1. Environment variables: WIKIAGENT_BASE_URL, WIKIAGENT_API_KEY, WIKIAGENT_MODEL
      2. config.yaml in current working directory
      3. config.yaml in project root (next to wikiagent/ package)
    """
    config = {}

    # Try config.yaml (cwd first, then project root)
    for candidate in ["config.yaml", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")]:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
            llm_section = raw.get("llm", {})
            config["base_url"] = llm_section.get("base_url", "")
            config["api_key"] = llm_section.get("api_key", "")
            config["model"] = llm_section.get("model", "")
            break

    # Env vars override config.yaml
    config["base_url"] = os.environ.get("WIKIAGENT_BASE_URL", config.get("base_url", ""))
    config["api_key"] = os.environ.get("WIKIAGENT_API_KEY", config.get("api_key", ""))
    config["model"] = os.environ.get("WIKIAGENT_MODEL", config.get("model", ""))

    # Validate
    missing = [k for k in ("base_url", "api_key", "model") if not config.get(k)]
    if missing:
        print("❌ Missing LLM config: {}".format(", ".join(missing)))
        print("   Set via config.yaml (llm.base_url / llm.api_key / llm.model)")
        print("   Or env vars: WIKIAGENT_BASE_URL, WIKIAGENT_API_KEY, WIKIAGENT_MODEL")
        sys.exit(1)

    return config


SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")


def create_subagent(subagent_type, config=None):
    cfg = config or _load_config()
    sa_config = SUBAGENT_CONFIGS.get(subagent_type)
    if sa_config is None:
        return None
    llm = LLMClient(base_url=cfg["base_url"], api_key=cfg["api_key"], model=cfg["model"])
    registry = create_limited_registry(sa_config["tool_names"])
    return Agent(
        llm=llm,
        tool_registry=registry,
        system_prompt=sa_config["system_prompt"],
        max_rounds=20,
        enable_logging=False,
    )


def main():
    start_time = time.time()

    config = _load_config()

    prompt_file = sys.argv[1] if len(sys.argv) > 1 else None
    if prompt_file:
        with open(prompt_file, "r", encoding="utf-8") as f:
            user_prompt = f.read().strip()
    else:
        user_prompt = input("Enter your prompt: ")

    print("\U0001f680 PyAgent starting...")

    skills = load_skills(SKILLS_DIR)
    print("\U0001f4e6 Loaded {} skills: {}".format(len(skills), [s.name for s in skills]))

    llm = LLMClient(base_url=config["base_url"], api_key=config["api_key"], model=config["model"])

    system_prompt = DEFAULT_SYSTEM_PROMPT
    # Allow injecting extra system prompt context via environment variable
    extra_prompt_file = os.environ.get("WIKIAGENT_SYSTEM_PROMPT_FILE")
    if extra_prompt_file and os.path.exists(extra_prompt_file):
        with open(extra_prompt_file, "r", encoding="utf-8") as f:
            extra_prompt = f.read().strip()
        system_prompt = extra_prompt + "\n\n" + system_prompt
        print("\U0001f4cb Loaded extra system prompt from: {}".format(extra_prompt_file))
    skill_resolve_log = None

    if skills:
        matched_skills, matcher_result = resolve_skills(user_prompt, skills, llm)
        if matcher_result is not None:
            skill_resolve_log = matcher_result.log
        if matched_skills:
            print("\u2705 Matched skills: {}".format([s.name for s in matched_skills]))
            skill_section = build_skill_prompt_section(matched_skills)
            system_prompt = system_prompt + skill_section
        else:
            print("\u2139\ufe0f No skills matched for this task.")

    print("\U0001f4dd Prompt: {}\n".format(user_prompt))

    registry = create_default_registry(agent_factory=lambda st: create_subagent(st, config))
    agent = Agent(llm=llm, tool_registry=registry, system_prompt=system_prompt)

    result = agent.run(user_prompt)

    if skill_resolve_log is not None:
        result.log["skill_resolver"] = skill_resolve_log

    total_time_min = (time.time() - start_time) / 60
    result.log["total_runtime_minutes"] = total_time_min

    if agent.enable_logging:
        agent._save_log(result.log)

    print("\n" + "=" * 50)
    print(f"  Total Runtime: {total_time_min:.2f} minutes")
    print("=" * 50)
    print("  Final Result")
    print("=" * 50)
    print(result.content)


if __name__ == "__main__":
    main()
