# blueprint-crafting ↔ parallel-development — Handshake Alignment Analysis

> Status: **Round-1 self-audit applied.** Single-author static analysis of both skills' specs plus the handshake tests — NOT a fresh-context adversarial review, and NOT a live end-to-end run. A first-pass reading overstated the data-contract alignment as a two-directional live contract; the self-audit re-grounded it as a single-sided compatibility assertion and surfaced the freeze→queue seam (since confirmed not wired; design-resolved in [rich-path-design.md](rich-path-design.md)). Outstanding items are disclosed as coverage notes (workspace rule 3), not hidden. See the convergence log at the end.
>
> Scope: how well does `blueprint-crafting`'s OUTPUT artifact spec align with `parallel-development`'s INPUT artifact spec?
>
> Companion docs: [bc-pd-coupling-charter.md](bc-pd-coupling-charter.md) — the prescriptive coupling rules; [rich-path-design.md](rich-path-design.md) / [odp2-verdict-design.md](odp2-verdict-design.md) / [odp1-blueprint-collapse-design.md](odp1-blueprint-collapse-design.md) — the three ODP designs (resolved at design level; this doc's open seam is closed at design level by rich-path-design).

**File-reference convention** — paths are relative to the skill root. **Dir convention**: `docs/*.md` = blueprint-crafting; `references/*.md` = parallel-development (the two skills use different companion-doc dirs). Under `skills/blueprint-crafting/`: `SKILL.md`, `plan-model.schema.json` (cited as `schema:`), `docs/design-decisions.md` (the ADR log), `infra/scripts/plan_model.py`, `infra/test/round_trip.py`, `infra/test/end_to_end.py`. Under `skills/parallel-development/`: any `references/*.md` (e.g. `scope.md`, `intent-blueprint.md`, `plan-driven-mode.md`, `arch-contracts.md`, `external-skills.md`, `orchestration-layers.md`, `design-decisions.md`), `infra/scripts/plan_queue.py`, `infra/scripts/vale_adapter.py`. **Same-name caveat**: both skills ship a `SKILL.md`, a `design-decisions.md`, AND a `run-record.schema.json` (`infra/schemas/`). Bare `SKILL.md` = blueprint-crafting's. ADR citations point to blueprint-crafting's `docs/design-decisions.md`; parallel-development's `references/design-decisions.md` is a separate, unrelated log.

## Context

`blueprint-crafting` produces convergence-checked upstream artifacts (product-spec / arch-design / iteration-plan / executable-summary / research). `parallel-development` consumes upstream plans as authoritative references and implements code. The two are a deliberate pair:

- bundled as a 2-skill plugin (`skills/parallel-development/infra/test/plugin_layout.py:74` — `EXPECTED_SKILLS`)
- framed as a **specify-then-implement** pipeline (`skills/blueprint-crafting/SKILL.md:9`)

## Headline finding

The alignment surface is a **deliberately narrow contract** — the **executable subset** (`item_id / seq / depends_on / dod_ref`) — and little else. Five verified facts frame everything below:

1. The executable subset is **representation-compatible** between `plan-model` and the `.queue.md` format, and **lossless both directions** — proven by `skills/blueprint-crafting/infra/test/round_trip.py` (4/4 PASS, run this session).
2. That proof is **single-sided**. `round_trip.py` and `end_to_end.py` run inside `blueprint-crafting` only. They prove blueprint-crafting's output is *shaped right* for parallel-development's parser; they do NOT prove parallel-development consumes it.
3. `parallel-development` references **none** of `plan-model` / `artifact_type` / `plan_model_version` / `process_converged` / `rightness` / `constraints-profile` (grep-empty across the skill; `process axis` appears once, but only describing blueprint-crafting's researcher in `references/orchestration-layers.md:81`, not as an adopted concept). Its standard entry point re-normalizes an @-referenced *source document* in its own Phase −1 (`references/plan-driven-mode.md`), not a blueprint-crafting plan-model.
4. `parallel-development` models `blueprint-crafting` as a **complementary axis-partner** (the upstream-doc-STRUCTURE checker, paired with Vale's PROSE axis) — `vale_adapter.py:10`, `references/arch-contracts.md:86`, `references/external-skills.md:40` — NOT as the upstream supplier whose artifacts it ingests.
5. There are **two frozen "blueprint" structures that are not the same artifact** (see Tension A).

Net: the contract is real and self-tested green, but it is **interoperability insurance, not a verified hot-path exchange.**

## The data contract (what aligns)

`plan-model.schema.json` classifies every item field into three subsets (ADR #1 — the executable-subset round-trip decision; `docs/design-decisions.md`):

| Subset | Fields | Cross-skill handling |
| --- | --- | --- |
| executable | `item_id, seq, depends_on, dod_ref` | lossless round-trip (tested) |
| upstream_only | `title, scope, source_location, complexity, risk, odp_status, constraints_profile, parallel_group` | not part of the lossless contract |
| downstream_only | `blueprint_subset` | no upstream source; parallel-development fills it |

`plan_queue.py` reads `item_id` (required, enforced in `parse_queue_structure` at 78-104) + `seq` + `depends_on` + `dod_ref`, plus — for display/orchestration only (field access in `merged_item` at 273-291) — `title` + `scope` + `source_location` + `blueprint_subset` + `parallel_group` + `open_decisions`.

**Artifact-type coverage of the queue contract** (corrected in the self-audit; `schema:34`). The executable-subset mechanism is artifact-type-agnostic, and the schema explicitly names **iteration-plan** AND **executable-summary** as the queue-round-tripping types. `plan_queue.py` does not inspect `artifact_type`.

| blueprint-crafting output | Consumed by parallel-development? | How | Contract strength |
| --- | --- | --- | --- |
| iteration-plan | yes | plan-driven mode → `plan_queue.py` executable subset | strong (4-field lossless) |
| executable-summary | yes (structurally) | same executable-subset mechanism (`schema:34`) | strong |
| arch-design | yes (context only) | `references/scope.md:11` authoritative reference; carried into the queue `authority_chain` as conflict-arbitration rules | weak (opaque, no field contract) |
| product-spec (PRD) | no | `scope.md:36` routes PRD-authoring to `requirements-manager`; parallel-development uses its own Intent Blueprint | none |
| research | no | non-queue artifact (no item-parser, `SKILL.md:52`); parallel-development mentions its constraints only as an axis description | none |

## Strong alignment (verified)

- **Executable-subset data shape** — field names/types/semantics match; `round_trip.py` green.
- **Freeze + read-only-guard pattern is isomorphic** — both use `status: frozen` + PreToolUse guard + revision channel. blueprint-crafting freezes the plan-model; parallel-development's `blueprint_guard.py` guards `.queue.md` and `.blueprint.md` (`plan_queue.py:7`, `references/intent-blueprint.md:21-25`). Caveat: they guard *different* artifacts, not a shared one.
- **Normalizer philosophy is shared (copy-not-import)** — both use graded extraction (latch high-confidence / semantic-infer low-confidence; heuristics never Blocker). blueprint-crafting copied parallel-development's pattern (`SKILL.md:104`, workspace rule 7).
- **resolve-now / deferred ODP semantics coincide** — both split must-resolve vs may-defer, and both gate forward progress on resolve-now. (Coincidence of concept, not a shared field — see Tension C.)
- **Scope guards are symmetric** — both have entry-time soft routing.

## Tensions (verified, persist)

### Tension A — two "blueprint" structures, not one

| | blueprint-crafting plan-model | parallel-development Intent Blueprint |
| --- | --- | --- |
| what it is | normalized spec/arch-design/iteration-plan | `intent-blueprints/<task>-v<n>.blueprint.md` |
| structure | items + anchors + authority_chain + convergence verdict | UC / AC (BDD) / NFR |
| producer | blueprint-crafting | parallel-development's own Phase 0 (`requirements-manager` / `Plan`; `intent-blueprint.md:18`) |

A queue item's `dod_ref` points into parallel-development's OWN structures — an Intent Blueprint `#AC-X`, or a master plan's validation gate (`plan-driven-mode.md:58-62,107-130`) — never into blueprint-crafting's spec. The only structural link between the two is the `blueprint_subset` field, which blueprint-crafting leaves empty and parallel-development fills with its own AC ids (`schema:82`, `round_trip.py` test D).

### Tension B — the convergence verdict is not consumed

blueprint-crafting's convergence machinery (anchors present, authority consistent, ODPs resolved, sources cited, `process_converged=true`) is **stripped at the consumption boundary**. parallel-development takes only the executable subset and re-normalizes the rest. A converged plan-model and an unconverged one are indistinguishable to parallel-development (grep: zero references to the verdict fields).

### Tension C — ODP is local to each side, not interchanged

blueprint-crafting: `odp_status` = `[{id, kind, resolution}]` (`schema:79,85-94`). parallel-development: `open_decisions` = `[{id, kind, question, default?, trigger?}]` (`plan-driven-mode.md:184`, `plan_queue.py:257`). ODP is **upstream_only, not in the executable contract**, and `round_trip.py` does not test it. Each side generates its own ODP representation for its own gate (blueprint-crafting's convergence checker; parallel-development's `claim` gate). They never interchange. The shared `id` + `kind` is a coincidental concept overlap, not a contracted field.

### Tension D — cognitive + routing asymmetry

- blueprint-crafting frames itself as producing "for parallel-development to consume" (`SKILL.md:9`) and routes code work to parallel-development **by name** (`SKILL.md:41`).
- parallel-development frames blueprint-crafting as an **axis-partner** (structural-doc checker) and routes spec/PRD/roadmap work to generic `requirements-manager` / `architect` (`scope.md:36-37`), **never naming blueprint-crafting** as a routing target.

This is defensible (parallel-development should accept any upstream), but the "closed loop" exists only in blueprint-crafting's docs.

## The one open seam (the actionable finding)

**The freeze→queue projection step is not verified as wired.**

- blueprint-crafting's canonical freeze output is the **plan-model** (`SKILL.md:58`: "frozen plan-model + spec run-record").
- parallel-development's parser reads **`.queue.md`** (markdown + fenced ```json).
- A bridge function `project_plan_model_to_queue` exists and is tested (`infra/scripts/plan_model.py:152`).
- No evidence was found that the freeze lifecycle calls it to emit a `.queue.md`. The documented freeze product is the plan-model, not a projected queue.

This is the single most verdict-affecting uncertainty: it decides whether the handshake is a *live path* or *only a compatibility contract*. Static analysis did not resolve it. See coverage notes.

**Update** — this seam is now confirmed (the projection is called only in tests; no freeze step emits a queue) and resolved at design level in [rich-path-design.md](rich-path-design.md) (emit the projected queue at freeze + a per-item producer marker). Implementation pending; the code is unchanged.

## Revised alignment scoring

| Dimension | Level | Basis |
| --- | --- | --- |
| Executable-subset data shape | medium-high | lossless + self-tested green; live path unverified |
| Live cross-skill data flow | unverified | freeze→queue projection not confirmed wired |
| Freeze + guard mechanism | medium-high | isomorphic pattern; guards different artifacts |
| Normalizer philosophy | high | copy-not-import, shared graded extraction |
| Artifact-type coverage | medium | iteration-plan + executable-summary have queue contract |
| Convergence-verdict propagation | low | `process_converged` not consumed |
| Cognitive symmetry | medium-low | supplier vs axis-partner |
| Semantic bridge (spec ↔ implementation) | low | empty `blueprint_subset` + `dod_ref` pointer only |
| Cross-skill ODP | n/a | local to each side |

## Coverage notes (what was NOT verified — workspace rule 3)

1. **freeze→queue projection wiring** — confirmed (this session): `project_plan_model_to_queue` is called only in tests; no freeze step emits a `.queue.md`. **Resolved at design level** in [rich-path-design.md](rich-path-design.md) (emit the projected queue at freeze + a per-item producer marker for detection). Implementation pending; code unchanged.
2. **Live end-to-end run** — no instance of blueprint-crafting output actually flowing into parallel-development was observed; this analysis is static.
3. **spec/arch-design `items` semantics** — the schema requires `items` for all artifact types, but only names iteration-plan/executable-summary as queue-round-tripping. Whether spec/arch-design items are meant to round-trip is undocumented.

## Convergence log

**Analysis reasoning (completed before this doc was written):**

- **Round 0** — mapped both skills via parallel Explore agents plus direct reads of `plan-model.schema.json`, `plan_queue.py`, `intent-blueprint.md`, `scope.md`, `plan-driven-mode.md`, `round_trip.py`. Ran `round_trip.py` (green) and cross-skill vocabulary greps.
- **Round 1 (self-audit of the analysis)** — re-checked conclusions against evidence. Corrections applied:
  - executable-summary **does** have the queue contract (`schema:34`) — the earlier matrix row was wrong; artifact-type coverage raised low → medium.
  - the handshake is a **single-sided compatibility assertion**, not a two-directional live contract — data-contract level lowered high → medium-high; added the "live data flow = unverified" row.
  - the ODP "naming mismatch" was **reframed** from a gap-to-fix to local-to-each-side (not interchanged) — ODP row set to n/a.
  - the "ignored fields" claim was **refined** — only `parallel_group` is operational (fan-out hint); `title` / `scope` / `source_location` are display-only.
  - the open seam (freeze→queue projection) was added as the primary actionable finding.

**Doc iteration (this write → review → fix loop):**

- **Doc iteration 1** — wrote v1; review found and fixed four issues: (a) the log pre-claimed "no further issues" before the loop closed (honesty, workspace rule 3) — restructured into analysis-rounds vs doc-iteration; (b) bare file references were ambiguous across the two skills — added a file-reference convention legend (rule 10); (c) "re-derived into the queue `authority_chain`" overstated the flow → "carried into"; (d) unglossed "round_trip test D" → "`round_trip.py` test D". markdownlint clean (exit 0).
- **Doc iteration 2** — found and fixed three precision issues: (a) "grep-empty across the skill" overstated for `process axis` (it appears once, describing blueprint-crafting's researcher in `references/orchestration-layers.md:81`, not as an adopted concept) — qualified; (b) `parse_queue_structure` (78-104) was credited with reading all fields, but it only enforces `item_id`; the rest are read in `merged_item` (273-291) — corrected the attribution; (c) "each queue item's `dod_ref` points to `docs/intent-blueprints`" overstated — `dod_ref` can also point to a master-plan validation gate; reframed to "points into parallel-development's OWN structures, never blueprint-crafting's spec".
- **Doc iteration 3** — found and fixed a factual citation error: ADR #1 was cited as `references/design-decisions.md`, but that is parallel-development's separate ADR log (whose own #1 is "Python stdlib only"); ADR #1 (executable-subset round-trip) lives in blueprint-crafting's `docs/design-decisions.md`. Root cause: the legend did not guard the same-name trap (both skills ship a `SKILL.md` AND a `design-decisions.md`). Fixed the path and hardened the legend (dir convention `docs/` = blueprint-crafting, `references/` = parallel-development; explicit same-name caveat).
- **Doc iteration 4** — re-reviewed clean: markdownlint exit 0; all 15 cited files verified to exist at their stated paths; line-number citations spot-checked against source. No further issues found. **Loop closed.**
- **Doc iteration 5** — cross-link update (no findings changed): the freeze→queue seam coverage note updated from "not confirmed" to "confirmed not wired" (verified this session: projection called only in tests) + a pointer to its design-level resolution in [rich-path-design.md](rich-path-design.md); the open-seam section and Status block given matching pointers. This doc remains descriptive; the code is unchanged. markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 6** — holistic review: added `run-record.schema.json` to the same-name caveat (completeness, matching the canonical charter legend); added a Companion-docs line linking the charter + the three ODP designs (this doc previously linked only rich-path). Findings unchanged; the doc remains descriptive. markdownlint clean (exit 0). **Loop closed.**
