---
type: recap
title: "Recap — EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL"
created: 2026-07-25
updated: 2026-07-25
status: stable
sources: [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo]
tags: [paper, text-to-sql, reinforcement-learning, llm]
---

# Recap — EXPO-SQL: Execution-based Clause-level Policy Optimization for Text-to-SQL

An arXiv paper (Jaehoon Lee, CheolWon Na, Suyoung Bae, Jin-Seop Lee, Jihyung Lee, YunSeok Choi, Jee-Hyong Lee; ACL 2026 Findings) addressing a weakness in reinforcement-learning approaches to **[[concepts/text-to-sql]]** [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo]. The authors note that existing RL methods for training LLMs to generate SQL from natural language assign a single, uniform reward to the whole query, treating every clause as equally correct or incorrect — which they argue produces an insufficiently fine-grained learning signal [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].

Their proposed method, EXPO-SQL, instead assigns **clause-level rewards**: it identifies which specific clauses are erroneous by analyzing execution results (error messages and incremental, clause-by-clause execution), giving the model targeted supervision rather than one query-wide signal [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo]. On widely-used text-to-SQL benchmarks, the authors report EXPO-SQL significantly outperforms existing supervised fine-tuning, prompting, and RL-based baselines [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo]. Code is released on GitHub (jhn25/EXPO-SQL) [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].

## Key claims

- Existing RL methods for text-to-SQL apply a single query-level reward, giving equal weight/signal to correct and incorrect clauses within the same query [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].
- EXPO-SQL introduces clause-level rewards derived from execution feedback (error messages plus clause-wise incremental execution) to pinpoint erroneous clauses [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].
- The authors report EXPO-SQL significantly outperforms supervised fine-tuning, prompting, and prior RL-based text-to-SQL methods on standard benchmarks [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].
- Accepted to ACL 2026 Findings; code available at github.com/jhn25/EXPO-SQL [2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo].

## Entities mentioned

- (none beyond the paper's authors)

## Concepts mentioned

- [[concepts/text-to-sql]], [[concepts/reinforcement-learning]], [[concepts/reward-shaping]]

## Source

`sources/2026-06-24-expo-sql-execution-based-clause-level-policy-optimization-fo.md`
