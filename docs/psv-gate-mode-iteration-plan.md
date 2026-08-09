# psv Gate Mode — Iteration Plan (enumeration updates, pd-facing)

> Status: **Iteration plan** for the enumeration updates of [psv-gate-mode-proposal.md](psv-gate-mode-proposal.md) (csr-converged: substantive_converged=true, 2 rounds, 9/9 core claims — record at docs/psv-gate-mode-proposal.csr-record.json; psv skipped per rule 13 — local citations, csr-verified; gate-mode evidence at docs/psv-gate-dogfood.gate-record.json).
> Authority chain: `docs/psv-gate-mode-proposal.md` (master, converged) > psv SKILL.md + proposal.md + design-decisions.md > this plan. On conflict, the proposal wins.

## Complexity tiers

- S — single-passage text edits: E1, E4, E5.
- M — multi-location wording + diagram: E2, E3.
- L — ADR entry + doc-audit sweep: E6, E7.

## Dependency edges

```
E1 (CLAUDE.md rule 13) — independent
E2 (USER_GUIDE) — independent
E3 (psv SKILL.md) — independent
E4 (csr SKILL.md) — independent
E5 (psv proposal.md Q5) — independent
E6 (psv design-decisions.md ADR) — depends E3 (wording must exist before the ADR cites it)
E7 (doc-audit grep) — depends ALL (E1-E6)
```

## DAG

- wave 1 (parallel): E1, E2, E3, E4, E5
- wave 2: E6 (← E3)
- wave 3: E7 (← all)

## Per-iteration DoD

| Item | DoD |
| --- | --- |
| E1 | CLAUDE.md rule 13: line 112/122 wording updated — psv is additive; when rule-13 conditions hold, run it FIRST as the gate (load-bearing-claims subset, GO/NO-GO, gate record), then after csr as the authoritative full-M record; non-rule-13 docs unchanged. CONTINGENT (novel-2): ODP-1 resolved = recommended-default (2026-08-09); ODP-5 (quantified q·C > p vs qualitative trigger) is OPEN — E1/E5 wording carries the proposal's contingency ("no new trigger machinery beyond the ODP-5 decision") |
| E2 | USER_GUIDE.md lines 24, 27-31 (diagram), 33, 47, 49, 54 updated — gate mode named in the Two-axis section + diagram; "after or beside csr" gains "and before csr as the gate when rule-13 conditions hold"; the GO-non-authoritative marker is included in the Two-axis section ("the gate's GO/NO-GO is a batch signal, NOT a coverage record — the authoritative coverage disclosure comes only from the full-M run") |
| E3 | psv SKILL.md description + line 73 updated — gate-mode note (subset gate, batch GO/NO-GO, gate record non-authoritative, bounded re-gate ≤2) |
| E4 | csr SKILL.md coordination section — psv-positioning note ADDED (gate mode reachable at the decision point; currently no psv text exists there) |
| E5 | psv docs/proposal.md Q5 — "after or beside csr" amended: "and before csr as the gate when rule-13 conditions hold" |
| E6 | psv docs/design-decisions.md — ADR entry: gate-mode decisions (GO = premise signal outside ADR #3's top-line contract; gate-M=0 = trigger-misapplication OR extractor miss, human adjudicates; batch threshold = refuted/unverifiable load-bearing or ≥2 narrowed load-bearing → NO-GO; bounded re-gate ≤2, not a debate loop — ADR #1 intact) |
| E7 | doc-audit grep (rule 5): every pipeline-order statement in the 6 enumerated locations updated. Patterns: "after or beside", "csr → psv", "after csr", "additive outcome-axis", "runs after or beside", "optional and additive", "inserted only when it adds value". EXCLUSIONS (legit old-wording occurrences, NOT to edit): the master proposal itself (historical context lines), this plan's own DoD table, the frozen queue, historical records (docs/record-auditability-fix-plan.md:3), and the ADR texts. Scope: the 6 enumerated locations, not the whole workspace (Gate 1's scope) — a workspace-wide sweep false-flags the exclusions |

## Phase acceptance gates

- Gate 1 (after E1-E5): the proposal's enumeration list (rule 5 completeness) is fully covered; grep (with the E7 exclusions) finds no stale pipeline-order statement in the 6 enumerated locations.
- Gate 2 (after E6): the ADR entry cites the E3 wording; ADR #1/#3/#5 texts untouched.
- Gate 3 (E7): full doc-audit sweep green — the proposal's "Enumerations to update" list maps 1:1 to landed edits.

## Risks and mitigations

- R1 — wording drift between the 6 locations (rule 10: one joiner, one term). Mitigation: E7's grep + the proposal's trigger/batch-rule wording copied verbatim.
- R2 — ADR #1/#3/#5 text accidentally amended. Mitigation: E6 touches ONLY the new ADR entry; E7 grep excludes the ADR texts.
- R3 — the gate-mode note in psv SKILL.md conflicts with the "additive, not sequential" positioning. Mitigation: E3 wording mirrors the proposal's boundary section (gate is an OPTIONAL insertion mode, not a pipeline stage).

## Out of scope

- psv/csr core-logic code changes (the gate record schema formalization is a deferred follow-up per ODP-3/N07).
- The gate record schema (deferred).
- Any behavior change to non-rule-13 docs.
- The evidence experiment subject (fedaot-kb doc — external).

## Cross-cutting tasks

- X1 — E7's grep patterns list doubles as the rule-5 doc-audit checklist.
- X2 — commit convention: one coherent commit per logical change, `parallel-dev:` prefix, `Co-Authored-By` trailer (rule 9).
