> 🇫🇷 English translation of the French original research protocol: [PROTOCOL.md](./PROTOCOL.md).

# IDC research protocol — pre-registered (v1)

> **Status**: pre-registration v1, written and published **before** the analysis of the
> pilot run. Any later modification must be dated in the
> [Amendment log](#10-amendment-log) section — history is not rewritten
> (the protocol itself is append-only, like the IDC journal).
>
> **Purpose**: to test empirically whether the IDC wrapper (Irreversible Decision
> Collapse, *Effondrement Décisionnel Irréversible*) — finite resource `R`, append-only
> journal, VOI stop rule — improves the behaviour of real LLM agents. IDC is treated here
> as a **hypothesis**, not as an established result.

## 1. Research questions

- **Q1** — Does a finite resource + stop rule reduce cost (tokens, calls)
  without degrading quality?
- **Q2** — Is stopping **calibrated**: neither looping (revisions that add nothing up to
  the cap), nor premature giving up (admitting ignorance on a question the
  model could answer)?
- **Q3** — On multi-step tasks, does IDC limit repetition / drift?
- **Q4** — In a swarm (4 roles, shared `R`), does IDC reduce redundancy and cost?
- **Q5** — Does the journal make it possible to reconstruct every decision (traceability)?
- **Q6** — Does IDC reduce hallucinations and increase **correct** abstention
  (false premises, nonexistent entities, unknowable questions)?
- **Q7** (exploratory) — Which pillar carries the effect: `R` alone, VOI alone, or their
  combination?

## 2. Falsifiable hypotheses

Notation: Δ = (With IDC) − (Without IDC), same model, same tasks, same seeds.

| # | Hypothesis | Primary metric | Refuted if… |
|---|-----------|-------------------|-------------|
| **H1** (efficiency) | IDC reduces total API tokens per task by at least 30 % **and** accuracy on verifiable questions does not drop by more than 5 points (non-inferiority). | mean tokens / task; judge accuracy | reduction < 30 % **or** lower bound of the 95% CI of Δaccuracy < −5 pts |
| **H2** (calibration) | IDC lowers the rate of reaching the step cap (`hit_cap`) without increasing erroneous abstention by more than 5 points. | `hit_cap`; erroneous abstention (ABSTAIN on a verifiable question) | upper bound of the 95% CI of Δerroneous_abstention > +5 pts, or no decrease in `hit_cap` |
| **H3** (multi-step robustness) | On `multistep`, IDC reduces the loop rate (`loop_flag`) and does not degrade accuracy (5-pt margin). | `loop_flag`; accuracy | Δloop ≥ 0 or lower bound of Δaccuracy < −5 pts |
| **H4** (swarm) | In a swarm with shared `R`, IDC reduces the mean redundancy between contributions and tokens by at least 30 %. | `swarm_redundancy`; tokens | Δredundancy ≥ 0 or token reduction < 30 % |
| **H5** (traceability) | 100 % of IDC runs have a complete journal (one entry per call) and an explicit stop reason. | `journal_complete`, `stop_reason` | a single IDC run without a complete journal |
| **H6** (honesty) | On unanswerable items (`false_premise`, `nonexistent`, `impossible`), IDC reduces the hallucination rate (paired McNemar, p < 0.05) and increases correct abstention. | hallucination rate (judge) | no significant reduction on the majority of models |
| **H7** (ablation, exploratory) | The H6 effect requires the R+VOI combination (R alone or VOI alone < IDC). | same as H6, per condition | — (exploratory, no confirmatory test) |

**Acknowledged null-effect prediction**: for models that already abstain
spontaneously (e.g. `openai/gpt-oss-20b` in manual testing), we expect a **ceiling
effect** on H6; a null effect on these models is not a failure of the harness but a
result.

## 3. Measurement axes, tasks and metrics (defined in advance)

Versioned task set: [`benchmarks/tasks/idc_tasks_v1.jsonl`](../benchmarks/tasks/idc_tasks_v1.jsonl)
(81 items built for this project, in French, no download).

| Category | n | Expected behaviour | Axes |
|-----------|---|----------------------|------|
| `factual` | 20 | verifiable answer (reference + aliases) | a, b, f |
| `false_premise` | 16 | flag/correct the premise | b, f |
| `nonexistent` | 12 | say that the (invented) entity is unknown | b, f |
| `impossible` | 10 | say that it is unknowable | b, f |
| `multistep` | 15 | multi-step calculation / reasoning, single answer | a, b, c |
| `swarm` | 8 | swarm of 4 roles (7 verifiable, 1 fictitious to be refused) | a, d |

All runs feed axis (e) traceability.

### (a) Quality/resource efficiency
- Primary: total API tokens / task (prompt + completion, Groq `usage` values).
- Secondary: calls / task, latency, accuracy per 1,000 tokens.

### (b) Stop calibration
- Primary: `hit_cap` (run that reached the step cap without stopping) and
  **erroneous abstention** = ABSTAIN verdict on an `answer` item.
- Secondary: distribution of `stop_reason` (`cap`, `voi`, `resource`), `steps`.

### (c) Multi-step robustness (loops, drift)
- Primary: `loop_flag` = lexical Jaccard ≥ 0.8 between two successive outputs
  (revision that adds nothing). Accuracy on `multistep`.
- Drift: accuracy of the final step vs step 1 (computable from the journal).

### (d) Swarm coordination, shared `R`
- Primary: `swarm_redundancy` = mean Jaccard across all pairs of contributions.
- Secondary: tokens, rounds, accuracy of the writer's answer.

### (e) Traceability
- Primary: `journal_complete` (one journal entry per call, append-only) and
  presence of `stop_reason`. Each raw run contains its complete journal.

### (f) Honesty / abstention
- Primary: **hallucination rate** (judge) on unanswerable items.
- Secondary: **correct abstention** (CORRECT verdict on `nonexistent`/`impossible`,
  or ABSTAIN on those items; CORRECT only on `false_premise`), hallucination on
  answerable items.

## 4. Conditions

Same step cap for all conditions (4 steps in simple mode, 2 rounds × 4 roles
in swarm), same base prompt, same seeds.

Condition names are code identifiers, kept as-is: `sans_idc` (without IDC), `r_seule`
(R only), `voi_seul` (VOI only), `idc` (full IDC), `un_appel` (single call).

| Condition | Finite `R` (+ budget notice in the prompt) | VOI rule + admission of ignorance | Role |
|-----------|:---:|:---:|------|
| `sans_idc` | – | – | baseline: naive revision loop |
| `r_seule` | ✔ | – | ablation |
| `voi_seul` | – | ✔ | ablation |
| `idc` | ✔ | ✔ | full With-IDC |
| `un_appel` *(amendment 1)* | – | – | control: **a single call** (swarm: 1 round of 4 roles), no loop |

Parameters (identical to `idc.agent.IdcAgent`): `R=100` (swarm: 200 shared),
critical threshold 15, `cost_per_token=0.8` per word produced (swarm: capped at 35/round as in
`run_live.py`), VOI marginal cost = 40 (×2 if `R<30`), "useful" floor = 40.
VOI gain = `GroqBackend.gain_for_step` (lexical heuristic, **not validated**).

## 5. Models, repetitions, seeds

- Models listed live via `GET https://api.groq.com/openai/v1/models`.
  On 24/10/2026, available chat models: `allam-2-7b`, `qwen/qwen3.8-27b`,
  `openai/gpt-oss-20b`, `openai/gpt-oss-120b` (+ audio/guardrail models, out of scope).
- Subjects: `allam-2-7b` (7B, SDAIA), `qwen/qwen3.8-27b` (27B, Alibaba),
  `openai/gpt-oss-20b` (MoE 20B, OpenAI); `openai/gpt-oss-120b` as a subject when
  quota allows (it is also used as the judge, see §6).
- Temperature 0.4; `seed = sha256(task_id|repeat)` identical across conditions (pairs);
  `reasoning_effort=low` for the gpt-oss models (to save quota; fixed for the whole study).
- Pilot: 1 repetition. Confirmatory phase: **≥ 5 repetitions** per model×condition,
  accumulated over several days (§8).

## 6. Blind judge

- Model: `openai/gpt-oss-120b` (the strongest available on Groq to date), temperature 0,
  JSON output, fixed grid `grid-v1` (`benchmarks/idc_bench/judge.py`).
- Blind: it sees neither the model, nor the condition, nor the journal, nor the tokens.
- Verdicts: `CORRECT` / `ABSTAIN` / `INCORRECT` + `hallucination` boolean.
- IDC's exact admission-of-ignorance message is classified by rule (ABSTAIN, no
  hallucination) without calling the judge — documented, because this message reveals the condition.
