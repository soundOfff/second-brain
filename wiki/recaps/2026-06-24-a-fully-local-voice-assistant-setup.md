---
type: recap
title: "Recap — A fully local voice assistant setup"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-a-fully-local-voice-assistant-setup]
tags: [voice-assistant, local-llms, home-automation, speech, platypush]
---

# Recap — A fully local voice assistant setup

A tutorial-style blog post by **Fabio Manganiello**, creator of
[[entities/platypush]], walking through a fully local, self-hosted voice-assistant
stack for 2026 [2026-06-24-a-fully-local-voice-assistant-setup]. Manganiello frames it
against his own history of DIY voice assistants going back to 2007 (Hidden Markov
models), through 2019–2024 iterations built on now-deprecated or discontinued
components (Google Assistant Library, Snowboy, Mozilla DeepSpeech, Mycroft/mimic3),
arguing that by 2026 both hardware and open local models are finally mature enough for
a fully on-device stack [2026-06-24-a-fully-local-voice-assistant-setup].

The recommended pipeline is [[entities/openwakeword]] for local wake-word detection,
[[entities/vosk]] for local [[concepts/speech-to-text]] transcription,
[[entities/piper]] for local [[concepts/text-to-speech]], and
[[entities/openai]]'s API used only where a language model genuinely adds value
(turning messy speech into structured intent, or answering open-ended questions)
[2026-06-24-a-fully-local-voice-assistant-setup]. Deterministic regex-based command
hooks handle common requests (lights, music) directly without touching a model, while
the LLM step is reserved as a fallback/interpretation layer — validated against an
explicit allow-list of actions before anything is executed, since "a model may be
useful for interpretation, but it should not get arbitrary access to run()"
[2026-06-24-a-fully-local-voice-assistant-setup]. To remove the last cloud dependency,
the post shows pointing the OpenAI-compatible API call at a local server (e.g.
[[entities/ollama]] serving Llama 3.1 8B), while cautioning that on a Raspberry Pi the
local LLM step will be noticeably slower than a cloud or GPU-backed model
[2026-06-24-a-fully-local-voice-assistant-setup].

The author's broader argument (opinion) is architectural: voice assistants have
historically been "a graveyard of abandoned SDKs and cloud products" (Snowboy, Mycroft,
Google Assistant SDK), so the safer long-term bet is a pipeline of small, independently
replaceable parts connected by an event system, rather than one monolithic vendor
assistant [2026-06-24-a-fully-local-voice-assistant-setup].

## Key claims

- Recommended fully-local pipeline: assistant.openwakeword (hotword) → assistant.vosk (STT) → deterministic Platypush event hooks or openai.get_response (fallback) → tts.piper (TTS) [2026-06-24-a-fully-local-voice-assistant-setup].
- Vosk model tradeoffs: vosk-model-small-en-us-0.15 (40MB, fast/low-accuracy, runs on old Pi) vs. vosk-model-en-us-0.22-lgraph (128MB, reasonably accurate, still Pi-friendly) vs. vosk-model-en-us-0.22 (1.8GB, most accurate, heavier on Pi) [2026-06-24-a-fully-local-voice-assistant-setup].
- The LLM is deliberately scoped as a fallback: common commands are handled by fast, inspectable, non-hallucinating regex hooks; the model is invoked only for messy/general requests [2026-06-24-a-fully-local-voice-assistant-setup].
- LLM-proposed actions must be validated against an explicit allow-list before execution — the model should not get arbitrary access to run arbitrary actions (author's stated design principle) [2026-06-24-a-fully-local-voice-assistant-setup].
- The pipeline can be made fully local end-to-end by pointing the OpenAI-compatible plugin at a local server such as Ollama, llama.cpp server, vLLM, or LocalAI [2026-06-24-a-fully-local-voice-assistant-setup].
- Author's opinion: a modular, swappable-parts architecture ages better than monolithic vendor assistants, citing the deaths of Snowboy, Mycroft/mimic3, and the deprecated Google Assistant SDK [2026-06-24-a-fully-local-voice-assistant-setup].

## Entities mentioned

- [[entities/fabio-manganiello]], [[entities/platypush]], [[entities/vosk]], [[entities/piper]], [[entities/openwakeword]], [[entities/openai]], [[entities/ollama]]

## Concepts mentioned

- [[concepts/local-llms]], [[concepts/llm-fallback-strategy]], [[concepts/speech-to-text]], [[concepts/text-to-speech]], [[concepts/hotword-detection]], [[concepts/home-automation]]

## Source

`sources/2026-06-24-a-fully-local-voice-assistant-setup.md`
