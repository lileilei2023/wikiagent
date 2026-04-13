import os
from wikiagent.tool import Tool


def _execute_ls(path: str = ".") -> str:
    try:
        if not os.path.exists(path):
            return "[Error] Path not found: {}".format(path)
        if not os.path.isdir(path):
            return "[Error] Not a directory: {}".format(path)
        entries = sorted(os.listdir(path))
        result_lines = []
        for entry in entries:
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                result_lines.append("  {}/".format(entry))
            else:
                size = os.path.getsize(full_path)
                result_lines.append("  {}  ({} bytes)".format(entry, size))
        return "{}:\n".format(path) + "\n".join(result_lines) if result_lines else "{}: (empty)".format(path)
    except Exception as e:
        return "[Error] {}".format(e)


def make_ls_tool() -> Tool:
    return Tool(
        name="ls",
        description=(
            "List files and directories at the given path. THIS IS THE FIRST TOOL YOU SHOULD USE WHEN EXPLORING A DIRECTORY. "
            "Shows both files and directories with sizes. Directories are marked with a trailing slash. "
            "ALWAYS use this tool instead of bash 'ls' or 'find'. "
            "You must use this tool to understand directory structure before doing anything else."
        ),
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list (default: current directory).",
                },
            },
            "required": [],
        },
        execute=lambda path=".": _execute_ls(path),
    )
