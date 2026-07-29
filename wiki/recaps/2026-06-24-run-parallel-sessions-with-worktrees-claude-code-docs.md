---
type: recap
title: "Recap — Run parallel sessions with worktrees (Claude Code docs)"
created: 2026-06-26
updated: 2026-06-26
status: stable
sources: [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]
tags: [claude-code, git, worktrees, agentic-coding, docs]
---

# Recap — Run parallel sessions with worktrees (Claude Code docs)

Official [[entities/claude-code]] documentation on using
[[concepts/git-worktrees]] to run multiple isolated sessions in parallel
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Key claims

- A git worktree is a separate working directory with its own files and branch sharing
  the same repo history/remote. Running each session in its own worktree means edits in
  one never touch another — e.g. building a feature in one terminal while fixing a bug
  in a second [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- **Start one:** `claude --worktree <name>` (or `-w`) creates a worktree under
  `.claude/worktrees/<name>/` on branch `worktree-<name>`; omit the name to auto-generate
  one. The desktop app makes a worktree for every new session automatically
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Worktrees branch from the repo's **default branch** (`origin/HEAD`) by default; set
  `worktree.baseRef: "head"` to carry unpushed commits. Branch from a PR with
  `claude --worktree "#1234"` [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- A `.worktreeinclude` file (gitignore syntax) copies gitignored files like `.env` into
  new worktrees; tracked files are never duplicated
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- **Subagent isolation:** add `isolation: worktree` to a custom subagent's frontmatter
  (or ask Claude to "use worktrees for your agents") so parallel edits don't conflict;
  each gets a temporary worktree removed automatically if it finishes without changes
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- **Cleanup:** clean worktrees (no changes/untracked/new commits) are auto-removed;
  dirty ones prompt to keep or remove. Subagent/background worktrees are swept after
  `cleanupPeriodDays`; `--worktree` ones are never swept. `git worktree remove` (with
  `--force`) cleans up manually
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- **Non-git VCS** (SVN, Perforce, Mercurial) is supported via `WorktreeCreate` /
  `WorktreeRemove` hooks
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

Worktrees isolate **file edits**; subagents and agent teams coordinate the **work** —
together a building block of [[concepts/agentic-engineering]]
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Entities mentioned

- [[entities/claude-code]] (incl. Anthropic — see [[entities/anthropic]])

## Concepts mentioned

- [[concepts/git-worktrees]], [[concepts/agentic-engineering]]

## Source

`sources/2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs.md` —
official docs page (code.claude.com/docs/en/worktrees).
