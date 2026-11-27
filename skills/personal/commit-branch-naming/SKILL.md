---
name: commit-branch-naming
description: "Use whenever writing a git commit message or naming a new git branch, in any project. Enforces Conventional Commits format (TYPE(SCOPE): DESCRIPTION) for commit subjects, and a ticket-linked branch naming scheme (PREFIX/US-ID-DESC or PREFIX/TK-ID-DESC). Trigger before running `git commit` or creating a branch (`git branch`/`git checkout -b`/`git switch -c`) - check this skill first rather than writing an ad hoc message or name."
---

# Commit & branch naming standard

Personal convention, applies across all projects. Follow this instead of writing free-form commit messages or branch names.

## Commit messages

Template:
```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

### `<type>` — pick one

- `feat` — adds, adjusts, or removes a feature relevant to the API or UI
- `fix` — fixes a bug in a preceding `feat`
- `refactor` — rewrites/restructures code without changing API or UI behavior
  - `perf` — a `refactor` specifically for performance
- `style` — code style only (whitespace, formatting, missing semicolons) — no behavior change
- `test` — adds missing tests or fixes existing ones
- `docs` — documentation only
- `build` — build tooling, dependencies, project version
- `ops` — infrastructure (IaC), deployment scripts, CI/CD, backups, monitoring, recovery
- `chore` — everything else (initial commit, `.gitignore` tweaks, etc.)

### `<optional scope>`

Where the change lives (a module, a feature area). Omit if it doesn't add information.

### `<description>`

- Imperative, present tense: "add", not "added"/"adds" — think "this commit will ..."
- No capital letter at the start
- No trailing period

### Breaking changes

- Add `!` before the `:` in the subject: `feat(api)!: remove status endpoint`
- Explain in the footer if the description alone isn't enough, starting with `BREAKING CHANGE:` (space + text on one line, or two newlines then the text for multi-line)

### `<optional body>`

Motivation for the change, contrasted with previous behavior. Same imperative/present-tense style as the description.

### `<optional footer>`

Issue references (`Closes #123`, `Fixes JIRA-456`) and breaking-change details. Required only if the commit is breaking.

### Examples

```
feat: add email notifications on new direct messages
feat(shopping-cart): add the amazing button
fix(shopping-cart): prevent order an empty shopping cart
fix(api): fix wrong calculation of request body checksum
perf: decrease memory footprint for determine unique visitors by using HyperLogLog
build: update dependencies
build(release): bump version to 1.0.0
refactor: implement fibonacci number calculation as recursion
style: remove empty line
feat!: remove ticket list endpoint

BREAKING CHANGE: ticket endpoints no longer support list all entities.
```

### Applying this with `git commit`

```bash
git commit -m "<type>(<scope>): <description>" \
           -m "<optional body>" \
           -m "<optional footer>"
```

## Branch names

Format: `<prefix>/<US- or TK-><id>-<short-description>`

Example: `feature/TK-78-dark-mode`

### 1. Prefix — pick one

- `feature/` — new feature development
- `bugfix/` — bug fixes
- `hotfix/` — urgent fixes branched directly from production
- `release/` — release preparation
- `docs/` — documentation-only work

### 2. Ticket ID

Every branch traces back to a tracked work item so anyone reading the branch name can find the corresponding record (acceptance criteria, why the work was done, status).

- **Ask the user for the ID and its type** (User Story → `US-`, Ticket → `TK-`) before naming the branch — never invent one. If they mention a tracker (Notion or otherwise), ask them to look it up there.
- **If the project has no ticket/story tracking**, say so explicitly and drop the `US-`/`TK-<id>-` segment instead of blocking: `<prefix>/<short-description>` (e.g. `feature/dark-mode`).

### 3. Description

2-3 words, kebab-case (lowercase, spaces → `-`): `dark-mode`, `user-authentication`, `fix-plant-inventory`, `login-page`.

### Creating the branch

```bash
git checkout -b <prefix>/US-<id>-<description>
# or, without a tracked ticket:
git checkout -b <prefix>/<description>
```

Verify with `git branch` — the new branch should be listed and checked out.
