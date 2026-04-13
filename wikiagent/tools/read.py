import os
from wikiagent.tool import Tool


def _execute_read(file_path: str, offset: int = 1, limit: int = 2000) -> str:
    try:
        if not os.path.exists(file_path):
            return "[Error] File not found: {}".format(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        total = len(lines)
        start = max(0, offset - 1)
        end = min(total, start + limit)
        selected = lines[start:end]
        numbered = []
        for i, line in enumerate(selected, start=start + 1):
            numbered.append("{:05d}| {}".format(i, line.rstrip()))
        header = "[{}] ({} lines total, showing {}-{})".format(file_path, total, start + 1, end)
        return header + "\n" + "\n".join(numbered)
    except Exception as e:
        return "[Error] {}".format(e)


def make_read_tool() -> Tool:
    return Tool(
        name="read",
        description=(
            "Read a file's content WITH LINE NUMBERS. EVERY LINE IS PREFIXED WITH ITS LINE NUMBER! "
            "ALWAYS use this tool instead of bash 'cat', 'head', or 'tail'. "
            "Use offset and limit parameters to read large files in chunks if needed. "
            "Line numbers are critical if you need to edit the file later with the 'edit' tool."
        ),
        parameters={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file to read.",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line number to start reading from (1-based, default: 1).",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read (default: 2000).",
                },
            },
            "required": ["file_path"],
        },
        execute=lambda file_path, offset=1, limit=2000: _execute_read(file_path, offset, limit),
    )
