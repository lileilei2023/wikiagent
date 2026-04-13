import glob as glob_module
import os
from wikiagent.tool import Tool


def _execute_glob(pattern: str, path: str = ".") -> str:
    try:
        full_pattern = os.path.join(path, pattern)
        matches = sorted(glob_module.glob(full_pattern, recursive=True))
        if not matches:
            return "No files matched pattern: {} in {}".format(pattern, path)
        return "\n".join(matches)
    except Exception as e:
        return "[Error] {}".format(e)


def make_glob_tool() -> Tool:
    return Tool(
        name="glob",
        description=(
            "Find files by name using glob patterns. ALWAYS use this tool instead of bash 'find' for file discovery! "
            "Supports standard glob syntax: "
            "- '*.py' matches all Python files in current directory "
            "- '**/*.py' matches all Python files RECURSIVELY (including subdirectories) "
            "- 'src/**/*.ts' matches all TypeScript files under src/ directory "
            "- '*.{py,js}' matches both Python and JavaScript files "
            "Use this whenever you need to find files by their name or path pattern."
        ),
        parameters={
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern (e.g., '**/*.py', '*.txt', 'src/**/*.ts').",
                },
                "path": {
                    "type": "string",
                    "description": "Base directory to search in (default: current directory).",
                },
            },
            "required": ["pattern"],
        },
        execute=lambda pattern, path=".": _execute_glob(pattern, path),
    )