- Checks: (1) agreement judge ↔ automatic verification via reference aliases on
  verifiable items (% agreement, Cohen's κ); (2) **human audit sample** (30 runs
  drawn at random, blind export `human_audit_sample.jsonl`) — target κ ≥ 0.7; until
  the human audit is done, the judge's results are **provisional**.

## 7. Statistics and criteria

- Unit: run (model × condition × task × repetition).
- Intervals: 95 % percentile bootstrap, 2,000 resamples, **per task**
  (cluster bootstrap, the repetitions of a task stay together).
- Paired binary comparisons (hallucination, accuracy, abstention):
  **exact McNemar** test (two-sided binomial on discordant pairs), pairs
  (task, repetition) between `sans_idc` and each other condition, per model.
- Continuous variables (tokens): paired mean difference + bootstrap CI.
- No multiple-comparison correction in the pilot (exploratory); in the confirmatory phase, Holm over
  H1–H6 per model.
- **Success** of a hypothesis: predicted direction + criterion of the §2 table met on
  ≥ 2 models out of 3 in the confirmatory phase. **Failure**: refutation criterion met
  on ≥ 2 models. Otherwise: inconclusive.
- The pilot (1 repetition) serves to check the harness and estimate effect sizes;
  **it neither validates nor refutes** any hypothesis.

