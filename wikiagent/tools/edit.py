import os
from wikiagent.tool import Tool


def _execute_edit(file_path: str, old_str: str, new_str: str) -> str:
    try:
        if not os.path.exists(file_path):
            return "[Error] File not found: {}".format(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_str not in content:
            return "[Error] old_str not found in {}".format(file_path)
        count = content.count(old_str)
        if count > 1:
            return "[Error] old_str matches {} times in {}. Please provide a more specific old_str.".format(count, file_path)
        new_content = content.replace(old_str, new_str, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return "Successfully edited {}".format(file_path)
    except Exception as e:
        return "[Error] {}".format(e)


def make_edit_tool() -> Tool:
    return Tool(
        name="edit",
        description=(
            "Edit a file by replacing a specific string block. PREFERRED OVER BASH for file edits. "
            "old_str must match EXACTLY (including whitespace) and EXACTLY ONCE. "
            "Always read the file first with 'read' tool to see the line numbers and exact content! "
            "Use this tool for all file modifications instead of trying to use sed/ed via bash. "
            "The replacement is safe and atomic - no partial writes."
        ),
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to edit.",
                },
                "old_str": {
                    "type": "string",
                    "description": "The EXACT string to find and replace (including newlines/spaces). Must match exactly once!",
                },
                "new_str": {
                    "type": "string",
                    "description": "The replacement string.",
                },
            },
            "required": ["file_path", "old_str", "new_str"],
        },
        execute=lambda file_path, old_str, new_str: _execute_edit(file_path, old_str, new_str),
    )
