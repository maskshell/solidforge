# Outcome-axis skill line — backlog

> Status: living backlog (updated 2026-08-01). NOT commitments. Records the outcome-axis skills behind readiness gates. State: **P1 BUILT** (Phase A converged + committed); **P2 BUILT** (Phase A converged 2026-08-01 — `collisions_under_known_coverage`); **P3 RESOLVED** (→ a csr mode, not a skill). The two-axis frame + rightness-tier mapping live in `skills/primary-source-verification/docs/proposal.md` §6 (and `skills/prior-art-search/docs/proposal.md` §5 for the two-outcome-leg span). Origin: evaluating arXiv:2607.13683 (GSME) against the spec-gaming paper (*Specification Gaming as an Orthogonal Failure Axis in Autonomous Coding Loops*).

## Frame

The skill family currently covers the PROCESS axis: `blueprint-crafting` (bc) authors and converges upstream artifacts; `cross-source-review` (csr) converges any doc-shaped artifact; `parallel-development` (pd) converges code. The OUTCOME axis (is the doc's content correct/novel/sound, not just well-formed) is opened by P1 (cited-source verification) + P2 (uncited-prior-art collision); P3 is resolved to a csr mode. None of these ever emits a convergence-to-truth boolean; the top-line outcome signal is `oracle_verified_under_known_coverage` (psv), `collisions_under_known_coverage` (prior-art-search), or `human_confirm_required` (spec-gaming paper §4.2).

## The outcome-axis skill line

| Skill | One-line contract | Status | Gate to earn a proposal |
| --- | --- | --- | --- |
| P1 `primary-source-verification` (psv) | extract atomic claims, fetch each cited primary source, emit per-claim verdict (verified/refuted/narrowed/unverifiable), output coverage disclosure | **BUILT** — Phase A converged (CSR + blueprint-crafting + parallel-development), committed 2026-07-31; live + dogfooded on 4 real docs | done (gate = its own convergence, met) |
| P2 `prior-art-search` | extract novelty claims, multi-source search (arXiv/web/repos), emit prior-art collision report + uncited-work + coverage disclosure; never `novel_confirmed` | **BUILT** — Phase A converged 2026-08-01 (CSR + psv-verified proposal + parallel-development plan-driven); `collisions_under_known_coverage` tier; 7 self-gates green, offline dogfood catches the canonical collision; live N≥3 dogfood (incl. ≥1 long doc) is the human acceptance criterion | gate met (worked example 2026-07-31): the search-to-collision loop on the spec-gaming paper surfaced uncited prior art (the "Verification Paradox" / "Self-Critique Paradox" framings) for its self-certification-paradox claim — a finding bc's forward-gather `researcher` would not produce. (Caveat: those sources need primary-source adjudication — psv's job, additive.) |
| P3 `argument-red-team` | per load-bearing claim emit attack vectors with a different-family leg for partial decoupling; red-team EVIDENCE only, never `soundness_converged` | **RESOLVED → csr mode, NOT a skill** | gate answered (2026-07-31): csr's different-family adversarial leg already does per-claim weakness-flagging; P3's only difference (per-claim attack-vector shaping) is a prompt mode, not a capability. Plus the cross-family-overlap finding (this session: cross-family shares correctness blind spots, arXiv:2607.08065) bounds P3's different-family leg to partial decoupling — no distinct ceiling. → reclassified as a csr prompt-mode (a structured per-claim attack pattern), not a 4th skill. |

Permanent non-goal (not Phase B, not ever a skill): **significance** — community judgment, human only. A skill may gather signals for the human; it does not verdict.

## Carried open questions (soundness weaknesses, unresolved)

- ~~P2 yield~~ RESOLVED (2026-07-31 worked example): real yield — the backward-collision hunt surfaced uncited prior art (Verification/Self-Critique Paradox framings) for the spec-gaming paper's self-certification claim, a finding bc's forward-gather `researcher` would not produce. Caveat: those sources need primary-source adjudication (P2's own job when built). The absence-of-evidence limit still caps the OUTPUT (never `novel_confirmed`), but the collision report itself has yield.
- ~~P3 identity~~ RESOLVED (2026-07-31): a csr mode, not a skill (see table).
- ~~P2 oracle strength~~ RESOLVED (2026-08-01, prior-art-search proposal §3 + design-decisions.md ADR #4): the searchable prior-art corpus is weaker than psv's fetched source at TWO layers (comparison-side + selection-side), not one; this is precisely why prior-art-search NEVER emits `novel_confirmed` and its top-line is `collisions_under_known_coverage` (a coverage disclosure, not a verdict).

## Decision rule

A skill earns its own proposal only when its gate clears, and converges on its own (one-skill-one-proposal; do not pre-commit unconverged designs). Outcome as of 2026-08-01: **P1 built**; **P2 built** (Phase A converged); **P3 resolved to a csr mode** (no proposal — it's a csr prompt-pattern, to be documented when adopted). The outcome-axis line = psv (built, cited-source verification) + prior-art-search (built, uncited-prior-art collision); the line did not contract to P1-only, but P3 dissolved into csr exactly as its gate predicted ("may dissolve").
