# ODP-2 Design — consume the convergence verdict + carry ODP resolution

> Status: **Design decision — IMPLEMENTED in code** (`upstream` field `117783e` + emission `a8f4cc6`; ODP `resolution` carry `729fec2` + resolved-ODP seeding `b2ff3a6`). Resolves charter ODP-2. Builds on [rich-path-design.md](rich-path-design.md). Goes through its own convergence loop.
>
> Companion docs: [bc-pd-coupling-charter.md](bc-pd-coupling-charter.md) — the rules; [rich-path-design.md](rich-path-design.md) — R4 form + ODP-3 (the rich path this builds on); [blueprint-parallel-handshake-analysis.md](blueprint-parallel-handshake-analysis.md) — current-state analysis.

**File-reference convention** — same as the charter (the canonical legend, including the same-name caveat for `SKILL.md` / `design-decisions.md` / `run-record.schema.json`). This doc cites BOTH run-record schemas (blueprint-crafting's and parallel-development's), distinguished inline by the skill each belongs to.

## Context (verified current state)

ODP-2 covers two rich-path faithful-consumption gaps (charter R6) that the basic rich path (rich-path-design) did not address:

- **The verdict is a separate artifact, not in plan-model items.** `process_converged` lives in blueprint-crafting's spec run-record (`infra/schemas/run-record.schema.json`: `artifact_type`, `process_converged` (bool), `rightness` (constant `human_confirm_required`), `inner_ring`, `outer_ring`, `coverage`, `caveats`), emitted by `verdict.py`. It is NOT a field on plan-model items. So consuming it is a separate channel from the queue.
- **The verdict is not wired into a freeze step.** `verdict.emit` is called only in tests (`run_record.py`) and the `verdict.py` CLI `main()` — same wiring gap as the projection (rich-path-design D1). `SKILL.md:58` names the spec run-record a freeze product conceptually, but no freeze step emits it to a consumer-readable location.
- **The projection drops ODP resolution.** `project_plan_model_item` translates `odp_status → open_decisions` keeping only `id` + `kind`, dropping `resolution` (`infra/scripts/plan_model.py:108-129`; noted in rich-path-design). blueprint-crafting's `odp_status` carries `{id, kind, resolution}` (`plan-model.schema.json`); a resolve-now ODP without `resolution` is unresolved and Blocks convergence.
- **parallel-development's run-record has no upstream-provenance field.** Its run-record schema (`infra/schemas/run-record.schema.json`) is `additionalProperties: false` and has no field for an upstream verdict. Adding one requires a schema + validator update (the schema docstring states this).
- **parallel-development has an ODP-resolution model.** `plan_queue.py resolve-odp` stores `odps[odp_id] = {status: "resolved", resolution, defaulted}`; `claim` refuses any item with an unresolved resolve-now ODP (`plan_queue.py:418-431`). So parallel-development can already represent a resolved ODP — the gap is that the projection never seeds it.

## Decision

**D1 — Verdict: blueprint-crafting emits the spec run-record at freeze; parallel-development records `process_converged` as upstream provenance, not a gate-skip.**

