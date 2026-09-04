#!/usr/bin/env bash
# Idempotent setup for the git-conventions PreToolUse hook.
# Symlinks the script into ~/.claude/hooks/ and merges its config into
# ~/.claude/settings.json (never overwrites existing settings/hooks).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_SRC="$REPO_DIR/hooks/validate-git-conventions.py"
SCRIPT_DEST="$HOME/.claude/hooks/validate-git-conventions.py"
SETTINGS="$HOME/.claude/settings.json"
HOOK_COMMAND="python3 ~/.claude/hooks/validate-git-conventions.py"

mkdir -p "$HOME/.claude/hooks"
ln -sf "$SCRIPT_SRC" "$SCRIPT_DEST"
echo "Linked $SCRIPT_DEST -> $SCRIPT_SRC"

if [ ! -f "$SETTINGS" ]; then
  echo '{}' > "$SETTINGS"
fi

if jq -e --arg cmd "$HOOK_COMMAND" \
  '.hooks.PreToolUse[]? | select(.matcher == "Bash") | .hooks[]? | select(.command == $cmd)' \
  "$SETTINGS" > /dev/null 2>&1; then
  echo "Hook already registered in $SETTINGS, skipping."
else
  tmp="$(mktemp)"
  jq --arg cmd "$HOOK_COMMAND" '
    .hooks.PreToolUse = ((.hooks.PreToolUse // []) + [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": $cmd,
        "if": "Bash(git *)",
        "statusMessage": "Checking commit/branch naming conventions..."
      }]
    }])
  ' "$SETTINGS" > "$tmp"
  mv "$tmp" "$SETTINGS"
  echo "Registered git-conventions hook in $SETTINGS"
fi
