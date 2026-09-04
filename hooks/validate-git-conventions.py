#!/usr/bin/env python3
"""PreToolUse hook: enforce personal commit/branch naming conventions on Bash git commands.

Convention source: ~/.claude/skills/commit-branch-naming/SKILL.md
(also published at skills/personal/commit-branch-naming/SKILL.md in the np-skills repo).
"""
import json
import re
import shlex
import sys

COMMIT_TYPES = "feat|fix|refactor|perf|style|test|docs|build|ops|chore"
COMMIT_RE = re.compile(
    rf"^({COMMIT_TYPES})(\([a-zA-Z0-9_./-]+\))?!?: [a-z0-9].*[^.]$"
)
BRANCH_RE = re.compile(
    r"^(feature|bugfix|hotfix|release|docs)/"
    r"((US|TK)-[0-9]+-)?[a-z0-9]+(-[a-z0-9]+)*$"
)

SKILL_HINT = "See ~/.claude/skills/commit-branch-naming/SKILL.md for the full convention."


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def allow() -> None:
    sys.exit(0)


def split_chained(command: str):
    """Split on shell chaining operators so `cd x && git commit ...` is still inspected."""
    parts = re.split(r"&&|\|\||;", command)
    return [p.strip() for p in parts if p.strip()]


def find_flag_value(tokens, flag_names):
    for i, tok in enumerate(tokens):
        if tok in flag_names and i + 1 < len(tokens):
            return tokens[i + 1]
        for flag in flag_names:
            if tok.startswith(flag + "="):
                return tok[len(flag) + 1:]
    return None


def check_commit(tokens):
    messages = [tok for i, tok in enumerate(tokens) if tokens[i - 1:i] == ["-m"] or tokens[i - 1:i] == ["--message"]]
    if not messages:
        # No -m: opens an editor, content unknowable here — nothing to validate.
        return
    subject = messages[0]
    if not COMMIT_RE.match(subject):
        deny(
            "Commit subject '" + subject + "' doesn't follow Conventional Commits format.\n"
            "Expected: <type>(<optional scope>): <description>\n"
            f"  type: one of {COMMIT_TYPES.replace('|', ', ')}\n"
            "  description: imperative present tense, starts lowercase, no trailing period\n"
            "Example: feat(auth): add password reset flow\n"
            + SKILL_HINT
        )


def check_branch_create(tokens):
    name = None
    if tokens[:2] == ["git", "checkout"] and "-b" in tokens:
        name = find_flag_value(tokens, ["-b"])
    elif tokens[:2] == ["git", "switch"] and "-c" in tokens:
        name = find_flag_value(tokens, ["-c"])
    elif tokens[:2] == ["git", "branch"]:
        positional = [t for t in tokens[2:] if not t.startswith("-")]
        if positional:
            name = positional[0]

    if name is None:
        return
    if not BRANCH_RE.match(name):
        deny(
            "Branch name '" + name + "' doesn't follow the naming convention.\n"
            "Expected: <prefix>/<US- or TK-><id>-<short-description>\n"
            "  prefix: one of feature, bugfix, hotfix, release, docs\n"
            "  or, if the project has no ticket tracking: <prefix>/<short-description>\n"
            "Example: feature/TK-78-dark-mode\n"
            + SKILL_HINT
        )


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        allow()
        return

    if payload.get("tool_name") != "Bash":
        allow()
        return

    command = payload.get("tool_input", {}).get("command", "")
    if not command:
        allow()
        return

    for segment in split_chained(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue
        if len(tokens) < 2 or tokens[0] != "git":
            continue
        if tokens[1] == "commit":
            check_commit(tokens)
        elif tokens[1] in ("checkout", "switch", "branch"):
            check_branch_create(tokens)

    allow()


if __name__ == "__main__":
    main()
