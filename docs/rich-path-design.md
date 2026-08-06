# Rich-Path Design (charter R4 form + ODP-3 detection)

> Status: **Design decision — IMPLEMENTED in code** (freeze emits queue + run-record `13b391b`; producer marker `f27ea11` emit + `73eb392` detect). Resolves charter R4's form and ODP-3 (rich-path detection), and closed the analysis doc's freeze→queue seam. Grounded in the verified current state of both skills' code. (ODP-1 and ODP-2 are also now implemented — see their docs.) Goes through its own convergence loop.
>
> Companion docs: [bc-pd-coupling-charter.md](bc-pd-coupling-charter.md) — the rules; [blueprint-parallel-handshake-analysis.md](blueprint-parallel-handshake-analysis.md) — the current-state analysis; [odp2-verdict-design.md](odp2-verdict-design.md) and [odp1-blueprint-collapse-design.md](odp1-blueprint-collapse-design.md) — the other two ODP designs.

**File-reference convention** — same as the charter. `docs/*.md` = blueprint-crafting; `references/*.md` = parallel-development. Same-name caveat: both skills ship a `SKILL.md` and a `design-decisions.md`; bare `SKILL.md` = blueprint-crafting's; ADR citations point to blueprint-crafting's `docs/design-decisions.md`.

## Context (verified current state)

- **blueprint-crafting has the projection, but does not emit.** `project_plan_model_to_queue` / `project_plan_model_item` (`infra/scripts/plan_model.py:108,152`) exist and are tested, but are called ONLY in tests (`round_trip.py`, `end_to_end.py`). No freeze step or CLI emits a `.queue.md`. The "freeze" lifecycle step (`SKILL.md:58,72`) is conceptual; its concrete product is the plan-model, not a queue.
- **The projection already carries readable upstream_only fields.** `project_plan_model_item` emits: the executable subset (`item_id / seq / depends_on / dod_ref`) + `title` / `scope` / `source_location` / `parallel_group` + `open_decisions` (translated from `odp_status`, keeping only `id` + `kind`, dropping `resolution`) + `blueprint_subset` (empty). It does NOT carry `complexity` / `risk` / `constraints_profile`.
- **parallel-development's parser already reads those fields.** `plan_queue.py` `parse_queue_structure` stores the whole item dict; `merged_item` (273-291) surfaces `title` / `scope` / `source_location` / `parallel_group` / `open_decisions` / `blueprint_subset`. The field-flow from a projected queue into parallel-development is already end-to-end functional.
- **parallel-development has no blueprint-crafting-shape awareness.** `plan_queue.py` has zero references to `artifact_type` / `plan_model_version` / `blueprint-crafting`. It is purely free-path.
- **The verdict is not in items.** `process_converged` is emitted by `verdict.py` into the run-record, not into plan-model items. Consuming it is a separate integration (ODP-2), out of scope here.

So the field-flow machinery already exists on both sides; the only real gaps are (a) blueprint-crafting does not emit the queue at freeze, and (b) parallel-development does not detect blueprint-crafting origin.

## Decision

**D1 — Form: blueprint-crafting emits the projected queue at freeze; parallel-development reads it with its existing parser.**

- blueprint-crafting's freeze step invokes the existing `project_plan_model_to_queue` and writes a `.queue.md` (the format `plan_queue.py` already parses: a fenced ```json block under `## Items`). No new projection logic is needed for the basic rich path — the projection already carries the readable upstream_only fields.
- parallel-development's `parse_queue_structure` / `merged_item` read the emitted fields unchanged. No new parser.
- Rationale: maximal reuse (workspace rule 7). Both the projection and the parser exist; the only missing piece is the freeze-time emission.

**D2 — Detection (ODP-3): a producer marker on the queue; fail-safe to the free path.**

