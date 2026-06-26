---
type: concept
title: Git Worktrees (parallel isolated agent sessions)
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]
tags: [git, claude-code, agentic-coding, tooling]
aliases: [worktree, worktrees, parallel sessions]
---

# Git Worktrees

A **git worktree** is a separate working directory with its own files and branch that
**shares the same repository history and remote** as your main checkout
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. Running each
[[entities/claude-code]] session in its own worktree isolates **file edits**, so you can
build a feature in one terminal while fixing a bug in another without the sessions
touching each other's files
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Using them with Claude Code

- `claude --worktree <name>` (or `-w`) creates one under `.claude/worktrees/<name>/` on
  branch `worktree-<name>`; omitting the name auto-generates one. The desktop app makes a
  worktree per session automatically
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Worktrees branch from the repo's **default branch** (`origin/HEAD`) for a clean tree;
  set `worktree.baseRef: "head"` to carry unpushed/feature work, or
  `claude --worktree "#1234"` to branch from a PR
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- `.worktreeinclude` (gitignore syntax) copies gitignored config like `.env` into new
  worktrees; tracked files are never duplicated
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Isolating subagents

Add `isolation: worktree` to a custom subagent's frontmatter so parallel edits don't
conflict; each subagent gets a **temporary worktree removed automatically** if it
finishes without changes
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Cleanup

Clean worktrees (no changes, untracked files, or new commits) are auto-removed; dirty
ones prompt to keep or remove. Subagent/background worktrees are swept after
`cleanupPeriodDays`; `--worktree` ones are never swept. Use `git worktree remove`
(`--force` if dirty) to clean up manually
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Where it fits

Worktrees handle **file isolation**; subagents and agent teams coordinate the **work
itself**. Together they are a building block of [[concepts/agentic-engineering]] —
"isolate worktrees" is one of the named practices of preserving quality while running
agents in parallel [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
