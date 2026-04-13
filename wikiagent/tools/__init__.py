from wikiagent.tool import Tool, ToolRegistry
from wikiagent.tools.bash import make_bash_tool
from wikiagent.tools.edit import make_edit_tool
from wikiagent.tools.glob_tool import make_glob_tool
from wikiagent.tools.grep import make_grep_tool
from wikiagent.tools.ls import make_ls_tool
from wikiagent.tools.read import make_read_tool
from wikiagent.tools.write import make_write_tool
from wikiagent.tools.todo import make_todo_create_tool, make_todo_write_tool, make_todo_read_tool
from wikiagent.tools.task import make_task_tool
from wikiagent.tools.web_fetch import make_web_fetch_tool


def create_default_registry(agent_factory=None):
    registry = ToolRegistry()
    for tool in [
        make_bash_tool(),
        make_edit_tool(),
        make_glob_tool(),
        make_grep_tool(),
        make_ls_tool(),
        make_read_tool(),
        make_write_tool(),
        make_todo_create_tool(),
        make_todo_write_tool(),
        make_todo_read_tool(),
        make_web_fetch_tool(),
        make_task_tool(agent_factory),
    ]:
        registry.register(tool)
    return registry


def create_limited_registry(tool_names, agent_factory=None):
    full = create_default_registry(agent_factory)
    limited = ToolRegistry()
    for name in tool_names:
        tool = full.get(name)
        if tool:
            limited.register(tool)
    return limited
