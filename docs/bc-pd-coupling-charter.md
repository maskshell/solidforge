# blueprint-crafting ↔ parallel-development — Coupling Charter

> Status: **Prescriptive business rules (the "should"), not a description of current code.** Derived from a design discussion (see convergence log) and grounded in the workspace's agent-first philosophy. Where a rule is not yet met by the current code, it is noted in the table below; the companion analysis doc holds the descriptive "is" state and the gap detail. This charter is the authoritative statement of how the two skills SHOULD couple. Open decisions forced by the charter are recorded as ODPs, not hidden.
>
> Companion docs: [blueprint-parallel-handshake-analysis.md](blueprint-parallel-handshake-analysis.md) — descriptive current-state analysis; [rich-path-design.md](rich-path-design.md) — design resolving R4 form + ODP-3 (the freeze→queue seam, resolved at design level); [odp2-verdict-design.md](odp2-verdict-design.md) — design resolving ODP-2 (consume the verdict as provenance + carry ODP resolution, resolved at design level); [odp1-blueprint-collapse-design.md](odp1-blueprint-collapse-design.md) — design resolving ODP-1 (seed the Intent Blueprint from the spec, resolved at design level). All three ODPs are now IMPLEMENTED in code (rich-path units 1-7 + emission wiring, commits `729fec2`…`a8f4cc6`); the end-to-end branch is agent-orchestrated.

