#!/bin/bash
# Launch wikiagent.
# Usage:
#   ./start.sh                          # interactive mode
#   ./start.sh prompts/ingest.txt       # prompt file mode
#   ./start.sh prompts/batch_ingest.txt # batch mode

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)${PYTHONPATH:+:$PYTHONPATH}"

# Find the right python3 (homebrew or system)
if command -v /opt/homebrew/bin/python3 &>/dev/null; then
    PYTHON=/opt/homebrew/bin/python3
else
    PYTHON=python3
fi

# Inject wiki-specific system prompt into main agent
export WIKIAGENT_SYSTEM_PROMPT_FILE="wiki_main_prompt.md"

exec "$PYTHON" -m wikiagent.main "$@"
