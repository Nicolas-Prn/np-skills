#!/usr/bin/env bash
# Idempotent setup for this repo's Claude Code hooks.
# Symlinks each script into ~/.claude/hooks/ and merges its config into
# ~/.claude/settings.json — never overwrites existing settings/hooks.
# Requires jq.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS="$HOME/.claude/settings.json"

mkdir -p "$HOME/.claude/hooks"
[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"

link() {
  local name="$1"
  ln -sf "$REPO_DIR/hooks/$name" "$HOME/.claude/hooks/$name"
  echo "Linked ~/.claude/hooks/$name -> $REPO_DIR/hooks/$name"
}

# register_hook <event> <matcher-or-empty> <if-filter-or-empty> <command> <statusMessage>
register_hook() {
  local event="$1" matcher="$2" if_filter="$3" command="$4" status="$5"

  local already
  already=$(jq -e --arg ev "$event" --arg cmd "$command" --arg iff "$if_filter" '
    (.hooks[$ev] // [])[] | .hooks[]? | select(.command == $cmd and ((.if // "") == $iff))
  ' "$SETTINGS" > /dev/null 2>&1 && echo yes || echo no)

  if [ "$already" = "yes" ]; then
    echo "Hook already registered for $event ($command | if=$if_filter), skipping."
    return
  fi

  local tmp
  tmp="$(mktemp)"
  jq --arg ev "$event" --arg matcher "$matcher" --arg iff "$if_filter" \
     --arg cmd "$command" --arg status "$status" '
    def entry:
      {"type": "command", "command": $cmd, "statusMessage": $status}
      + (if $iff == "" then {} else {"if": $iff} end);
    .hooks[$ev] = ((.hooks[$ev] // []) + [
      ({"hooks": [entry]} + (if $matcher == "" then {} else {"matcher": $matcher} end))
    ])
  ' "$SETTINGS" > "$tmp"
  mv "$tmp" "$SETTINGS"
  echo "Registered hook for $event ($command | if=$if_filter)"
}

link validate-git-conventions.py
link branch-guard.py

register_hook "PreToolUse" "Bash" "Bash(git *)" \
  "python3 ~/.claude/hooks/validate-git-conventions.py" \
  "Checking commit/branch naming conventions..."

register_hook "SessionStart" "" "" \
  "python3 ~/.claude/hooks/branch-guard.py SessionStart" \
  "Checking current branch..."

register_hook "PostToolUse" "Bash" "Bash(git merge*)" \
  "python3 ~/.claude/hooks/branch-guard.py PostToolUse" \
  "Checking branch after merge..."

register_hook "PostToolUse" "Bash" "Bash(git pull*)" \
  "python3 ~/.claude/hooks/branch-guard.py PostToolUse" \
  "Checking branch after pull..."
