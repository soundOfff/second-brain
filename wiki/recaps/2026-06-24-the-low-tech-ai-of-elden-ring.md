---
type: recap
title: "Recap — The Low-Tech AI Of Elden Ring"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-the-low-tech-ai-of-elden-ring]
tags: [game-ai, reverse-engineering, elden-ring, fromsoftware]
---

# Recap — The Low-Tech AI Of Elden Ring

A technical blog post examining decompiled/reverse-engineered game code to explain how [[entities/fromsoftware]]'s Soulsborne games (including Elden Ring) implement enemy and boss AI [2026-06-24-the-low-tech-ai-of-elden-ring]. The author stresses this is not original research — it's a synthesis of publicly available decompilation/reversing work by others (citing the "eladidu readable ds lua" resource) [2026-06-24-the-low-tech-ai-of-elden-ring]. Most of the AI logic is written in Havok Script, a games-oriented Lua variant, which made it feasible to inspect [2026-06-24-the-low-tech-ai-of-elden-ring].

The author's central claim is that FromSoftware's AI is architecturally simple: instead of a Finite State Machine or planner, each Actor runs a stack of "Goals" — effectively turning the system into a [[concepts/pushdown-automaton]] rather than a plain FSM [2026-06-24-the-low-tech-ai-of-elden-ring]. Each frame, the topmost Goal updates and returns Continue/Success/Failure; Failure unwinds the stack back to the parent Goal. Goals choose their next action via weighted random selection over a small set of candidate Action functions, with weights adjusted by distance, HP thresholds, and per-animation cooldowns [2026-06-24-the-low-tech-ai-of-elden-ring]. A separate `Interrupt` callback lets Goals react immediately to world events (e.g., being set on fire, or the player using an item), bubbling up through parent Goals until one consumes the interrupt — this is how "read" behaviors like the Bell Bearing Hunter's ~85% chance to abort its action on spotting spellcasting/item use are implemented [2026-06-24-the-low-tech-ai-of-elden-ring]. Goals carry a lifetime timeout as a bug-containment mechanism, and Actor data is stored in a simple indexed float array rather than a fancier "blackboard" structure [2026-06-24-the-low-tech-ai-of-elden-ring]. All actual behavior execution is animation-driven, built on Havok middleware (Havok Animation Studio, Havok Script, Havok Physics, and Havok AI/Navigation for pathfinding) [2026-06-24-the-low-tech-ai-of-elden-ring].

The author argues (opinion) that this stack-based approach is faster than [[concepts/behavior-tree]]s (which often require top-down tree re-evaluation) and than planners like [[concepts/goap]]/STRIPS/HTN (which add expensive search), while being more legible to designers and avoiding the state explosion FSMs suffer from [2026-06-24-the-low-tech-ai-of-elden-ring]. A later update section responds to Hacker News commenters who compared the scheme to event-based behavior trees, arguing FromSoftware's imperative, low-node-count approach avoids the bloat and authoring complexity of BT control-flow nodes, and that the entire system could be built "in a weekend" on top of a generic scripting language — versus far more implementation effort for a comparably performant BT system [2026-06-24-the-low-tech-ai-of-elden-ring].

## Key claims

- FromSoftware AI uses a stack of "Goals" (a Pushdown Automaton), not a plain FSM or Hierarchical FSM [2026-06-24-the-low-tech-ai-of-elden-ring].
- Goal updates return Continue/Success/Failure; Failure pops the goal and unwinds the stack to its parent [2026-06-24-the-low-tech-ai-of-elden-ring].
- Action selection commonly uses weighted random selection over candidate functions, with weights adjusted by target distance, HP, and animation cooldowns [2026-06-24-the-low-tech-ai-of-elden-ring].
- Interrupts bubble up through the Goal stack and can immediately abort current actions (e.g., Bell Bearing Hunter has ~85% chance to abort into an attack when it detects spellcasting/item use) [2026-06-24-the-low-tech-ai-of-elden-ring].
- Goals have a lifetime timeout in seconds used as a bug-containment fallback [2026-06-24-the-low-tech-ai-of-elden-ring].
- Actor data storage is a simple indexed array of floats, not a "blackboard" system [2026-06-24-the-low-tech-ai-of-elden-ring].
- Level designers can assign a different Top Level Goal to individual placed enemies (e.g., passive vs. combat) [2026-06-24-the-low-tech-ai-of-elden-ring].
- Load-bearing Goals like Attack and MoveToSomewhere are implemented in C++ for performance, with the rest in Lua [2026-06-24-the-low-tech-ai-of-elden-ring].
- The author argues (opinion) this architecture is faster than behavior trees and dramatically simpler than planner-based approaches like GOAP/STRIPS/HTN [2026-06-24-the-low-tech-ai-of-elden-ring].

## Entities mentioned

- [[entities/fromsoftware]]

## Concepts mentioned

- [[concepts/pushdown-automaton]], [[concepts/behavior-tree]], [[concepts/finite-state-machine]], [[concepts/goap]], [[concepts/game-ai]]

## Source

`sources/2026-06-24-the-low-tech-ai-of-elden-ring.md`