- blueprint-crafting's freeze step (rich-path-design D1) emits the spec run-record alongside the queue. `verdict.py` already produces it; `SKILL.md:58` already names it a freeze product. No new verdict logic — only the freeze-time emission (the same wiring gap rich-path-design addresses for the queue).
- On the rich path, parallel-development reads the run-record and records `process_converged` in its OWN run-record as upstream provenance — a new OPTIONAL field, e.g. `upstream: {producer, process_converged, profile}`. (parallel-development's run-record is `additionalProperties: false`, so this needs a schema + validator addition.)
- Acting on it is conservative and fail-safe: `process_converged=true` is a provenance signal (the upstream quality bar was met), NOT an execution-correctness guarantee (charter R6: necessary but not sufficient). Default behavior is unchanged — parallel-development still runs its own validation. A gate-skip is an explicit opt-in, never the default.
- Degrade: no upstream run-record (free path) → the field is omitted; `process_converged` false or absent → parallel-development does not trust it and validates normally.

**D2 — ODP resolution: extend the projection to carry blueprint-crafting's `resolution`; parallel-development seeds its resolve-odp state on the rich path.**

- Extend `project_plan_model_item` so each `open_decisions` entry carries blueprint-crafting's resolution: `{id, kind, resolution}` (resolution present = blueprint-crafting already resolved it). This is the "beyond basic" projection refinement that rich-path-design explicitly deferred to ODP-2.
- On the rich path, parallel-development's `plan_queue` seeds `odps[odp_id] = {status: "resolved", resolution, defaulted: false}` from the carried resolution, so `claim` sees a resolve-now ODP as already resolved and does not re-ask a decision blueprint-crafting closed.
- Degrade: no resolution carried (free path, or blueprint-crafting did not resolve) → parallel-development's existing behavior (surface at the mandatory checkpoint). Fail-safe.

## Why

- D1 honors charter R6 + Premise P: the verdict is trust scaffolding produced for agent consumers; recording it as provenance lets parallel-development (and its human reader) see "upstream converged" without re-deriving. The conservative default (no auto gate-skip) respects that `process_converged` ≠ execution-correct.
- D2 closes the faithful-consumption gap rich-path-design flagged: without resolution carry, parallel-development re-asks decisions blueprint-crafting already resolved → divergence and waste.
- Both are additive (a new optional field; an extended projection) and fail-safe (absent → today's behavior).

## Rejected

- **Embed the verdict in the queue (per-item).** The verdict is artifact-level (one per plan-model), not per-item; embedding it distorts the queue's item-list grain. A separate run-record file is the clean channel.
- **Auto gate-skip when `process_converged=true`.** Violates charter R6 ("necessary but not sufficient"); process convergence ≠ execution correctness. Opt-in only, never default.
- **Carry the full run-record into parallel-development.** Over-coupling; parallel-development needs only `process_converged` (+ profile) as provenance, not the inner-ring / outer-ring detail.
- **Re-derive the verdict inside parallel-development.** Duplicates blueprint-crafting's convergence machinery and violates independence (charter R1).

## Required follow-ups (out of scope)

- parallel-development run-record schema: add the optional `upstream` field + update the validator — implementation.
- blueprint-crafting `project_plan_model_item`: extend to carry `resolution` into `open_decisions` — implementation (amends the projection; fold into the ADR #1 amendment noted in rich-path-design).
- parallel-development `plan_queue`: seed `odps` from carried resolution on the rich path — implementation.
- ODP-1 — blueprint collapse.

## Coverage notes (workspace rule 3)

1. IMPLEMENTED in code — `freeze` emits the run-record (`13b391b`); pd records `process_converged` as upstream provenance (`117783e` schema + `a8f4cc6` emission); the projection carries ODP `resolution` (`729fec2`) and pd seeds it (`b2ff3a6`).
2. The `upstream` field shape is illustrative; exact fields TBD at implementation (must be optional and fail-safe).
3. `process_converged` is explicitly NOT a gate-skip authorization by default — provenance only, conservative default.

## Convergence log

- **Doc iteration 1** — wrote v1; review found the file-reference legend's same-name caveat listed only `SKILL.md` and `design-decisions.md`, but this doc cites `run-record.schema.json` in BOTH skills (each has one at `infra/schemas/`) — a reader could confuse which. Fixed: the legend's same-name caveat now includes `run-record.schema.json`, and notes the two citations are distinguished inline. markdownlint clean (exit 0).
- **Doc iteration 2** — re-reviewed clean: markdownlint exit 0; all 5 Context claims re-verified against source (bc run-record schema + verdict.py not wired to freeze; projection drops resolution; pd run-record `additionalProperties: false`; pd `resolve-odp` shape + `claim` refuse range); inline `run-record.schema.json` citations distinguish bc vs pd; the "no auto gate-skip" safety point stated consistently in D1 / Rejected / coverage; D2 seed shape matches pd's `resolve-odp` model; dependency on rich-path-design's freeze step is consistent. No further issues found. **Loop closed.**
- **Doc iteration 3** — holistic review: simplified the file-reference legend to "same as the charter" now that the charter's caveat is canonical and complete (includes `run-record.schema.json`); kept this doc's note that it cites BOTH run-record schemas inline. No content changes. markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 4** — implementation-status sync: this design is now IMPLEMENTED in code (`upstream` field `117783e` + emission `a8f4cc6`; ODP `resolution` carry `729fec2` + resolved-ODP seeding `b2ff3a6`). Flipped the Status block + coverage note from "not implemented" to "IMPLEMENTED". markdownlint clean (exit 0). **Loop closed.**