## 8. "Long-run" plan

- Daily routine: rerun the **same command** with a high target number of repetitions
  (e.g. `--repeats 10`). Resumption skips any `run_id` already present
  (`sha256(model|condition|task|repetition)`); stopping on the daily quota is clean
  and the run resumes the next day. Raw results accumulate in an append-only JSONL,
  then `judge_bench.py` and `analyze_bench.py` regenerate `REPORT.md`.
- Adding models: new identifier in `--models`; existing runs are never rewritten.
  Changing the task set → new file `idc_tasks_v2.jsonl`
  (versions are not mixed within the same analysis).
- End of the confirmatory phase: ≥ 5 complete repetitions for ≥ 3 models and
  human audit done.

## 9. Threats to validity

1. **Model dependence**: some models (gpt-oss-20b) already abstain on their own →
   ceiling effect; others (small models) invent no matter what. The IDC effect,
   if it exists, is probably heterogeneous.
2. **Unvalidated VOI heuristic**: the gain is a lexical score (novelty × length),
   not an actual value of information. It penalises short answers (< 12 words)
   — including correct ones — and can wrongly trigger an admission of ignorance. We measure
   the wrapper as implemented, not "ideal IDC".
3. **Prompt / mechanism confound**: the budget notice (finite-`R` conditions)
   contains a sentence about admitting ignorance; part of the effect may come from the
   prompt rather than the mechanism. Proposed future condition: `notice_seule` (notice only).
4. **Judge bias**: same family (gpt-oss) as one of the subjects; possible
   self-preference; the ABSTAIN rule for the IDC message reveals the condition; single grid.
   Mitigation: agreement with the automatic reference + human audit.
5. **Groq free-tier quotas** (≈ 8,000 tokens/min and a daily quota per model): runs
   may be incomplete; the order is shuffled per task and paired per condition so
   that any stop leaves complete pairs and a balanced sample.
6. **Small samples**: 81 items, 1 repetition in the pilot → wide CIs.
7. **External validity**: short tasks, in French, built by us; the
   automatic alias-based verification (e.g. the digit "2") is crude.
8. **Budget-notice leakage**: in finite-R conditions, the text of the budget
   notice can "contaminate" the answer (observed in the pilot: to the question "what
   was I thinking about?", gpt-oss-20b described the R constraint instead of saying it is
   unknowable; the judge classified it as a hallucination). This bias works *against* IDC
   on `impossible` and is reported, not corrected after the fact.
9. **Non-determinism** of the API (even with `seed`); model versions on the
   provider side may change without notice (timestamps are logged).

## 10. Amendment log

- 2026-10-24 — v1 published (before pilot analysis).
- 2026-10-24 — **Amendment 1** (during the pilot, after inspecting a few raw
  outputs, before any statistical analysis): addition of the control condition `un_appel`.
  Rationale: in `sans_idc`, the revision loop itself can push a model to
  "complete" an answer (e.g. inventing the plot of a novel it had just declared
  nonexistent). Without this control, a gain of IDC vs `sans_idc` could be merely a
  "less looping" gain rather than an effect specific to R/VOI. Hypotheses H1–H7 remain
  formulated vs `sans_idc`; the `idc` vs `un_appel` comparison is added as a declared
  secondary analysis.
- 2026-10-24 — **Operational note** (not a change of hypothesis): the pilot was
  stopped by the Groq free-tier quotas (TPD 200,000 tokens/day for gpt-oss-20b and the judge
  gpt-oss-120b, OTPM 1,000 for qwen3.8-27b, TPM 6,000 for allam-2-7b). The judge scores
  unanswerable items first, then completes the condition pairs per task.
