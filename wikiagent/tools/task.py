from wikiagent.tool import Tool


def _execute_task(prompt, subagent_type="explore", agent_factory=None):
    if agent_factory is None:
        return "[Error] Agent factory not configured. Cannot launch subagent."
    try:
        agent = agent_factory(subagent_type)
        if agent is None:
            return "[Error] Unknown subagent type: {}".format(subagent_type)
        print("\n" + chr(9472) * 40)
        print("  \U0001f916 Launching '{}' subagent".format(subagent_type))
        print(chr(9472) * 40)
        agent_result = agent.run(prompt)
        print("\n" + chr(9472) * 40)
        print("  \U0001f916 Subagent '{}' finished".format(subagent_type))
        print(chr(9472) * 40)
        return agent_result
    except Exception as e:
        return "[Error] Subagent failed: {}".format(e)


def make_task_tool(agent_factory=None):
    return Tool(
        name="task",
        description=(
            "Launch a subagent to handle a task autonomously with its own conversation. "
            "Subagents are great for: "
            "- Large exploration tasks that benefit from isolated context "
            "- Multi-step subtasks that would clutter the main conversation "
            "- Tasks requiring specialized tool sets "
            "Available types: "
            "'explore' (code exploration, read-only tools); "
            "'wiki_ingest' (read ONE source and integrate it into the markdown wiki); "
            "'wiki_query' (answer a question by searching and reading the wiki, read-only); "
            "'wiki_lint' (health-check the wiki, fix safe issues, report the rest). "
            "Provide a very detailed prompt so the subagent knows exactly what to do!"
        ),
        parameters={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "DETAILED task description for the subagent - be specific about what to do and what to return!",
                },
                "subagent_type": {
                    "type": "string",
                    "description": "Type of subagent to launch (default: 'explore').",
                    "enum": ["explore", "wiki_ingest", "wiki_query", "wiki_lint"],
                },
            },
            "required": ["prompt"],
        },
        execute=lambda prompt, subagent_type="explore": _execute_task(prompt, subagent_type, agent_factory),
    )
