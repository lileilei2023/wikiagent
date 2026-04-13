import subprocess
from wikiagent.tool import Tool


def _execute_grep(pattern: str, path: str = ".", include: str = "") -> str:
    try:
        cmd = ["grep", "-r", "-n", pattern, path]
        if include:
            cmd.insert(2, "--include={}".format(include))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        if not output:
            return "No matches found for pattern: {}".format(pattern)
        lines = output.split("\n")
        if len(lines) > 100:
            return "\n".join(lines[:100]) + "\n... ({} more lines)".format(len(lines) - 100)
        return output
    except subprocess.TimeoutExpired:
        return "[Error] grep timed out"
    except Exception as e:
        return "[Error] {}".format(e)


def make_grep_tool() -> Tool:
    return Tool(
        name="grep",
        description=(
            "Search INSIDE file contents using regular expressions. ALWAYS use this tool instead of bash 'grep'! "
            "This tool searches file contents RECURSIVELY and shows LINE NUMBERS. "
            "Use this when you want to find WHERE in files a string or pattern appears, "
            "not just which files contain it. "
            "Examples: "
            "- Search for 'def ' in all Python files: pattern='def ', include='*.py' "
            "- Search for TODO in all files: pattern='TODO' "
            "- Search for class definitions in specific directory: pattern='class ', path='src/'"
        ),
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern or plain text to search for in file contents.",
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search in (default: current directory).",
                },
                "include": {
                    "type": "string",
                    "description": "Optional file pattern filter (e.g., '*.py', '*.ts') to limit search.",
                },
            },
            "required": ["pattern"],
        },
        execute=lambda pattern, path=".", include="": _execute_grep(pattern, path, include),
    )
