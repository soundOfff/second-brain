---
type: entity
title: Claude Code
created: 2026-06-23
updated: 2026-06-26
status: active
sources: [2026-06-23-karpathy-llm-wiki, 2026-06-24-2025-llm-year-in-review, 2026-06-24-sequoia-ascent-2026-summary, 2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs, 2026-06-24-opfs-pyodide-test-harness]
tags: [tool, ai, agent]
aliases: [Claude Code CLI, CC]
---

# Claude Code

[[entities/anthropic]]'s agentic coding tool. It is the **AI engine** that owns and
maintains an [[concepts/llm-wiki]]: its **skills** (`.claude/skills/<name>/SKILL.md`)
implement the `/capture`, `/sync`, `/lint`, `/digest` operations, and its `CLAUDE.md`
schema makes it a disciplined maintainer rather than a generic chatbot
[2026-06-23-karpathy-llm-wiki].

## "AI that lives on your computer"

[[entities/andrej-karpathy]] calls Claude Code the **first convincing demonstration of an
LLM agent** — looping tool-use and reasoning for extended problem solving — and credits
its **local-first** design: it runs on your computer with your private environment, data,
secrets, and low-latency context. He argues Anthropic got the "order of precedence" right
(vs. [[entities/openai]]'s early cloud-container focus for Codex), packaging CC as a
minimal CLI — "a little spirit/ghost that lives on your computer," a new interaction
paradigm [2026-06-24-2025-llm-year-in-review]. See [[concepts/ghosts-vs-animals]].

## Capabilities seen in the batch

- **Worktrees / parallel sessions.** `claude --worktree <name>` runs each session in an
  isolated [[concepts/git-worktrees|git worktree]] so parallel edits never collide;
  subagents can be isolated with `isolation: worktree`. A building block of
  [[concepts/agentic-engineering]]
  [2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs].
- **Claude Code for web.** [[entities/simon-willison]] had "Claude Code for web" build a
  browser playground UI to test OPFS behaviour
  [2026-06-24-opfs-pyodide-test-harness].

Listed alongside [[entities/codex]] and [[entities/cursor]] as the agentic coding tools
that became reliable around the December 2025 inflection
[2026-06-24-sequoia-ascent-2026-summary]. Its scheduling feature can run `/digest` (and,
here, `/sync`) on a recurring basis.