**File-reference convention** — paths relative to the skill root. **Dir convention**: `docs/*.md` = blueprint-crafting; `references/*.md` = parallel-development. Under blueprint-crafting: `SKILL.md`, `plan-model.schema.json` (cited as `schema:`), `docs/design-decisions.md` (ADR log), `docs/arch-design.md`. Under parallel-development: any `references/*.md`, `infra/scripts/plan_queue.py`. **Same-name caveat**: both skills ship a `SKILL.md`, a `design-decisions.md`, AND a `run-record.schema.json` (`infra/schemas/`); bare `SKILL.md` = blueprint-crafting's; ADR citations point to blueprint-crafting's `docs/design-decisions.md` (parallel-development's `references/design-decisions.md` is a separate, unrelated log). This is the canonical legend for the doc set; the design docs cite it as "same as the charter".

## Premise P (governing) — the consumer is an AI Agent

blueprint-crafting's output artifacts are produced for **AI-agent consumption as the first and only important priority**. Human readability is **not a design constraint**; when it conflicts with agent parseability, the human loses.

Grounding:

- workspace global rule "Agent-Oriented Writing" — "Write with AI agents as the primary reader... not optimized for human readability."
- workspace rule 10 — "Write skill docs for the AI agent as the first reader... optimize for parse reliability, not human prose flow."
- blueprint-crafting `docs/arch-design.md:10` — artifacts are "for `parallel-development` to consume"; parallel-development is itself an agent skill. The documented consumer is already an agent.

This premise extends the workspace's agent-first principle from **docs** to blueprint-crafting's **output artifacts** (spec / arch-design / iteration-plan / executable-summary / research). It is a governing business rule, consistent with but extending the documented philosophy.

**Key consequence — convergence is trust scaffolding for an agent consumer.** An agent cannot judge outcome (rightness) any more than blueprint-crafting can; the convergence verdict (`process_converged` + constraints-profile) is the deterministic signal that lets an agent consumer use the artifact without re-validating its quality. Convergence exists for the agent consumer, not the human. (This is a derivation from Premise P + the process/outcome axis, not a separately documented decision.)

## The charter (6 rules, 3 tiers)

### Tier 1 — Coupling mode (foundational, non-negotiable)

- **R1 — Independence.** Both skills run standalone; neither is a build-time or run-time dependency of the other. They are two skills, not one.
- **R2 — Free input.** parallel-development accepts any reasonable plan-shaped input, not constrained to blueprint-crafting's format.

### Tier 2 — Producer obligation (what blueprint-crafting owes)

- **R3 — Agent-consumable + structural handoff.** blueprint-crafting produces structured, agent-parseable artifacts, with convergence as the agent trust scaffolding, and guarantees a structural handoff contract (the executable subset: `item_id / seq / depends_on / dod_ref`) so its designated consumer parallel-development can execute them. parallel-development is the consumer with a structural contract, not the only conceivable consumer.

### Tier 3 — Consumption principle (how parallel-development treats the handoff)

- **R4 — Dual-mode consumption (the reconciler).** parallel-development detects whether the input is a blueprint-crafting artifact; if so it takes the **rich path** (consume blueprint-crafting's fields faithfully); otherwise the **free path** (re-normalize arbitrary input). The rich path degrades gracefully to the free path. This is the mechanism that lets R5 (consume all) coexist with R2 (free input).
- **R5 — Full consumption (typed).** On the rich path, every blueprint-crafting output is consumable by parallel-development — but consumption is typed, not uniform: execution-queue artifacts (iteration-plan / executable-summary) → execute; arch-design → conflict-arbitration authority; spec → product-intent authority; research → inform implementation. "Consumable" = parallel-development has a way to use it; it does not mean every field drives execution equally.
- **R6 — Faithful consumption.** On the rich path, parallel-development may re-shape inputs for its own design, but preserves blueprint-crafting's information — carry all fields, utilize where relevant, do not silently discard. This specifically includes the convergence verdict `process_converged` (read as a trust/provenance signal, not an execution-correctness guarantee — necessary but not sufficient) and the resolved ODP state, because these were produced for agent consumers. Spec-completeness markers (anchors) are carried as trust/provenance, not as execution drivers.

## Decisions forced by this charter (ODPs)

Decisions the charter derived. All three are now IMPLEMENTED in code (rich-path units 1-7 + emission wiring, commits `729fec2`…`a8f4cc6`); follow the links for each decision + its commit.

- **ODP-1 — Blueprint collapse.** **Resolved at design level** — see [odp1-blueprint-collapse-design.md](odp1-blueprint-collapse-design.md). Decision: **seed, don't alias** — on the rich path, parallel-development's Phase 0 derives the Intent Blueprint from blueprint-crafting's spec (spec AC → BDD AC; jtbd/scope → UC; constraints → NFR), not from the raw request. The spec is a product spec and the Blueprint is a technical/acceptance spec (`references/scope.md:36`) at different AC abstraction levels, so they are NOT aliased — the Blueprint is a derivative, collapsing the **authority** (one source) not the artifacts. **Implemented** — Phase-0 spec-seeding landed as agent instruction (`d18ccfc`).
- **ODP-2 — Consume the convergence verdict + carry ODP resolution.** **Resolved at design level** — see [odp2-verdict-design.md](odp2-verdict-design.md). Decision: blueprint-crafting emits the spec run-record at freeze; parallel-development records `process_converged` as upstream provenance (a new optional run-record field), NOT a gate-skip (conservative default; opt-in only). Plus the projection carries blueprint-crafting's ODP `resolution` so parallel-development seeds resolved ODPs instead of re-asking. **Implemented** — verdict `upstream` field + emission (`117783e`, `a8f4cc6`); ODP `resolution` carry + seed (`729fec2`, `b2ff3a6`).
- **ODP-3 — Rich-path detection.** **Resolved at design level** — see [rich-path-design.md](rich-path-design.md). Decision: a per-item producer marker on the emitted queue; fail-safe to the free path (no YAML parser required). Also resolves R4's form (blueprint-crafting emits the projected queue at freeze; parallel-development reads it with its existing parser). **Implemented** — `freeze` operator emits the queue + run-record with the marker (`13b391b`, `f27ea11`); `detect_producer` (`73eb392`).

## Relationship to current code (prescriptive vs descriptive)

This charter is **prescriptive**. The companion analysis doc establishes the **descriptive** current state. R4–R6 are rich-path rules; the rich-path MACHINERY is now implemented in code (commits `729fec2`…`a8f4cc6`), but the end-to-end branch is AGENT-ORCHESTRATED — the Planner / orchestrator invokes `detect_producer` / `upstream-provenance` / Phase-0 seeding per `intent-blueprint.md` §Rich path + `plan-driven-mode.md`, not a deterministic coded branch. The rows below distinguish coded machinery vs agent-orchestrated vs not-yet-wired. (Detail and evidence in the analysis doc.)

| Rule | Current code |
| --- | --- |
| R1 independence | met (both skills standalone; loose coupling via artifact) |
| R2 free input | met (parallel-development re-normalizes any plan) |
| R3 agent-consumable + handoff | met on the executable subset; the structural contract is tested only from blueprint-crafting's side (`round_trip.py` runs in bc) |
| R4 dual-mode | machinery implemented — `detect_producer` (`73eb392`) + producer marker on the emitted queue (`f27ea11`); the detect→consume branch is agent-orchestrated |
| R5 full consumption | machinery implemented — `freeze` emits queue + run-record + research payload (`13b391b`); `upstream` field (`117783e` + `a8f4cc6`); spec→Blueprint seeding (`d18ccfc`, agent); research→inform via `read_research` **free-form** (accepts bc's `.research.json` OR any research doc — R2; not gated to bc's `{claims, sources}`); orchestrator surfaces content to the Coder. research-ref discovery is agent-level (authority_chain) |
| R6 faithful consumption | machinery implemented — ODP `resolution` carry (`729fec2`) + resolved-ODP seeding (`b2ff3a6`) + verdict as upstream provenance (`a8f4cc6`); no longer discarded on the rich path |

The rich-path machinery (R4 detection + emission; R5 research→inform; R6 carry + seed + provenance) is implemented. Remaining gap: the end-to-end rich-path branch is agent-orchestrated (the Planner/orchestrator invokes the pieces per `intent-blueprint.md` / `plan-driven-mode.md`), not a deterministic coded branch.

## Coverage notes (workspace rule 3)

1. This charter is derived from a design discussion, not from code. It is a target, not a status report.
2. Premise P extends the workspace's agent-first principle to blueprint-crafting's output artifacts; that extension is consistent with but not literally stated by the existing rules (which cover docs). It is adopted here as a governing premise.
3. All three ODPs are implemented in code (commits `729fec2`…`a8f4cc6`). The end-to-end rich-path branch is agent-orchestrated (not a coded branch), and research→inform (R5) is not yet wired — see the current-code table.

## Convergence log

- **Doc iteration 1** — wrote v1; review found and fixed the "Relationship to current code" table conflating free-path behavior with rich-path compliance: R5/R6 are rich-path rules, and since the rich path (R4) does not exist yet, they are strictly "not met", not "partially". Also fixed three precision points: R1 "copy-not-import" → "loose coupling via artifact" (copy-not-import is blueprint-crafting's mechanism only); R3 "single-sided-tested" glossed ("`round_trip.py` runs in bc"); authority_chain described as "preserved (re-derived from source)", not "carried" (parallel-development re-derives it in the free path). The summary line was re-pointed to "the rich path (R4), which gates R5 and R6". markdownlint clean (exit 0).
- **Doc iteration 2** — re-reviewed clean: markdownlint exit 0; all descriptive claims in the current-code table re-verified against source (R5/R6 free-path behavior, authority_chain re-derivation, verdict / research / resolved-ODP discard); citations re-checked (`docs/arch-design.md:10`, CLAUDE.md rules by name, design-decisions same-name caveat); rich-path scoping consistent across R4 / R5 / R6 and the table; ODPs open; carry-vs-utilize distinction consistent. No further issues found. **Loop closed.**
- **Doc iteration 3** — pointer update only (no rule or table changes): ODP-3 marked "resolved at design level" linking [rich-path-design.md](rich-path-design.md); companion links and the table intro updated to point at the rich-path design. Triggered by the rich-path design doc landing. The charter's rules and current-code table are unaltered (the code is unchanged — design-level resolution only). markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 4** — pointer update only: ODP-2 marked "resolved at design level" linking [odp2-verdict-design.md](odp2-verdict-design.md); companion links updated. Triggered by the ODP-2 design doc landing. Rules and current-code table unaltered (code unchanged). markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 5** — pointer update only: ODP-1 marked "resolved at design level" linking [odp1-blueprint-collapse-design.md](odp1-blueprint-collapse-design.md); companion links updated and now note all three ODPs are resolved at design level. Triggered by the ODP-1 design doc landing. Rules and current-code table unaltered (code unchanged). markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 6** — holistic (cross-doc) review of the 5-doc set: fixed stale claims that the ODPs were "unresolved / need design work" (the ODP-section intro + coverage note 3) — all three are resolved at design level; renamed the section "Decisions forced by this charter (ODPs)". Made this doc's file-reference legend the canonical complete one (added `run-record.schema.json` to the same-name caveat) because three design docs reference it as "same as the charter". Rules and the current-code table are unaltered. markdownlint clean (exit 0). **Loop closed.**
- **Doc iteration 7** — implementation-status sync (post-implementation review): the rich path is now IMPLEMENTED in code (commits `729fec2`…`a8f4cc6`); flipped the ODP entries + companion + intro + coverage note + the current-code table from "pending / not met" to "IMPLEMENTED" with commit refs, honestly distinguishing coded machinery vs agent-orchestrated vs not-yet-wired (research→inform). markdownlint clean (exit 0). **Loop closed.**
