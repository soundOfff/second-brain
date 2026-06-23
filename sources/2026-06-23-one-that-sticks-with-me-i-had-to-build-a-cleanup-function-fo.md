---
id: 2026-06-23-one-that-sticks-with-me-i-had-to-build-a-cleanup-function-fo
title: "One that sticks with me: I had to build a cleanup function for text in"
type: note
captured: 2026-06-23
---

One that sticks with me: I had to build a cleanup function for text inputs to improve note writing quality, and I integrated the Groq API using a single model. I was confident in the implementation and didn't think through edge cases. Then one night I woke up to a flood of Sentry alerts on my phone — the model was down, and I had no fallback strategy in place. Users were affected. I fixed it inmediately adding a second model as fallback and the next morning by migrating to OpenRouter, which gives me model redundancy

