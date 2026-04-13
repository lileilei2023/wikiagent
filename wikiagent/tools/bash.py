import subprocess
from wikiagent.tool import Tool


def _execute_bash(command: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=None,
        )
        output_parts = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            output_parts.append("[stderr]\n{}".format(result.stderr))
        if result.returncode != 0:
            output_parts.append("[exit code: {}]".format(result.returncode))
        return "\n".join(output_parts) if output_parts else "(no output)"
    except subprocess.TimeoutExpired:
        return "[Error] Command timed out after {}s".format(timeout)
    except Exception as e:
        return "[Error] {}".format(e)


def make_bash_tool() -> Tool:
    return Tool(
        name="bash",
        description=(
            "Execute arbitrary bash commands. Only use this when NO OTHER TOOL fits the task. "
            "ALWAYS prefer using dedicated tools instead: "
            "- Use 'ls' for listing directories instead of 'ls' via bash "
            "- Use 'read' for reading files instead of 'cat' via bash "
            "- Use 'glob' for finding files instead of 'find' via bash "
            "- Use 'grep' for searching file contents instead of 'grep' via bash "
            "Use this tool only for tasks that require complex shell pipelines or commands with no dedicated tools."
        ),
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute (only use when no other tool fits).",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30).",
                },
            },
            "required": ["command"],
        },
        execute=lambda command, timeout=30: _execute_bash(command, timeout),
    )
