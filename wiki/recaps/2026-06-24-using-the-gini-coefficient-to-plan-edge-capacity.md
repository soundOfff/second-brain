---
type: recap
title: "Recap — Using the Gini Coefficient to Plan Edge Capacity"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]
tags: [engineering, capacity-planning, cdn, machine-learning]
---

# Recap — Using the Gini Coefficient to Plan Edge Capacity

A **[[entities/fastly]]** engineering blog post describing how the company built its
production capacity-planning model for edge POPs (points of presence) around the
**[[concepts/gini-coefficient]]**, an inequality metric borrowed from economics
[2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. The author reports trying
a wide range of standard AI/ML approaches first — AutoML, neural nets, tree models,
ensembles, regressions, time-series models, and even LLMs — which fit ordinary traffic
well but performed poorly on the rare, extreme-traffic events (major game releases,
live sporting events, provider failovers) that matter most for capacity planning
[2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. The winning model that
replaced them is deliberately small and interpretable, and has been in production for
over a year [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].

The core insight: traffic concentration (a few customers/workloads dominating a POP's
traffic during a big event) predicts cache-hit ratio, because caches benefit from
popularity, and popularity is itself a form of inequality
[2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. Fastly models predicted
front-end cache-hit ratio as `a * sqrt(gini) + b * top_N_ratio + c`, with the square
root chosen because cache behavior improves steeply at first concentration and then has
diminishing returns [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. That
predicted cache ratio then feeds a second robust-regression model that predicts per-POP
CPU utilization from bits/sec, requests/sec, and compute-task volume, forming a chain:
traffic mix → predicted cache ratio → predicted CPU → headroom
[2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. The author reports the
simple model stays within 5% of real CPU utilization, versus 25%+ deviation for more
sophisticated models [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. A
separate finding: for establishing a "normal" traffic baseline, plain seasonal-naive
forecasting (via `statsforecast`) outperformed more flexible approaches like
Prophet-style models [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity]. The
author's broader takeaway is that feature engineering — finding a feature that captures
real system behavior — mattered more than model sophistication
[2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].

## Key claims

- Fastly's production capacity model chain is: traffic inequality → cache behavior →
  CPU utilization → headroom [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- Standard ML/AI techniques (AutoML, neural nets, trees, ensembles, LLMs) fit average-case
  traffic well but failed on the rare high-impact events capacity planning cares about
  [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- Predicted cache-hit ratio formula: `a * sqrt(gini) + b * top_N_ratio + c`, fit via
  robust regression [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- The simple production model keeps CPU-utilization predictions within 5% of actual,
  versus 25%+ deviation for more complex models
  [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- Seasonal-naive forecasting outperformed more flexible time-series models (e.g.
  Prophet-style) for picking a "normal" traffic baseline
  [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- The model has been in production at Fastly for more than a year, used for event
  planning and POP builds worldwide
  [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].
- The insight also led Fastly to deliberately concentrate compatible workloads on some
  hardware to improve cache locality and efficiency, rather than always spreading traffic
  evenly [2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity].

## Entities mentioned

- [[entities/fastly]]

## Concepts mentioned

- [[concepts/gini-coefficient]], [[concepts/edge-capacity-planning]]

## Source

`sources/2026-06-24-using-the-gini-coefficient-to-plan-edge-capacity.md`
