---
type: recap
title: "Recap — Run parallel sessions with worktrees (Claude Code Docs)"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]
tags: [claude-code, git, worktrees, documentation, dev-tools]
---

# Recap — Run parallel sessions with worktrees (Claude Code Docs)

Official **[[entities/claude-code]]** documentation explaining how git
**[[concepts/git-worktrees]]** are used to run multiple isolated Claude Code sessions in
parallel against the same repository without their file edits colliding
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. `claude --worktree
<name>` creates an isolated worktree (default location `.claude/worktrees/<value>/`, new
branch `worktree-<value>`) and starts a session in it; omitting a name auto-generates one;
Claude can also be asked mid-session to "work in a worktree," which invokes the
`EnterWorktree` tool [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
Worktrees branch from the repo's default remote branch (`origin/HEAD`) unless
`worktree.baseRef` is set to `"head"`, and a worktree can also be created directly from a
GitHub PR number or URL [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

A `.worktreeinclude` file (gitignore syntax) copies specified gitignored files (e.g.
`.env`, `config/secrets.json`) into every new worktree, since a worktree is a fresh
checkout that otherwise lacks untracked local files
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. Subagents can be
isolated in their own worktrees too — either by asking Claude to "use worktrees for your
agents" or by setting `isolation: worktree` in a custom subagent's frontmatter — and such
worktrees are removed automatically once the subagent finishes without changes
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. Cleanup behavior on
exit depends on whether changes were made: clean worktrees are auto-removed, dirty ones
prompt to keep or discard; non-interactive (`-p`) runs are never auto-cleaned and must be
removed manually with `git worktree remove`
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. Background/subagent
worktrees age out automatically past a configurable `cleanupPeriodDays` if they have no
uncommitted changes, and Claude runs `git worktree lock` on a worktree while an agent is
actively using it to prevent concurrent cleanup from removing it
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. For non-git version
control systems, `WorktreeCreate`/`WorktreeRemove` hooks can fully replace the default git
logic [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Key claims

- `claude --worktree <name>` creates an isolated git worktree under
  `.claude/worktrees/<value>/` on a new branch `worktree-<value>` and starts a session
  there [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Worktrees branch from `origin/HEAD` by default; setting `worktree.baseRef` to `"head"`
  makes new worktrees branch from local HEAD instead (only `"fresh"` or `"head"` are valid
  values) [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- A worktree can be created directly from a GitHub PR via `claude --worktree "#1234"`, at
  `.claude/worktrees/pr-<number>` [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- A `.worktreeinclude` file (gitignore syntax) copies specified gitignored files into every
  new worktree; only files that are both matched and gitignored are copied
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Custom subagents can set `isolation: worktree` in frontmatter to always run in an
  isolated, auto-cleaned worktree [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Non-interactive runs (`claude -p --worktree`) are never auto-cleaned since there's no
  exit prompt; they must be removed manually via `git worktree remove`
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- Claude runs `git worktree lock` on a worktree while an agent is active in it, so the
  periodic cleanup sweep (governed by `cleanupPeriodDays`) can't remove it mid-use
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].

## Entities mentioned

- [[entities/claude-code]]

## Concepts mentioned

- [[concepts/git-worktrees]]

## Source

`sources/2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs.md`
