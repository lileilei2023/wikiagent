import os
from wikiagent.tool import Tool


def _execute_write(file_path: str, content: str) -> str:
    try:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return "Successfully wrote {} characters to {}".format(len(content), file_path)
    except Exception as e:
        return "[Error] {}".format(e)


def make_write_tool() -> Tool:
    return Tool(
        name="write",
        description=(
            "Write content to a file - creates new files or overwrites existing ones. "
            "PREFERRED OVER BASH 'echo > file' or 'cat > file'. "
            "Automatically creates parent directories if they don't exist. "
            "Use this to create new files or completely rewrite existing ones. "
            "For partial edits, use the 'edit' tool instead."
        ),
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to write or create.",
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write to the file.",
                },
            },
            "required": ["file_path", "content"],
        },
        execute=lambda file_path, content: _execute_write(file_path, content),
    )
