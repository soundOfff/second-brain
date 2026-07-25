---
type: recap
title: "Recap — Unlimited-OCR: One-shot Long-horizon OCR"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr]
tags: [ocr, document-parsing, open-source, model-release, computer-vision]
---

# Recap — Unlimited-OCR: One-shot Long-horizon OCR

GitHub README/release page for **[[entities/unlimited-ocr]]**, an OCR model released by
**[[entities/baidu]]** and pitched as pushing **[[entities/deepseek-ocr]]** "one step further,"
aiming at what the project calls the "era of one-shot long-horizon parsing" — i.e. document
parsing/[[concepts/optical-character-recognition]] over long, multi-page inputs in a single pass
[2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr]. The page is primarily inference
documentation (Hugging Face Transformers and SGLang code paths) rather than a paper; the
accompanying arXiv paper (id 2606.23050) is only linked, not summarized on this page
[2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].

The repo supports two single-image inference configs — "gundam" (base_size 1024, image_size 640,
crop_mode enabled) and "base" (image_size 1024, crop_mode disabled) — while multi-page and PDF
inputs are restricted to the "base" config; PDFs are handled by converting pages to images via
PyMuPDF before multi-page inference [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr]. Besides
the Hugging Face Transformers path, the project ships an [[entities/sglang]]-based server with an
OpenAI-compatible streaming chat-completions API and a custom no-repeat-n-gram logit processor,
plus a batch-inference script (`infer.py`) that can process an image directory or PDF with
configurable concurrency [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr]. The model is also
distributed via [[entities/huggingface]] Spaces (demo credited to community member "AK") and
[[entities/modelscope]] [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr]. The README credits
[[entities/deepseek-ocr]], "Deepseek-OCR-2," and [[entities/paddleocr]] as prior work the project
builds on, and is released under the MIT license [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
At capture time the repo showed 6.2k stars and 473 forks [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].

## Key claims

- Unlimited-OCR is positioned as an improvement over Deepseek-OCR for one-shot, long-horizon
  document parsing [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
- The associated paper is on arXiv as id 2606.23050, authored by a Baidu-affiliated team
  (Youyang Yin et al.) [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
- Single-image inference offers two configs, "gundam" (crop_mode on, image_size 640) and "base"
  (crop_mode off, image_size 1024); multi-page/PDF inference only supports "base"
  [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
- The project provides both a Hugging Face Transformers inference path and an SGLang server with
  an OpenAI-compatible streaming API [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
- The model is distributed on Hugging Face Spaces (demo) and ModelScope, in addition to the GitHub
  repo, and is MIT-licensed [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].
- The README explicitly acknowledges Deepseek-OCR, Deepseek-OCR-2, and PaddleOCR as prior
  models/ideas it draws on [2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr].

## Entities mentioned

- [[entities/unlimited-ocr]], [[entities/baidu]], [[entities/deepseek-ocr]],
  [[entities/paddleocr]], [[entities/huggingface]], [[entities/modelscope]], [[entities/sglang]]

## Concepts mentioned

- [[concepts/optical-character-recognition]], [[concepts/document-parsing]]

## Source

`sources/2026-06-24-unlimited-ocr-one-shot-long-horizon-ocr.md`
