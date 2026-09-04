#!/usr/bin/env python3
"""Reminder hook (not a hard block): nudge Claude to ask what to work on
instead of working directly on the repository's default branch.

Fires on SessionStart and after `git merge`/`git pull` (PostToolUse on Bash).
Silent no-op outside a git repo, or in a repo with no commits yet (initial setup).
"""
import json
import subprocess
import sys


def sh(*args):
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=5
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_git_repo():
    return sh("rev-parse", "--is-inside-work-tree") == "true"


def has_commits():
    return sh("rev-parse", "--verify", "HEAD") is not None


def current_branch():
    return sh("branch", "--show-current")


def default_branch():
    ref = sh("symbolic-ref", "refs/remotes/origin/HEAD")
    if ref:
        return ref.rsplit("/", 1)[-1]
    for candidate in ("main", "master"):
        if sh("rev-parse", "--verify", candidate) is not None:
            return candidate
    return None


def remind(hook_event_name):
    when = "after a merge" if hook_event_name == "PostToolUse" else "at session start"
    message = (
        f"You're on the repository's default branch {when}. "
        "Before making any change, ask the user what to work on this session "
        "and create/checkout a feature branch per the commit-branch-naming "
        "convention — do not edit files or commit directly on this branch."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": message,
        }
    }))


def main():
    hook_event_name = sys.argv[1] if len(sys.argv) > 1 else "SessionStart"
    # Drain stdin (hook input JSON) even though we don't need its fields here.
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    if not is_git_repo() or not has_commits():
        sys.exit(0)

    branch = current_branch()
    default = default_branch()
    if branch and default and branch == default:
        remind(hook_event_name)
    sys.exit(0)


if __name__ == "__main__":
    main()
