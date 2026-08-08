# Record-Auditability Fixes — Iteration Plan (pd-facing)

> Status: **Iteration plan** for the fix set A/B/C/E of [record-auditability-fix-plan.md](record-auditability-fix-plan.md) (csr-converged + psv-verified: 69/1/4/0 of 74). Consumed by `parallel-development` (plan-driven mode). Fix D (fedaot-kb doc repointing) is external — executed by fedaot-kb's own process, NOT this plan.
> Authority chain: `docs/record-auditability-fix-plan.md` (master) > csr SKILL.md + psv SKILL.md (the skills being modified) > this plan. On conflict, the fix-plan wins.

## Complexity tiers

- S — single-file edit, no logic change: `pyproject.toml` (C1), SKILL.md wording (A3).
- M — schema + logic + fixtures in one skill: A1/A2/A4, B1/B2/B3.
- L — cross-file, cross-skill change with test suite updates: A5 (ADR log + doc-audit), E1 (full self-gate sweep).

## Dependency edges

```
A1 (schema: round gains findings+dispositions) ──► A2 (converge.py pass-through + run.json shape)
A1 ──► A3 (SKILL.md step-2/step-4 wording)
A1 + A2 ──► A4 (test fixtures)
A1 + A2 + A3 ──► A5 (ADRs + doc-audit)
B1 (psv SKILL.md emit + extractor guidance) ──► B3 (psv test fixtures)
B2 (coverage-record.schema.json registry) ──► B3
C1 (pyproject.toml jsonschema) — independent
E1 (full self-gate sweep) ──► ALL (A1-A5, B1-B3, C1)
```

## DAG

Wave-form (matches the dependency edges and the plan-model `depends_on` arrays exactly):

- wave 1 (parallel): A1, B1, B2, C1 — no dependencies
- wave 2: A2 (← A1), A3 (← A1), B3 (← B1 + B2)
- wave 3: A4 (← A1 + A2)
- wave 4: A5 (← A1 + A2 + A3)
- wave 5: E1 (← A1–A5, B1–B3, C1)

C1 is independent throughout; E1 is the sink of every item.

## Per-iteration DoD

| Item | DoD (all must pass) |
| --- | --- |
| A1 | `convergence-record.schema.json` round `$defs` carries required `findings` (array of doc-findings `$defs/finding`) + required `dispositions` (array of `{defect_id, action: fixed/rejected/escalated, note}` — one disposition per finding in the round's findings array, rationale (`note`) required); schema validates via `convergence_policy_check.py` |
| A2 | `converge.py` passes through per-round findings + dispositions from run.json into the emitted record; `jsonschema` validation covers both; old counts-only fixture records updated |
| A3 | SKILL.md step 2: "record accept/reject/escalate + rationale per defect_id at reconcile time" (escalate target = human, stated explicitly); step 4: "per-round findings + dispositions" replaces "findings trend"; schema-version note (record shape changed: findings + dispositions required) in SKILL.md + `references/install.md` |
| A4 | `convergence_policy_check.py` + `findings_shape_check.py` fixtures include embedded-findings + dispositions records; round-trip asserts record-with-findings validates; `convergence_policy_check` asserts every finding defect_id in a round's findings array has exactly one disposition entry with a non-empty rationale (a partial dispositions array is a contract violation — never a silent pass) |
| A5 | `skills/cross-source-review/docs/design-decisions.md` created (sibling convention) with the 3 pre-ADRs (embed-vs-external; flag-vs-forbid volatile authorities; schema back-compat required-not-optional) + the escalate-target under-defined note; doc-audit pass (rule 5): no stale enumeration of the round shape anywhere in csr docs — including the schema-version note in SKILL.md + `references/install.md` (R1's mitigation element, landed here with A3) |
| B1 | psv SKILL.md step 4: per-claim doc-findings packet persisted as a file beside the coverage-record; extractor guidance: prefer durable in-repo sources; volatile sources flagged |
| B2 | `coverage-record.schema.json` gains the volatile-authority registry (claim_ref → volatile source, covering verified claims too); `coverage_policy_check.py` validates |
| B3 | psv test fixtures: packet-with-registry record validates; `fetched_quote_gate.py` unchanged-green |
| C1 | `jsonschema` in both `[project.optional-dependencies] dev` and `[dependency-groups] dev`; `uv sync` succeeds; `converge.py` under the repo venv validates without the SKIP note |
| E1 | Full test suites green: csr (disconnect/plugin_layout/findings_shape/convergence_policy/lint_self/dogfood) + psv (disconnect/plugin_layout/findings_shape/coverage_policy/fetched_quote/lint_self/dogfood) + pd suite (its infra shares the repo pyproject that C1 touches — regression check not vacuous) + bc suite unaffected; no `coverage` SKIP note under the repo venv |

## Phase acceptance gates

- Gate 1 (after A1-A4): a csr-record fixture with embedded findings + dispositions validates; `converge.py` emits both.
- Gate 2 (after B1-B3): a psv coverage-record fixture with the volatile-authority registry validates; the packet file lands beside the record.
- Gate 3 (after C1): `converge.py` under the repo venv emits no SKIP note.
- Gate 4 (E1): full self-gate sweep green; fix B's acceptance holds verbatim — every non-verified finding's source is re-fetchable; every volatile source is flagged in the registry (flagging suffices only for volatile VERIFIED-claim sources); the audit's two record-layer defects demonstrably closed (a reader can list every finding per round, its severity, and what was done about it).

## Risks and mitigations

- R1 — schema back-compat: old counts-only records (e.g. the fedaot-kb one) no longer validate. Mitigation: accepted by pre-ADR (historical records, no migration); csr SKILL.md + install.md note the schema version.
- R2 — disposition producer gap: dispositions only exist if the orchestrator records them at reconcile time. Mitigation: A3 makes step 2 the producing step; converge.py REJECTS a round missing dispositions (required input) — never silent.
- R3 — psv packet bloat: per-claim quotes can be large. Mitigation: packet stays per SKILL.md (findings only; verified counted-not-listed); the registry is the verified-claim signal.
- R4 — test fixture churn: schema change ripples through convergence fixtures. Mitigation: A4 lands with the schema change in the same item; run `convergence_policy_check.py` per commit.
- R5 — escalate target under-defined (P73): SKILL.md's reconciliation row names no target. Mitigation: A3 states the target explicitly in step 2 (human escalation).

## Out of scope

- Fix D (fedaot-kb doc repointing) — external repo, fedaot-kb's own process.
- The fedaot-kb environment gap (jsonschema absent in fedaot-kb's own `.venv`/`pyproject.toml` — the environment where the audited degradation occurred) — external; tracked as a follow-up to fix D's handoff. Fix C prevents the gap in THIS workspace only (fix C's coverage note).
- `parallel-development` core (its counts-only run-record is evidence, not a fix target here).
- `blueprint-crafting` / `prior-art-search` internals.
- Outcome-axis judgments (whether the audit's assessment is right) — human.
- The pre-existing modified profile files (`skills/*/infra/scripts/profiles/{deepseek,qwen3}.json`) — unrelated proxy config, left untouched.

## Cross-cutting tasks

- X1 — ADR log file creation + doc-audit grep (A5): `grep -rn "same_source_findings\|findings trend" skills/cross-source-review/` for stale enumerations after the schema change.
- X2 — Sidecar conventions: this plan's own queue + run-record land in `docs/` (pd consumes via `plan_queue.py`).
- X3 — Commit convention: one coherent commit per logical change, `parallel-dev:` prefix, `Co-Authored-By` trailer (workspace rule 9); commit only when the user asks.
