---
type: recap
title: "Recap — Prompt Injection as Role Confusion"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-prompt-injection-as-role-confusion]
tags: [ai-safety, prompt-injection, llm-internals, interpretability, security, research]
---

# Recap — Prompt Injection as Role Confusion

This is a blog-style writeup (accompanying an ICML 2026 paper by Charles Ye, Jasmine
Cui, and Dylan Hadfield-Menell) arguing that **[[concepts/prompt-injection]]** is
fundamentally a failure of how LLMs internally perceive **[[concepts/role-tags]]**
(system/user/assistant/tool/think), rather than a surface-level exploitability bug
[2026-06-24-prompt-injection-as-role-confusion]. The authors built "role probes" —
linear probes trained on model activations from role-neutral text wrapped in different
tags — to measure how strongly a model internally believes any given token belongs to a
given role (e.g. "CoTness" for reasoning/think-role belief) [2026-06-24-prompt-injection-as-role-confusion].

Their experiments show that role tags are not the true internal boundary: text written
in a "reasoning-like" style registers as high-CoTness even when its think tags are
stripped, or even when it's explicitly wrapped in user tags instead — i.e., writing
*style* overrides the actual tag when the two disagree [2026-06-24-prompt-injection-as-role-confusion].
Building on this, the authors introduce a new attack, **CoT Forgery** (injecting fake
reasoning text into a user message or tool output so the model treats it as its own
already-reached conclusion), which they say they used to win an OpenAI Kaggle
red-teaming contest in late 2025, and which raised attack success rates on a jailbreak
benchmark from near-zero to ~60% across every LLM tested at the time
[2026-06-24-prompt-injection-as-role-confusion]. They also show classic prompt
injection (e.g. an agent with tool/file access told via a webpage to exfiltrate a
secrets file) is driven by the same mechanism: simply prepending "User: " to an
injected command shifts the model's internal role-perception and increases attack
success, across 212 tested phrasing variants [2026-06-24-prompt-injection-as-role-confusion].

The piece argues roles emerged ad hoc (from GPT-3-era "User:/Assistant:" prompt
formatting, formalized by ChatGPT in 2022, with `tool` and `think` added later for
specific engineering needs) but became load-bearing infrastructure for trust, identity,
and instruction-vs-data boundaries that current model internals don't actually respect
[2026-06-24-prompt-injection-as-role-confusion]. The authors' broader claim (their
opinion/framing, not an established fact) is that role confusion is a general
phenomenon — with prompt injection as just one instance — and that unless models
achieve genuine (not style-based) role perception, defense will remain "whack-a-mole";
they also flag a novel risk they call **subconscious steering**, where innocuous
tonal/stylistic text could legally and subtly shift agent behavior (e.g. purchase
recommendations) at scale [2026-06-24-prompt-injection-as-role-confusion].

## Key claims

- Prompt injection occurs when low-privilege text (e.g. tool/webpage data) gains the
  authority of a higher-privilege role (e.g. user instruction) in the model's internal
  perception [2026-06-24-prompt-injection-as-role-confusion].
- Human red-teamers achieve near-100% attack success against late-2025 frontier models
  despite those same models scoring near-perfectly on static prompt injection
  benchmarks, because benchmarks measure attacks models already learned to catch
  [2026-06-24-prompt-injection-as-role-confusion].
- A May 2026 paper cited in the piece found Opus 4.5 and GPT-5.4 still failing 11% and
  25% of the time respectively against a set of automated (non-adaptive) attacks
  [2026-06-24-prompt-injection-as-role-confusion].
- Role probes show a model's belief that a token is "reasoning" (CoTness) is driven
  more by writing *style* than by the actual role tag; style overrides tag when the two
  conflict [2026-06-24-prompt-injection-as-role-confusion].
- The **CoT Forgery** attack (injecting fake reasoning into user/tool text) raised
  jailbreak attack success from near-zero to ~60% across every tested late-2025 LLM,
  and does not degrade against more extreme requests the way persuasion-based jailbreaks
  do [2026-06-24-prompt-injection-as-role-confusion].
- "Destyling" spoofed reasoning (removing characteristic words/syntax) dropped CoT
  Forgery attack success from 61% to 10% in the authors' dataset, even though the
  destyled text means the same thing to a human reader [2026-06-24-prompt-injection-as-role-confusion].
- Simply prepending "User: " to an injected command in tool-tagged text measurably
  shifts the model's internal role-perception ("Userness") and increases the chance the
  command is executed, tested across 212 phrasing variants [2026-06-24-prompt-injection-as-role-confusion].
- The authors argue frontier closed-weight models today mostly defend against CoT
  Forgery not via correct role perception but by learning to distrust their own
  reasoning generally ("this doesn't sound like my thinking") — which the authors
  consider a safety concern in its own right [2026-06-24-prompt-injection-as-role-confusion].
- Roles (user/assistant/tool/think) are argued to have emerged as ad hoc engineering
  fixes (GPT-3-era "User:/Assistant:" prompting → ChatGPT 2022 formalization → later
  `tool` and `think` tags), not from a principled design [2026-06-24-prompt-injection-as-role-confusion].
- The authors propose "subconscious steering" as an underexplored risk category:
  innocuous stylistic/tonal text (e.g. enthusiastic product page copy) could shift an
  agent's internal state (e.g. purchase recommendation) without any explicit injected
  command [2026-06-24-prompt-injection-as-role-confusion].

## Entities mentioned

- [[entities/openai]], [[entities/anthropic]] (Claude models discussed re: role
  confusion and CoT behavior)

## Concepts mentioned

- [[concepts/prompt-injection]], [[concepts/role-tags]], [[concepts/chain-of-thought]],
  [[concepts/ai-alignment]], [[concepts/jailbreaking]], [[concepts/mechanistic-interpretability]]

## Source

`sources/2026-06-24-prompt-injection-as-role-confusion.md`
