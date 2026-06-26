---
type: concept
title: Agentic Engineering
created: 2026-06-26
updated: 2026-06-26
status: active
sources: [2026-06-24-sequoia-ascent-2026-summary, 2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]
tags: [llm, agentic-coding, engineering, software, ai]
aliases: [agentic engineer]
---

# Agentic Engineering

The **professional engineering discipline** of coordinating fallible, stochastic agents
to go faster **while preserving the quality bar** — correctness, security, taste, and
maintainability [2026-06-24-sequoia-ascent-2026-summary]. [[entities/andrej-karpathy]]
contrasts it with [[concepts/vibe-coding]]:

> Vibe coding raises the **floor**. Agentic engineering raises the **ceiling**
> [2026-06-24-sequoia-ascent-2026-summary].

The agentic engineer does not blindly accept generated code. They **design specs,
supervise plans, inspect diffs, write tests, build evaluation loops, manage permissions,
isolate worktrees, and preserve quality** [2026-06-24-sequoia-ascent-2026-summary]. The
unit of work shifts from typing lines to delegating "macro actions" (implement a feature,
refactor a subsystem, research a library) — the programmer becomes an **orchestrator of
agents** [2026-06-24-sequoia-ascent-2026-summary].

## Why human judgment stays essential

Agents are spiky ([[concepts/jagged-intelligence]]). Karpathy's MenuGen payment bug —
the agent matched Stripe purchases to Google logins by **email address** instead of using
a **persistent user ID** — is "plausible code, but bad system design"
[2026-06-24-sequoia-ascent-2026-summary]. The frontier skill is **not** memorizing API
details (agents recall whether a tensor lib uses `dim`/`axis`/`keepdim`/`reshape`/
`permute`); the human must understand the underlying concepts — storage, views, memory
copies, invariants, identity, security boundaries, system shape
[2026-06-24-sequoia-ascent-2026-summary]. This is why
[[concepts/outsourcing-thinking-vs-understanding|understanding stays the bottleneck]].

## Tooling

Mechanisms that support the discipline include
[[concepts/git-worktrees]] (isolate parallel edits so one session/subagent never
corrupts another) and subagents/agent teams (coordinate the work itself)
[2026-06-24-run-parallel-sessions-with-worktrees-claude-code-docs]. Tools like
[[entities/claude-code]], [[entities/codex]], and [[entities/cursor]] are the current
environment; you invest in your setup as engineers always did with Vim or VS Code
[2026-06-24-sequoia-ascent-2026-summary].

## Implications

- **Hiring should change:** replace coding puzzles with "build a substantial project with
  agents, deploy it, secure it, then have adversarial agents try to break it"
  [2026-06-24-sequoia-ascent-2026-summary].
- **The 10x engineer becomes more extreme:** people who master agentic workflows may
  outperform others "by far more than 10x" — using agents as leverage rather than
  producing slop ([[concepts/ai-slop]]) [2026-06-24-sequoia-ascent-2026-summary].
