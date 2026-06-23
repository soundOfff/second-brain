# Operations Log

Append-only. Every skill run records one entry. Newest at the bottom.

Format:

```
## YYYY-MM-DD HH:MM — /command [arg]
- sources: <ids added/processed>
- recaps: <recaps created/updated>
- wiki: <entity/concept pages created/updated>
- index: <updated? what>
- notes: <decisions, contradictions found, follow-ups>
```

---

## 2026-06-23 — system initialized
- Created three-layer structure: `sources/`, `wiki/{entities,concepts,recaps,digests}/`.
- Authored `CLAUDE.md` schema, `index.md` map of content, this log.
- Installed skills: `/capture`, `/sync`, `/lint`, `/digest`.
- notes: Empty brain, ready for first `/capture`.

## 2026-06-23 — /capture https://www.askglitch.com/blog/build-a-second-brain
- sources: 2026-06-23-karpathy-llm-wiki (article)
- recaps: recaps/2026-06-23-karpathy-llm-wiki
- wiki: created concepts/{llm-wiki, second-brain, retrieval-augmented-generation};
  created entities/{andrej-karpathy, claude-code, obsidian}
- index: added top entities, top concepts, recently-updated entry
- notes: Self-referential seed — the brain's first source is the article describing the
  brain. RAG, Karpathy, Claude Code, Obsidian left as stubs pending more sources. No
  contradictions. 1 source → 7 wiki pages (recap + 6).

## 2026-06-23 — infra: /remember skill + launchd scheduler
- skills: created `/remember` (.claude/skills/remember/SKILL.md) — distils the current
  conversation into a `type: note` source, then runs the `/capture` ripple. Save+ripple
  behavior chosen by the user.
- scheduler: added launchd LaunchAgents (bin/launchd/com.secondbrain.{sync,digest}.plist)
  — sync nightly 02:00, digest Mondays 09:00 — plus bin/brain-schedule.sh
  (install/uninstall/status/run) which symlinks the repo plists into ~/Library/LaunchAgents.
- gitignore: added `.brain/` (headless run logs).
- docs: updated CLAUDE.md (skills table → 5 skills + Scheduling section), README.md
  (operations table + scheduling section), index.md (how-to).
- notes: plists + script lint clean (plutil, zsh -n). The actual `launchctl` load was
  NOT performed — the auto-approval classifier blocked loading agents that run
  `claude -p --permission-mode bypassPermissions`. User must run
  `bin/brain-schedule.sh install` themselves to activate the schedule.
