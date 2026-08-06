# ODP-1 Design — blueprint collapse: seed the Intent Blueprint from the spec

> Status: **Design decision — IMPLEMENTED in code** (Phase-0 spec-seeding landed as agent instruction `d18ccfc`). Resolves charter ODP-1. Builds on [rich-path-design.md](rich-path-design.md) + [odp2-verdict-design.md](odp2-verdict-design.md) (the rich path). The last design-layer ODP. Goes through its own convergence loop.
>
> Companion docs: [bc-pd-coupling-charter.md](bc-pd-coupling-charter.md) — the rules; [rich-path-design.md](rich-path-design.md) — R4 form + ODP-3; [odp2-verdict-design.md](odp2-verdict-design.md) — ODP-2; [blueprint-parallel-handshake-analysis.md](blueprint-parallel-handshake-analysis.md) — current-state analysis.

**File-reference convention** — same as the charter. `docs/*.md` = blueprint-crafting; `references/*.md` = parallel-development. Same-name caveat: both skills ship a `SKILL.md` and a `design-decisions.md`; bare `SKILL.md` = blueprint-crafting's; ADR citations point to blueprint-crafting's `docs/design-decisions.md`.

## Context (verified current state)

Charter ODP-1 asked: should parallel-development's Intent Blueprint consume blueprint-crafting's spec/AC directly on the rich path, instead of being re-derived independently? Verification settles the crux — the two artifacts are **different kinds at different abstraction levels**, not aliases:

- **blueprint-crafting's product-spec** (`infra/scripts/constraints.json` profile `product-spec`): anchors = `jtbd`, `desired-outcome-metrics`, `scope-boundary`, `constraints-assumptions`, `decisions`, `acceptance-criteria`, `non-goals`; authority rule "spec is the master; `authority_chain[0]` is the spec". A **product** spec (jobs-to-be-done, outcome metrics, market framing).
- **parallel-development's Intent Blueprint** (`references/intent-blueprint.md`): UC (Use Cases) + AC (BDD Given/When/Then, each → an executable test) + NFR. A **technical / acceptance** spec — `references/scope.md:36` states explicitly it is "a technical/acceptance PRD, not a product PRD (no market, personas, business value)".
- **AC shapes differ**: blueprint-crafting's `acceptance-criteria` is product-level; the Blueprint's AC is BDD-executable (maps to tests). Same concept, different level.
- **Partial overlap only**: some spec anchors have no Blueprint counterpart (`desired-outcome-metrics`, `decisions` are product-strategic); the Blueprint's executable-test mapping has no spec counterpart.

So "collapse" ≠ "alias". It = the Blueprint is **derived** from the spec (seed + refine), turning the "two parallel authorities" concern into one authority chain (spec → Blueprint → code).

## Decision

**D1 — Seed, don't alias: on the rich path, parallel-development's Phase 0 derives the Intent Blueprint from blueprint-crafting's spec, not from the raw request.**

- When blueprint-crafting's spec is present in the queue's `authority_chain` (rich path), parallel-development's Phase 0 locates the spec entry in the chain — the product-intent source for the AC / UC / NFR seeds — wherever it sits (the chain is already carried per charter R5 and the arch-design authority flow; the schema orders `spec > blueprint > summary > companion`, but arch-design's relative rank is governed by per-type rules, so pd locates the spec rather than assuming `authority_chain[0]`) — and derives the Blueprint:
  - spec `acceptance-criteria` → Blueprint AC, refined into BDD Given/When/Then (each → an executable test).
  - spec `jtbd` + `scope-boundary` → Blueprint UC.
  - spec `constraints-assumptions` → Blueprint NFR.
  - spec `non-goals` → Blueprint scope (explicit exclusions).
  - spec `desired-outcome-metrics` + `decisions` → authority context parallel-development references but does NOT replicate (no Blueprint counterpart).