- The emitted queue carries a producer marker (e.g. a `producer: blueprint-crafting` + `plan_model_version` field). parallel-development checks it: present → rich path (treat the carried fields as blueprint-crafting-authored and utilize them per charter R5/R6); absent or unreadable → free path (re-normalize, ignore unknown fields — current behavior).
- Constraint: `plan_queue.py` parses only the fenced ```json block with no YAML dependency (`plan_queue.py:10,33`), and that block is a **list** of item dicts (`parse_queue_structure` requires a list). So the marker cannot be YAML frontmatter or a top-level json field; it rides as a **per-item field** (exact field TBD at implementation).
- Fail-safe is mandatory: detection never blocks. Worst case parallel-development re-normalizes, exactly as today.

## Why

- The field-flow machinery already exists end-to-end (blueprint-crafting projection + parallel-development parser); the rich path is therefore low-cost to enable — it is "wire the existing projection into freeze + add a marker", not a new subsystem.
- Reuses both skills' existing code; no second parser (keeps parallel-development's parser uniform — one format).
- Fail-safe detection preserves charter R1 (independence) and R2 (free input): no marker → today's free-path behavior, unchanged.

## Rejected

- **parallel-development reads blueprint-crafting's plan-model JSON directly.** Needs a second parser in parallel-development; couples it to blueprint-crafting's schema; breaks parser uniformity. The queue format already bridges the two.
- **Auto-detect by field-shape heuristics (no marker).** Fragile (field overlap with free-path queues); an explicit marker is cheaper, unambiguous, and fails safe.
- **Carry the verdict (`process_converged`) in the rich queue now.** It lives in the run-record, not items; carrying it is ODP-2 (separate channel). Deferred.

## Known faithful-consumption gap (R6, noted not resolved here)

The existing projection translates `odp_status → open_decisions` keeping only `id` + `kind`, dropping `resolution`. So even on the rich path, parallel-development would see an ODP's id/kind but not that blueprint-crafting already resolved it → parallel-development might re-ask. Closing this (carry `resolution` or a resolved flag) is an R6 refinement, deferred to the ODP-2 follow-on (it touches the same blueprint-crafting→parallel-development field set as the verdict).

## Required follow-ups (out of scope)

- Amend blueprint-crafting ADR #1 wording: "upstream_only ignored downstream" → "ignored on the free path; utilized on the rich path". The three-way classification stands; only the consumption mode is new.
- ODP-2 — consume the verdict (separate run-record channel) + the ODP-resolution carry noted above.
- ODP-1 — blueprint collapse.
- R5/R6 field-level — which carried fields parallel-development utilizes and how (e.g. `complexity` / `risk` are not currently carried; carry them or not).

## Coverage notes (workspace rule 3)

1. IMPLEMENTED in code — the `freeze` operator emits the `.queue.md` + `.run-record.json` (`13b391b`); the producer marker is `f27ea11` (emit) + `73eb392` (detect). The freeze→queue seam is closed.
2. The exact producer-marker field and location are TBD at implementation; the decision is "explicit marker, fail-safe to the free path, no YAML parser required".
3. The verdict and ODP-resolution carry are explicitly NOT covered here — ODP-2.

## Convergence log

- **Doc iteration 1** — wrote v1; review found D2 specified a frontmatter producer-marker, but `plan_queue.py` deliberately has no YAML dependency (parses only the ```json block, `plan_queue.py:10,33`) — a frontmatter marker would force a YAML parser on parallel-development, contradicting its design. Fixed: D2 now states the marker location must not require a YAML parser (candidate: a field within the json block), and coverage note 2 updated. markdownlint clean (exit 0).
- **Doc iteration 2** — found a precision issue: D2 said the marker could be "a field within the json block", but the json block is a **list** of item dicts (`parse_queue_structure` requires a list), so a top-level field does not fit and YAML frontmatter is excluded by the no-YAML constraint. Fixed: the marker rides as a per-item field. markdownlint clean (exit 0).
- **Doc iteration 3** — re-reviewed clean: markdownlint exit 0; load-bearing code claims re-verified against source (projection field set at `plan_model.py:108-129`; `parse_queue_structure` requires a list at `plan_queue.py:96-104`); D1/D2 internally consistent; defer-scopes (ODP-1 / ODP-2 / ADR #1 amendment) honest; citations correct. No further issues found. **Loop closed.**
- **Doc iteration 4** — holistic review: extended the Companion-docs line to include the ODP-2 and ODP-1 designs (they did not exist when this doc converged). No content changes. markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 5** — implementation-status sync: this design is now IMPLEMENTED in code (`13b391b` freeze operator; producer marker `f27ea11` emit + `73eb392` detect). Flipped the Status block + coverage note from "not implemented" to "IMPLEMENTED". markdownlint clean (exit 0). **Loop closed.**
