from wikiagent.subagents.explore import EXPLORE_SYSTEM_PROMPT, EXPLORE_TOOLS
from wikiagent.subagents.wiki_ingest import WIKI_INGEST_SYSTEM_PROMPT, WIKI_INGEST_TOOLS
from wikiagent.subagents.wiki_query import WIKI_QUERY_SYSTEM_PROMPT, WIKI_QUERY_TOOLS
from wikiagent.subagents.wiki_lint import WIKI_LINT_SYSTEM_PROMPT, WIKI_LINT_TOOLS

SUBAGENT_CONFIGS = {
    "explore": {
        "system_prompt": EXPLORE_SYSTEM_PROMPT,
        "tool_names": EXPLORE_TOOLS,
    },
    "wiki_ingest": {
        "system_prompt": WIKI_INGEST_SYSTEM_PROMPT,
        "tool_names": WIKI_INGEST_TOOLS,
    },
    "wiki_query": {
        "system_prompt": WIKI_QUERY_SYSTEM_PROMPT,
        "tool_names": WIKI_QUERY_TOOLS,
    },
    "wiki_lint": {
        "system_prompt": WIKI_LINT_SYSTEM_PROMPT,
        "tool_names": WIKI_LINT_TOOLS,
    },
}
