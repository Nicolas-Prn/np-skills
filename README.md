# np-skills

Nicolas's personal Claude Code skills.

## Origin & license

This repo **started as a fork of [mattpocock/skills](https://github.com/mattpocock/skills)**, MIT-licensed, © Matt Pocock. The original [`LICENSE`](./LICENSE) file and its copyright notice are kept as required by the MIT license and apply to every file that still derives from that original work.

The intent, however, is to **diverge**: skills here are being rewritten and adapted to my own conventions (commit/branch naming, testing preferences, coding standards, workflow habits) skill by skill, until this becomes a fully personal set rather than a customized copy. As a skill is substantially rewritten, its `SKILL.md` gets a short note on what changed from upstream and why; skills not yet touched are still effectively Matt Pocock's original work under MIT terms.

## Installation

As a Claude Code plugin, from any machine:

```
/plugin marketplace add Nicolas-Prn/np-skills
/plugin install np-skills
```

## Global instructions (CLAUDE.md)

[`CLAUDE.md`](./CLAUDE.md) at the repo root holds standing personal preferences that should apply automatically in every project, on every machine — e.g. always write code in English, keep inline comments minimal and put substance in docs. This is the single source of truth; `~/.claude/CLAUDE.md` on each machine is a symlink to it, not a separate copy.

Setup on a (new) machine:

```bash
git clone git@github.com:Nicolas-Prn/np-skills.git ~/Documents/np-skills
ln -sf ~/Documents/np-skills/CLAUDE.md ~/.claude/CLAUDE.md
```

To change a global preference: edit `CLAUDE.md` in this repo and commit/push — every machine picks it up on the next `git pull` since `~/.claude/CLAUDE.md` just points at this file.

## Hooks (deterministic enforcement)

Some conventions can't rely on Claude remembering to apply them — they need to be enforced by the harness itself, before or after a tool call runs, independent of Claude's judgment in the moment.

- [`hooks/validate-git-conventions.py`](./hooks/validate-git-conventions.py) — `PreToolUse` hook that **blocks** `git commit`/`git branch`/`git checkout -b`/`git switch -c` calls that don't follow the [commit-branch-naming](./skills/personal/commit-branch-naming/SKILL.md) convention.
- [`hooks/branch-guard.py`](./hooks/branch-guard.py) — reminder (not a block) fired on `SessionStart` and after `git merge`/`git pull`: if the current branch is the repo's default branch (and it already has commits — a brand-new repo's initial setup is exempt), it nudges Claude to ask what to work on and create a feature branch before touching any files, instead of working directly on the default branch.

Setup on a (new) machine, after cloning the repo (see above):

```bash
./hooks/install.sh
```

This symlinks the script into `~/.claude/hooks/` and merges its config into `~/.claude/settings.json` — it never overwrites existing settings or hooks, and running it again is a no-op if already installed. Requires `jq`.

## Structure

- `CLAUDE.md` — global personal preferences, symlinked into `~/.claude/CLAUDE.md` on every machine (see above)
- `hooks/` — deterministic enforcement scripts + their setup script (see above)
- `skills/engineering/` — TDD, code review, diagnosing bugs, domain modeling, codebase design, spec/ticket flows, and more
- `skills/productivity/` — grilling, handoff, teaching, writing for agents, and more
- `skills/personal/` — skills that are fully mine from the start (not derived from Pocock's set), e.g. commit/branch naming conventions

## Credits

Original skills by [Matt Pocock](https://www.aihero.dev) ([mattpocock/skills](https://github.com/mattpocock/skills)), MIT licensed.