- The Blueprint remains parallel-development's technical / executable artifact; blueprint-crafting's spec remains the product artifact. The Blueprint is a **derivative** of the spec, not an alias. parallel-development still does the refinement work (product AC → BDD → test mapping).
- This collapses the **authority** (one source: the spec), not the **artifacts** (they stay distinct, in a derivative relationship). One authority chain (spec → Blueprint → code), not two independent ones.
- Degrade: no spec in the chain (free path) → parallel-development derives the Blueprint from the raw request, unchanged (today's behavior). Spec present but a seed anchor missing → parallel-development derives what it can + a coverage note.

## Why

- Resolves the charter ODP-1 concern (two parallel authorities): the spec becomes the single source; the Blueprint is its executable projection. parallel-development no longer re-imagines product intent blueprint-crafting already converged.
- Derivation (not aliasing) respects that the artifacts are genuinely different kinds (product vs technical): an alias would either push product content (`jtbd`, metrics) into the Blueprint (which `scope.md:36` says it is not), or strip product content from the spec.
- Rich-path-only: free-path behavior unchanged (charter R2); parallel-development does not hard-depend on blueprint-crafting (charter R1).

## Rejected

- **Full alias (Blueprint = spec).** Wrong kind: the spec is a product spec; the Blueprint is a technical/acceptance spec (`scope.md:36`). Aliasing conflates product-level content (`jtbd`, `desired-outcome-metrics`) with executable-level content.
- **Identical AC (no refinement).** blueprint-crafting AC is product-level; Blueprint AC is BDD-executable. The refinement (product AC → BDD → test) is real work an alias would skip, losing the executable-test mapping that is the Blueprint's purpose.
- **Keep re-deriving the Blueprint from the request (today's behavior).** Loses blueprint-crafting's converged product intent → divergence risk (the charter ODP-1 concern, left unresolved).
- **Push the Blueprint upstream into blueprint-crafting.** Violates blueprint-crafting's scope (it produces upstream artifacts, not the execution anchor; the Blueprint is parallel-development's Phase-0 freeze) and the executable-test mapping belongs to parallel-development.

## Required follow-ups (out of scope)

- The spec-anchor → Blueprint-component mapping is a Phase-0 derivation rule — implementation (parallel-development's Phase 0 / Planner).
- parallel-development's Phase 0 reading blueprint-crafting's spec from the `authority_chain` (locating the spec entry, not assuming `authority_chain[0]`) on the rich path — implementation (the spec is currently opaque authority context).
- A coverage-note path when a seed-source anchor is missing — implementation.

## Coverage notes (workspace rule 3)

1. IMPLEMENTED in code (agent instruction) — Phase 0 now seeds the Blueprint from bc's spec on the rich path (`d18ccfc`); on the free path it still derives from the request (`references/scope.md:36`). The seeding fidelity is an outer-ring/eval concern (the Planner is an LLM act).
2. The derivation mapping is illustrative; exact anchor → component rules are TBD at implementation.
3. This is rich-path-only; free-path Blueprint derivation is unchanged.

## Convergence log

- **Doc iteration 1** — wrote v1; review found D1 said "read the spec via `authority_chain[0]`", but `authority_chain[0]` is the queue artifact's own master (iteration-plan → arch-design; not always the spec). The spec is locatable IN the chain (the schema orders authority `spec > blueprint > summary > companion`), not necessarily at `[0]`. Fixed: D1 reads the spec by locating it in the `authority_chain`, conditioned on the spec being present in the chain; the degrade was updated to "no spec in the chain". markdownlint clean (exit 0).
- **Doc iteration 2** — found an overclaim: D1's parenthetical said "where a spec is present it is the master authority", but arch-design can outrank the spec in arch-centered chains (its rule is "arch-design wins on conflict"; the schema ordering line `spec > blueprint > summary > companion` does not even list arch-design). Fixed: dropped the "master authority" claim; reframed as "pd locates the spec (the product-intent source) wherever it sits, rather than assuming `authority_chain[0]`". markdownlint clean (exit 0).
- **Doc iteration 3** — found a fix-induced inconsistency: D1 had been changed to "locate the spec in the chain, not assuming `authority_chain[0]`", but the Required-follow-ups bullet still said "reading the spec via `authority_chain[0]`" — contradicting D1. (Line 13's `[0]` is fine: it quotes the product-spec profile's own rule verbatim.) Fixed the follow-up to "locating the spec entry, not assuming `authority_chain[0]`". markdownlint clean (exit 0).
- **Doc iteration 4** — re-reviewed clean: markdownlint exit 0; all `authority_chain[0]` mentions now consistent (line 13 is the verbatim product-spec rule quote; lines 24 + 50 are the "not assuming `[0]`" caveats; the log entries are historical); Context claims re-verified (`constraints.json` product-spec anchors, `intent-blueprint.md` Blueprint shape, `scope.md:36` "not a product PRD", schema authority ordering); D1 / Why / Rejected / follow-ups internally consistent. No further issues found. **Loop closed.**
- **Doc iteration 5** — implementation-status sync: this design is now IMPLEMENTED in code (Phase-0 spec-seeding landed as agent instruction `d18ccfc`). Flipped the Status block + coverage note from "not implemented" to "IMPLEMENTED"; the seeding fidelity stays an outer-ring/eval concern (the Planner is an LLM act). markdownlint clean (exit 0). **Loop closed.**
