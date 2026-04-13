import json
from wikiagent.tool import Tool

_TODO_STORE: dict[str, list[dict]] = {}


def _todo_create(name: str, description: str = "") -> str:
    if name in _TODO_STORE:
        return "[Error] Todo list '{}' already exists.".format(name)
    _TODO_STORE[name] = []
    return "Todo list '{}' created.".format(name) + (" Description: {}".format(description) if description else "")


def _todo_write(name: str, todos) -> str:
    if name not in _TODO_STORE:
        _TODO_STORE[name] = []
    try:
        if isinstance(todos, str):
            items = json.loads(todos)
        else:
            items = todos
        _TODO_STORE[name] = items
        return "Todo list '{}' updated with {} items.".format(name, len(items))
    except json.JSONDecodeError as e:
        return "[Error] Invalid JSON: {}".format(e)
    except Exception as e:
        return "[Error] {}".format(e)


def _todo_read(name: str = "") -> str:
    if name:
        if name not in _TODO_STORE:
            return "[Error] Todo list '{}' not found.".format(name)
        return json.dumps(_TODO_STORE[name], ensure_ascii=False, indent=2)
    if not _TODO_STORE:
        return "(No todo lists)"
    result = []
    for list_name, items in _TODO_STORE.items():
        result.append("=== {} ({} items) ===".format(list_name, len(items)))
        for item in items:
            status = item.get("status", "pending")
            marker = "✅" if status == "completed" else "⏳" if status == "in_progress" else "⬚"
            result.append("  {} [{}] {}".format(marker, item.get("id", "?"), item.get("content", "")))
    return "\n".join(result)


def make_todo_create_tool() -> Tool:
    return Tool(
        name="todo_create",
        description="Create a new todo list to track tasks. Use this first when you have a multi-step task to complete. Todo lists help organize work and track progress.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the new todo list."},
                "description": {"type": "string", "description": "Optional description of what this todo list tracks."},
            },
            "required": ["name"],
        },
        execute=lambda name, description="": _todo_create(name, description),
    )


def make_todo_write_tool() -> Tool:
    return Tool(
        name="todo_write",
        description="Write or update todo items in an existing todo list. IMPORTANT: You can pass either a JSON string OR a LIST as the todos parameter. If you pass a list, it will be automatically converted to JSON for you! Each todo item should have: id (string), content (task description), status (pending|in_progress|completed). Use this to initialize todo items OR update their status as you progress through tasks.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the todo list to update."},
                "todos": {"type": "string", "description": "JSON array OR list: [{\"id\": \"1\", \"content\": \"...\", \"status\": \"pending|in_progress|completed\"}]"},
            },
            "required": ["name", "todos"],
        },
        execute=lambda name, todos: _todo_write(name, todos),
    )


def make_todo_read_tool() -> Tool:
    return Tool(
        name="todo_read",
        description="Read todo list(s) to see current status. Use this to check what tasks remain or review progress. If name is omitted, shows all todo lists.",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of todo list to read (empty = all lists)."},
            },
            "required": [],
        },
        execute=lambda name="": _todo_read(name),
    )
