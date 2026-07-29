---
type: recap
title: "Recap — The Future of the Con Is Already Here, It's Just Not Evenly Distributed"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d]
tags: [ai-safety, scams, social-engineering, security, essay]
---

# Recap — The Future of the Con Is Already Here, It's Just Not Evenly Distributed

An essay by Manish Goregaokar arguing that LLMs collapse the historical gap between
cheap "spray-and-pray" scams and expensive, human-intensive targeted cons
[2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d]. The piece
opens with an extended fictionalized worked example — a fake job-recruiting/NDA-signing
flow used to hijack a victim's SSO login, monitor their accounts undetected, and
eventually drain a brokerage account — that the author states was "orchestrated and
carried out by an LLM" [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].

The author's core argument, building on a quote from James Mickens about adversary
capability being historically bimodal ("Mossad or not-Mossad"), is that **[[concepts/ai-enabled-scams]]**
now fill the previously-empty middle of that distribution: cheap enough to run at scale
(a cited 2024 paper found LLM spearphishing costs ~4¢/email) yet sophisticated enough to
sustain a multi-month, individually-tailored operation
[2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d]. Scale is
claimed to unlock new attacker capabilities specifically: patience (operations can lie
dormant for months), composition (chaining smaller scams, e.g. recruiting money mules),
and new target classes (a thousand compromised accounts becomes an asset in itself, able
to overwhelm platform "seams" that were tolerated at low fraud volume)
[2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].

The author argues traditional personal heuristics for spotting scams (fluent writing =
real person, a strong web presence takes real effort, family voices on a call are
trustworthy) are proxies for cost and capability that LLMs now break, and recommends
concrete countermeasures: pre-arranged spoken passwords with family, verifying "sent"
rather than "received" channels, and hardware 2FA over SMS/authenticator apps
[2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d]. The essay
draws an analogy to the "don't trust Wikipedia" advice given to students, framing it as a
correction in the wrong direction — the response should be building new heuristics for a
changed world, not clinging to old ones [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].

## Key claims

- An extended fictionalized example illustrates an LLM-orchestrated scam: fake recruiter,
  fake NDA-signing site with a credential-harvesting SSO flow, then patient monitoring and
  fund exfiltration from a victim's accounts
  [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- Adversary capability was historically bimodal (cheap/untargeted vs. expensive/targeted);
  the author argues LLMs now fill the middle, making targeted scams cheap enough to run at
  scale [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- Cites a 2024 paper finding LLM-generated spearphishing costs around 4¢ per email
  [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- Scaling unlocks patience, composition (chained smaller scams), and new targets (masses
  of compromised authenticated accounts as an asset class)
  [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- LLM capabilities cited as scam-relevant today: mark research, tailored/adaptive
  communication, voice cloning, real-time video deepfaking, fake web-presence generation,
  and spam-filter evasion [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- Recommended countermeasures: pre-arranged spoken family passwords, verifying via
  channels you initiate rather than ones you receive, and hardware 2FA (FIDO2/WebAuthn)
  over SMS or authenticator-app 2FA [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].
- Notes a real (non-LLM) precedent for coordinated exploitation of tolerated system
  "seams": a viral 2024 TikTok check-fraud trend that led Chase to file lawsuits
  [2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d].

## Entities mentioned

- [[entities/manish-goregaokar]]

## Concepts mentioned

- [[concepts/ai-enabled-scams]], [[concepts/social-engineering]]

## Source

`sources/2026-06-29-the-future-of-the-con-is-already-here-it-s-just-not-evenly-d.md`
