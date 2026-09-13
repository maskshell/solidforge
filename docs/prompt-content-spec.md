# Prompt Content Specification (solidforge workspace)

> spec-version: 2 (2026-09-14 — D5 promotion landed: L4 → workspace rule 14, L6 → rule 15; v1 was the 2026-09-13 csr-terminal text)
> Status: process-axis spec. Authored via blueprint-crafting (sidecar `.plan-model.json` / `.queue.md` / `.run-record.json`; process_converged=true via 3-round outer ring). Cross-reviewed via cross-source-review: 9 rounds to the human-extended cap (5→7→9), terminal honest stalemate — the formal 2-clean-round streak did not assemble (rounds 4–8 each carried exactly one blocker, all fixed on discovery; round 9 both legs clean); sidecar `.csr-record.json`. Content correctness stays outcome axis — human.
> Authority: this spec is the master for model-facing prompt artifact CONTENT in this workspace. Where a layer restates an existing written rule (L1 restates workspace rule 10 + the global Agent-Oriented Writing rule; L5 restates workspace rule 8), the CLAUDE.md rule wins on conflict — the restatement here is a convenience index, not a second truth source.
> Outcome axis: this spec governs process and content shape. It does NOT judge whether any prompt's strategy is correct. That stays human (`rightness: human_confirm_required`).

## Terms (gloss before use — every term below is used with exactly this meaning)

- model-facing prompt artifact: a file or generated text whose primary consumer at its point of use is an AI model. Tier-1 in the workspace's three-tier reader model.
- consuming model: the model that tokenizes the artifact at its point of use. May be same-family (Claude) or different-family (异源, e.g. DeepSeek / GLM / Qwen via a wrapper).
- routing surface: the part of an artifact an orchestrating model reads to DECIDE whether to invoke (skill / agent frontmatter description).
- execution body: the part an invoked model reads to DO the work (SKILL.md body, agent body, generated instructions).
- runtime-assembled prompt: prompt text a script composes at invocation time (wrapper prompt templates, per-round state injection — NOT token injection, which is settings materialization, see L6).
- mapping-routed agent: an agent selected by a deterministic row in `skills/parallel-development/references/role-agent-mapping.md` (11 agents, grep-verified 2026-09-13), not by description matching.
- workflow-routed agent: an agent named at a fixed pipeline step in its owning skill's instructions (the pipeline-step seats of psv = primary-source-verification, csr = cross-source-review, pas = prior-art-search, bc = blueprint-crafting), spawned every time that step runs — or conditionally within the step (bc's researcher: dispatched for multi-source web gathering only, bc ADR #13).
- dual-mode agent: an agent routable both ways (workflow step + ad-hoc description matching). web-claim-verifier is the current instance.
- NOT-for clause / negative boundary: the TERM is "NOT-for clause"; the grep-able MARKER STRING is "NOT for" (with a space — the hyphenated spelling does not occur in the governed artifact population, SKILL.md / agent description surfaces; this spec's own normative text uses the hyphenated form only as the term, never as the marker); "negative boundary" is the semantic routing-exclusion clause the marker instantiates. The semantic clause has several idiom spellings (see §6 audit finding 1: "Route here …", exclusive triggers); the L2 MUST binds the semantic clause, of which "NOT for" is the conventional SKILL-level spelling.
- codification status: written-rule (carried by a CLAUDE.md / SKILL.md rule), de-facto (pattern exists in files, no written general rule), experiential (carried by ADR / memory / run-records only).
- MUST / SHOULD / MAY: RFC-2119 strength. MUST violations are Blockers; SHOULD violations need a stated reason; MAY is genuinely optional.
- seat: a pipeline-step position AND the agent file that occupies it — the unit L3 binds, D4 grandfathers, and ODP-3 sweeps. A producer seat (e.g. researcher) occupies a pipeline step but sits outside L3's binding scope.

## 1. Jobs to be Done

When an agent session or a maintainer authors, edits, or reviews a model-facing prompt artifact in this workspace, they need one normative reference for what its content MUST / SHOULD contain — so that the artifact:

- parses reliably in the consuming model (enumerations extracted as intended, cross-references understood without loading the target);
- routes precisely (invoked when appropriate, declined with a named alternative when not);
- behaves inside a contracted authority (reports schema'd output, never edits, no stake, oracle declared);
- survives different-family consumers (delimiters, state lines, assembly determinism hold across model families);

without re-deriving the rules from scattered sources (CLAUDE.md sections, ADRs, dogfooding memory, agent-file exemplars).

Secondary JTBD: an auditor reading a converged prompt artifact can trace each normative statement to its enforcement locus (deterministic gate / advisory outer-ring / human) and its codification status.

## 2. Desired Outcome Metrics

Proxy metrics (process-axis; none claims the prompt is RIGHT):

- M1 parse reliability: enumeration extraction fidelity — N bullets yield N extracted items, no middot-join loss. Spot-checkable deterministically; not currently gated.
- M2 routing precision: mis-triggered / missed skill invocations trend down. Baseline instrument: none exists — the activation-side gate asserts the description surface only (bc ADR #8) — aspirational, advisory.
- M3 behavioral uniformity: the review/verification seat family converges on the canonical clause set (§5 L3) — grep-able, no silent variants.
- M4 cross-family robustness: different-family legs degraded by prompt-drift (state-line bloat, un-delimited quotes, assembly errors) trend to zero incidents. Baseline instruments, split by carrier: degraded rounds → the convergence-record's per-round `hetero_degraded` boolean (aggregated across rounds[] for a trend); malformed incidents → the run-progress sidecar's hetero-leg-end outcome (plus the wrapper's fingerprint + rewrite rounds). Advisory.
- M5 codification coverage: layers carried as written-rules rises over time (audit §6 is the baseline; promotion per §7 D5).

## 3. Scope Boundary

Three-tier reader model (the boundary THIS spec draws its scope from):

- Tier 1 — model-facing (IN SCOPE): SKILL.md files, `references/*` docs (rule 10's own class), agent definition files (`agents/*.agent.md`; the global rule's `agents/json/*.json` convention has no instances in this repo today), rule files (CLAUDE.md and `.graphiti.json` instantiated at repo root; AGENTS.md and `.mdc` are enumerated by the global rule with no instances in this repo today) and design/plan docs (`docs/*.md`, `skills/*/docs/*.md`) — the classes workspace rule 10 and the global Agent-Oriented Writing rule enumerate — plus two spec-added classes they do not enumerate: command prompt templates (`commands/*.md` — defensible via the global rule's "similar files consumed by AI" catch-all; the $ARGUMENTS channel is deterministically asserted by plugin_layout.py, ADR #66) and runtime-assembled prompt text with its builder functions / templates. Also tier-1 by the Terms test — which is the OPERATIVE rule when it and the class list diverge; the class list is illustrative, not closed: the model-facing templates under `skills/*/infra/templates/**` — whether model-FILLED (`intent-blueprint.template.md`) or model-READ verbatim (the L1-Constitution section template, appended as-is; `cold-start-patterns/*.md`, pattern slices an agent mirrors) — copied into consuming projects by `arm.py`, so both the repo copy and the armed project-side copy are in scope. The tool-config templates in the same directory stay OUT of tier-1: their primary consumer is a lint/scan tool, not a model. Two registries govern them (arm.py): ARCH_CONFIGS (clippy.toml, checkstyle.xml, .importlinter.ini, .dependency-cruiser.cjs, .swiftlint.yml, .golangci.yml — copied by per-language detection, no flag) and the `--scaffold-configs` registry EXTERNAL_CONFIGS (.vale.ini, .semgrep.yml, .spectral.yaml — copied only under the flag). A third copy path, the secrets placeholder `.env.solidforge.example` (copy_env_example), is human-facing — out of tier-1 by the master model-facing test.
- Self-placement: this spec is itself a tier-1 artifact (the rules-doc class) and follows its own L1.
- Tier 2 — human-facing (OUT): README, README.zh-CN, USER_GUIDE, USER_GUIDE.zh-CN, GitHub About. These MAY retain moderate formatting; their contract is human persuasion and completeness, not model parse reliability (workspace rule 5 — facade-doc sync is advisory, human-judged — governs their sync, not this spec).
- Tier 3 — dual-audience records (OUT): run-records, convergence records, psv/csr packets, violation logs. Contract: machine-parseable AND human-auditable. The record-auditability pipeline (2026-08-08) owns their shape.

Two further Terms-test-passing classes the globs above miss: produced blueprint artifacts (`docs/intent-blueprints/*.blueprint.md` — tokenized by the pd different-family wrapper as `{blueprint_ref}`) and prose contract docs under `skills/*/infra/` (e.g. csr's `hetero_doc_review.divergence.md`, a rule-7 copy-pattern trail registered by its disconnect_check). Prompt-adjacent but out of scope: hook scripts, gate code, registry JSON payloads (their contract is the schema, not prose). The prompt text a wrapper script composes at invocation is in scope (L6). Hook/gate EMIT text (violation logs, remediation guidance) is out of scope — its contract is the violation-log / run-record schema, and its deliberately multi-line remediation prose is exempt from L6's state-line rule.

## 4. Consumer Sub-Typing (who tokenizes what)

Tier 1 splits into three consumer kinds with DIFFERENT contracts:

- routing surface — consumer: an orchestrating model making an invoke/decline decision under uncertainty between neighbors. Contract §5 L2.
- execution body — consumer: the invoked model doing the work in a fresh context. Contract §5 L3 + L1 + L4.
- runtime-assembled prompt — consumer: possibly a different-family model via a wrapper subprocess. Contract §5 L6 + L1.

Dispatch-mode classification (verified 2026-09-13; 23 agents in `agents/`, partition checks out 11 + 7 + 1 + 4 = 23):

- mapping-routed (11): carry live rows in role-agent-mapping.md:
  - architect
  - backend-developer
  - code-reviewer
  - devops-engineer
  - documentation-writer
  - frontend-developer
  - graphiti-config-generator
  - ios-developer
  - requirements-manager
  - security-specialist
  - tester

  Routing burden lives in the mapping row. code-reviewer is here (pd Reviewer role, ADR #14; the row's security routing was updated per ADR #30 to defer dedicated security work to security-specialist) — its description is a secondary surface only.
- workflow-routed (7): named at fixed steps in their owning skills' pipeline text — bc: plan-reviewer, researcher; csr: doc-reviewer; psv: claim-extractor, claim-verifier; prior-art-search: novelty-claim-extractor, collision-verifier. Routing burden carrier per seat: SKILL.md step text for the bc/csr seats and for pas's novelty-claim-extractor (its SKILL.md NC-I2 step carries the full spawn directive; install.md repeats it); references/install.md pipeline text for psv's claim-extractor / claim-verifier (psv's SKILL.md carries no handle for these two seats — it does name web-claim-verifier for single-claim checks); pas's collision-verifier is the exception, label-carried in install.md (the step label names the verdict; the spawn convention lives in the pas dogfood record — promoting it to a spawn directive in install.md is the candidate follow-up, and this line is its only carrier).
- dual-mode (1): web-claim-verifier — two skills' pipeline text names the agent beyond a single fixed seat (csr reconcile moments inside the round loop; psv single-claim checks outside a full psv run), which is what makes its ad-hoc description path a first-class routed channel; the routing imperatives in other agents' descriptions (§6 audit finding 1) are one-sided negative-boundary instances on EXEMPT surfaces — not dual-mode (none of those agents is routable both ways; dual-mode stays 1-of-23; code-reviewer's description is likewise a secondary surface only, §4 mapping-routed).
- platform-flow-routed (4): ios-tester, playwright-test-generator / -healer / -planner — dispatched from platform flow references in parallel-development; no `Agent:` row of their own (the tester row's dispatch text names ios-tester, and the mapping's workflow line names the playwright-test-* chain).

L2 exemption boundary: mapping-routed, workflow-routed, and platform-flow-routed agents are exempt from the L2 description contract — a registry row, a fixed step, or a platform flow decides their spawn. A dual-mode agent's description SHOULD carry the negative boundary.

## 5. Constraints: The Six Principle Layers

### L1 — Parse-Reliability Layer (restates workspace rule 10 + global Agent-Oriented Writing)

- MUST: enumerations that a checker / registry / model extracts as items are bullet lists, one item per bullet. Never `·` / `+`-joined prose.
- MUST: one joiner convention per document. Do not mix `·`, `+`, and `-` as item separators (a consistent `-` joiner is conformant — rule 10's own wording).
- MUST: short declarative sentences. No parenthetical-within-parenthetical (verbatim quotations exempt). No em-dash chain carrying load-bearing logic — split into bullets or a table.
- SHOULD: prefer a table when each item carries two or more attributes (rule 10's own phrasing is preferential; a MUST over a preference predicate would be undecidable — workspace rule 4: a Blocker must be a real violation, never a guess).
- MUST: gloss inline any cross-reference not loaded in the same context (an agent without the referenced doc must still understand the sentence — e.g. "Fault 1 (user's real need ≠ team's understanding)").
- MUST: one term per concept. No alternating field-name / concept / colloquial for the same thing.
- SHOULD: state constraints as declarative rules addressed to the reader-model, not as narrative history.
- Scope note: L1 applies to ALL tier-1 artifacts including runtime-assembled prompts (the assembled text is what the different-family model tokenizes).

### L2 — Routing-Surface Layer (de-facto → this spec is its first written general carrier)

The description field is a routing contract, not a capability advertisement. For the surfaces this layer binds — SKILL-level routing surfaces, plus dual-mode agent descriptions (§4; the exemption carves these bounds) — it SHOULD be three-part:

- when to use: concrete trigger words + scenario enumeration (the positive surface).
- when NOT to use + where to route instead: name the neighboring skill/agent that owns the adjacent job. Negative boundaries carry the most routing information because the orchestrator's decision is "which of these neighbors", and exclusions resolve it.
- what it produces: one line stating the output artifact, so the orchestrator can predict downstream wiring.

- MUST: a review/spec-family skill description carries at least one NOT-for clause naming the routed-to neighbor. Scope: SKILL-level routing surfaces (the bound set: blueprint-crafting, cross-source-review, primary-source-verification, prior-art-search — all conformant at the §6 baseline). Agent descriptions are NOT bound by this MUST (§4 dispatch modes); a dual-mode agent's description SHOULD carry the negative boundary.
- SHOULD: the three parts appear in that order (trigger precision degrades when the negative boundary is buried).
- Evidence note: the four review/spec SKILL.mds (blueprint-crafting, cross-source-review, primary-source-verification, prior-art-search) carry NOT-for clauses today; parallel-development (implementation family) uses a trigger-rich style without NOT-for — acceptable because its neighbors all carry the exclusions pointing back at it.

### L3 — Behavioral-Contract Layer (de-facto with variant phrasings → canonical set defined here)

An execution body for an adversarial / verification / review seat MUST carry the clauses below, in two groups by seat semantics:

Core three — bind EVERY review/verification seat:

- schema-only output + no-edit: the agent reports schema'd findings ONLY and never edits or fixes the artifact under review.
- no-stake / fresh-context declaration: the agent did not author the artifact and has no stake in it.
- honest-disclosure duty: the agent MUST emit what it did NOT verify (coverage disclosure), never a silently green summary.

Adjudication two — bind seats that return verdicts against a fetched/read source:

- oracle declaration: state what adjudicates. Canonical form: "The fetched source TEXT is the oracle — not model recall." A verdict prompt without a declared oracle invites the model to fall back to recall.
- negative-authority (scope of judgment): state what the agent MUST NOT judge. Normative form (this spec's wording, not a verbatim extraction — carriers phrase it as "never judges whether … is right" at agent level and "Does NOT judge whether the doc is right" at SKILL level): "Does NOT judge whether the doc is right (outcome axis — human)." Model tendency is to over-claim conclusive judgment; the clause must be explicit.

- SHOULD: clauses use the canonical wording above (uniform terms survive grep audits and future gates; variants are how de-facto standards drift).
- Transition: the current agent inventory is grandfathered as a whole (§7 D4; conformance snapshot in §6). A new or touched seat MUST conform.
- Enforcement split: the OUTPUT side of this contract is deterministically shape-gated — the doc-findings-family schemas (`doc-findings.schema.json`, `collision-findings.schema.json`, bc's `review-findings.schema.json`) check findings shape, the outcome-axis bar, and evidence fields; the code-shaped sibling (`violation-log.schema.json`, reused by the pd different-family wrapper) gates findings shape only — `detail` stands in for evidence with no quote constraint, and there is no outcome-axis field (a code-side gap, stated per rule 3). The NO-EDIT clause is additionally enforced at the tool layer — `tools:` / `disallowedTools: Edit, Write, NotebookEdit` agent frontmatter (bc ADR #14); 9 agent files carry it (the 7 marker carriers + researcher + security-specialist). The remaining CLAUSE-PRESENCE side in agent files is grep-able advisory today — NOT a deterministic gate (coverage note; workspace rule 3: never silently green).

### L4 — Enforcement-Division Layer (experiential → first written carrier here)

- MUST: a tier-1 artifact MUST NOT re-state in prose a constraint that a deterministic gate already enforces WITHOUT an enforcement-locus declaration — a labelled re-statement ("X is enforced by gate Y") is the sanctioned form. Unlabelled duplication is the violation: two truth sources drift; drifted duplication is worse than silence.
- MUST: declare the enforcement locus in one line and spend the artifact's attention on the semantic residue the gate cannot check (cross-section story lines, abstraction appropriateness, exemplar fit).
- SHOULD: label each normative statement with its strength honestly (deterministically enforced / advisory / human-only) — mirroring workspace rule 4 (a Blocker must be a real violation, never a guess) and rule 3 (never silently green).
- Rationale: this is the inner-ring / outer-ring split applied to prompt content. The L1 Constitution section of workspace CLAUDE.md already performs the same split for red lines (codable → arch-contract gate; uncodable → listed in CLAUDE.md); L4 extends it from "where rules live" to "what prompts say".

### L5 — Placement Layer (restates workspace rule 8)

- MUST: every capability must be reachable at the decision-point doc a model reads at the point of need (progressive disclosure). A file existing elsewhere in the repo is NOT reachability.
- MUST: after any capability change, verify the FULL loading chain via the skill's checker (`disconnect_check.py` per skill), not just the file touched.
- Inherited enforcement: deterministic — every skill carries a disconnect_check gate (all five skills as of 2026-09-13: blueprint-crafting, parallel-development, cross-source-review, primary-source-verification, prior-art-search).

### L6 — Assembly-Discipline Layer (experiential → first written carrier here; dogfooding-lesson derived)

For runtime-assembled prompts (wrapper prompt templates, per-round state injection — NOT token injection, which is settings materialization per the bullet below):

- MUST: assembly is deterministic in-code construction (builder functions / committed templates), never hand-edited intermediate files. Committed provider settings live in version control (per-skill copies: `skills/parallel-development/infra/scripts/profiles/` and `skills/cross-source-review/infra/scripts/profiles/` — separate copies; workspace rule 7: mirror the closest exemplar, self-contained deployability).
- MUST: the assembled prompt is checked by an assert on its text, OR the covering spec declares a coverage note that only downstream shape-gates check the output (rule 3 applied to prompt assembly — assembly drift must not pass silently). Coverage note, current state (2026-09-13, verified): BOTH wrappers assemble the prompt in-code via an `adversarial_prompt()` f-string builder — pd `hetero_review.py` (holes: `{diff_ref}` / `{blueprint_ref}` / `{prior_block}` / `{round_no}`), csr `hetero_doc_review.py` (doc-shaped variant: `{artifact_ref}` / `{authority_ref}` / prior-findings / round). provider-template + token injection (`profiles/<provider>.json` + `ANTHROPIC_AUTH_TOKEN`) is the SETTINGS-materialization pattern both wrappers implement — it is not a prompt-assembly mechanism. NEITHER wrapper asserts the assembled prompt text; both rely on downstream output shape-gates only. Transition: the two current wrappers are grandfathered via this spec-side note until their first wrapper change — AC-7 arm c.
- MUST: state lines are minimal one-line summaries (claim-free; rewritten at every round spawn). Lesson source: the csr 17-round cap-hit run — carried in versioned form by pd ADR #67 and `docs/web-claim-verifier-proposal.csr-record.json` (r11/r12 status-line findings + the adopted spawn-time rewrite rule); any run-dir copy under workspace/ is volatile class (gitignored ephemera — present on the machine that ran it, absent on fresh checkouts) and is never the carrier.
- MUST: a verdict of `refuted` / `narrowed` grounded in a quote from model recall instead of fetched text is INVALID and downgrades to `unverifiable` (the fetched-QUOTE invariant; canonical carrier: `agents/web-claim-verifier.agent.md`). SHOULD: quoted source text carries explicit delimiters when embedded in assembled prose (a JSON schema field — the carrier's own `quote` slot — satisfies grounding without literal delimiters; delimiters bind free-form prompt text).
- MUST: the assembled prompt assumes a different-family consumer by default — no reliance on same-family implicit habits; delimiters, schemas, and instructions are written out in full.
- SHOULD: bounded-observable invocation (turn caps, heartbeat, byte circuit-breaker, budget backstop) rides the wrapper harness per ADR #52 / ADR #41 — the prompt text itself stays lean; bounds are the harness's job, not prose the model reads.

## 6. Codification-Status Audit (baseline 2026-09-13)

Re-derivation commands (run from repo root; the counts below are distilled from their output — the block was executed literally on macOS BSD grep 2026-09-13 by the orchestrator and all counts reproduce; the counts were also independently re-derived by the review legs across rounds and reproduce — the BSD execution itself and per-leg tool choices are session-carried, not repo-carried):

- `grep -l "NOT for" skills/*/SKILL.md`
- `grep '^Agent: .solidforge:' skills/parallel-development/references/role-agent-mapping.md | sort -u` (POSIX-safe; the unscoped `^Agent: ` also matches one harness `Plan` row that has no file in `agents/` — 11 solidforge rows + 1 Plan)
- `grep -l "never edits or fixes" agents/*.agent.md`
- `grep -l "is the oracle" agents/*.agent.md`
- `grep -nF ".replace(" skills/parallel-development/infra/scripts/hetero_review.py` (0 hits)
- `grep -n "def adversarial_prompt" skills/*/infra/scripts/hetero*.py`
- `ls skills/*/infra/test/disconnect_check.py`
- `grep -l disallowedTools agents/*.agent.md` (the 9 tool-layer no-edit carriers)
- `ls agents/*.agent.md | wc -l` (the 23-agent denominator)
- `grep -iEl 'read-only|reports findings, does not fix' agents/*.agent.md` (locates the read-only-PHRASED carriers — 8 files; NOT a variant-carrier census). Membership:
  - the 6 no-edit marker carriers
  - web-claim-verifier (read-only phrasing, `agents/web-claim-verifier.agent.md:10`)
  - security-specialist
- Variant-carrier census note: security-specialist comes from the grep above; researcher's variants (no-stake framing, "did NOT author") need their own pattern — no single-command census covers both.

| Layer | Current carrier | Status | Enforcement locus |
|---|---|---|---|
| L1 parse | workspace CLAUDE.md rule 10 + global Agent-Oriented Writing | written-rule | advisory (not gated; lint-family check possible) |
| L2 routing | 4 review/spec SKILL.mds carry NOT-for; agent descriptions: 3 named-neighbor routing idiom instances + 1 exclusive-trigger (see audit finding 1) | de-facto | partial-deterministic — bc trigger_check.py's four strict assertions (PARALLEL-DEV REACHABLE skips with a note when parallel-development is absent) include the SKILL-body Scope Guard (a routing-away boundary naming the neighbor, strictly asserted); description-level NOT-for presence is unasserted (bc ADR #8 seam; verification level: the literal "NOT for" marker greps clean across all five skills' self-test suites — 2026-09-13; the route-here/instead-of/spawn-only idiom family has one known in-suite occurrence, bc activation.json's own registry comment "(route here)", so an idiom-presence assertion would need comment/string exclusion first; an indirect semantic assertion would need a suite-level review to rule out). Dual-mode SHOULD baseline: 0-of-1 — web-claim-verifier's description carries no negative-boundary idiom (grep-verified). SHOULD-order status: 0-of-4 bound descriptions put the negative boundary before the produces line (bc and csr lead with produces); retained — reordering live triggering surfaces is a behavior change that rides the D4 touch-trigger, not a doc edit |
| L3 behavioral | 7-of-23 two-marker union + 2 variant carriers + 1 zero-marker gap (snapshot caveat below) | de-facto, variant phrasings | output side shape-gated; no-edit clause tool-layer enforced (disallowedTools frontmatter, bc ADR #14, 9 carriers); remaining clause presence advisory |
| L4 enforcement-division | workspace CLAUDE.md rule 14 (promoted 2026-09-14, D5) + this spec §5 L4 | written-rule | advisory (semantic) |
| L5 placement | workspace CLAUDE.md rule 8 | written-rule | deterministic (disconnect_check in all five skills) |
| L6 assembly | workspace CLAUDE.md rule 15 (promoted 2026-09-14, D5) + this spec §5 L6; ADR #41 / #42 / #52 / #67 carry the lessons | written-rule | partial (assembly deterministic by construction; no assert-on-prompt-text — coverage gap stated in §5 L6) |

Audit findings:

- "NOT for" appears in 4 SKILL.md files (bc, csr, psv, prior-art-search). parallel-development (implementation family) uses a trigger-rich style without NOT-for — acceptable because its neighbors all carry the exclusions pointing back at it. In `agents/*.agent.md` the literal string "NOT for" has zero occurrences, but description-level negative boundaries DO exist via other idioms — named-neighbor routing in ios-developer ("Route here instead of general-purpose"), ios-tester (description: "route here only for UI/E2E", restated in its body), security-specialist ("Route here (not code-reviewer)"); plus a weaker exclusive-trigger clause in researcher ("Spawn only for multi-source web gathering"). Re-derive with `grep -iEl 'route here|instead of|spawn only for' agents/*.agent.md` (ERE, POSIX-portable; one known false positive: playwright-test-healer's "instead of hardcoded sleeps").
- L3 clause conformance snapshot (grandfathered baseline for D4 / ODP-3 / M3):
  - Two-marker union (no-edit marker "never edits or fixes" ∪ oracle marker "is the oracle"): 7 agents — claim-extractor, claim-verifier, collision-verifier, doc-reviewer, novelty-claim-extractor, plan-reviewer, web-claim-verifier. (6 carry the no-edit marker; 3 carry the oracle marker; overlap: claim-verifier + collision-verifier.) This is a marker-membership count, NOT a per-clause conformance baseline: 3 of the 5 clauses (no-stake, honest-disclosure, negative-authority) are unmeasured here; the per-clause baseline is ODP-3's sweep scope. web-claim-verifier sits in the union via the oracle marker; its no-edit clause is a phrasing variant ("Read-only: report, never edit or fix").
  - Variant carriers outside the strict union: security-specialist (no-edit variant "Read-only — reports findings, does not fix"); researcher (no-stake producer framing + a negative-authority variant "Never judges conclusion truth — outcome axis, human only" — a producer seat, not a review seat).
  - The real gap: code-reviewer — a live review seat (mapping-routed, pd Reviewer role) — carries zero canonical clauses; its one adjacent line is the ADR #38 honest-ceiling disclosure (a variant of the honest-disclosure duty only).
- NOT a clean generational split: clause coverage tracks the doc/claim-verification pipeline families (bc/csr/psv/pas seats), not seat seniority or review-ness in general — code-reviewer is the counterexample on the review side.
- Wrapper assembly (both verified in-source): prompt built by in-code `adversarial_prompt()` f-string builders; zero `.replace(` calls in the pd wrapper; settings materialized via provider-template + token-injection in both; no assert-on-prompt-text in either (§5 L6 coverage note).

## 7. Decisions

- D1 — Spec scope is tier-1 only. Facade docs (tier 2) and dual-audience records (tier 3) keep their own contracts. Why: each tier's failure mode differs (persuasion / auditability vs parse reliability); one spec for all three would compromise each.
- D2 — Consumer sub-typing adopted (routing surface / execution body / runtime-assembled). Why: the consuming model and its decision differ per surface; a single content contract under-specifies routing and over-specifies prose docs.
- D3 — L2's description contract binds SKILL-level routing surfaces; mapping-routed, workflow-routed, and platform-flow-routed agents are exempt; a dual-mode agent's description SHOULD carry the negative boundary. Why: a registry row, a fixed pipeline step, or a platform flow decides those spawns — duplicating negative boundaries into their descriptions creates drift surfaces for zero routing value. Rejected: requiring all 23 agent descriptions to carry NOT-for clauses.
- D4 — The current agent inventory is grandfathered against L3 as a whole (conformance snapshot §6); a new or touched seat MUST conform; canonical wording lands incrementally (rule 7 — mirror the closest exemplar — applied per touch). Why: a same-day mass rewrite violates commit granularity and carries review cost with no behavioral delta; and the corrected inventory (7 strict carriers + security-specialist's variant + code-reviewer's zero-marker gap = 9 L3-bound seats; researcher is a naming-alignment carrier outside the binding scope) corrects the first draft's hand-list — same cardinality, different membership. Rejected: grandfathering only a hand-picked agent list.
- D5 — L4 + L6 promotion to workspace CLAUDE.md rules is DEFERRED until this spec has ≥1 completed dogfood cycle (a real prompt authored or reviewed against it). Why: experiential layers earn rule status by surviving contact with a real artifact; promoting pre-evidence repeats the failure mode rule 6 exists to prevent (reverting a choice without re-deriving its rationale). This spec is the carrier meanwhile. **Promoted 2026-09-14**: L4 → workspace rule 14, L6 → rule 15 — the dogfood-cycle condition was satisfied by this spec's own convergence run (bc 3-round outer ring + csr 9 rounds; every L1/L6 principle was exercised against the author's own drafting).
- D6 — Assembly discipline requires assert-on-prompt-text OR a declared coverage note (rule 3 applied to L6). Why: both current wrappers rely on downstream shape-gates only; naming that honestly is cheaper than a retrofit gate now and keeps the gap visible instead of silently green.

## 8. Acceptance Criteria

Enforcement locus declared per AC (deterministic / advisory / human); seams named where a real public boundary exists.

- AC-1 — spec-surface: this spec states the tier boundary (§3) and consumer sub-typing (§4). Enforcement: advisory (outer-ring review checks presence and coherence). — seam: none (workspace-level doc).
- AC-2 — L1 conformance: a tier-1 artifact under review extracts its enumerations as bullets with one joiner. Enforcement: advisory (human/outer-ring spot check); NOT a deterministic gate today (coverage note).
- AC-3 — L2 conformance: every review/spec-family skill description carries ≥1 NOT-for clause naming the routed-to neighbor (bound set: bc, csr, psv, prior-art-search — all conformant at the §6 baseline). Advisory tracking: dual-mode agent descriptions carry the negative boundary (baseline 0-of-1, §6 L2 row). Enforcement: partial-deterministic — bc trigger_check.py's four strict assertions (PARALLEL-DEV REACHABLE skips with a note when parallel-development is absent) cover the positive surface (positive coverage, no-positive-steal) AND the SKILL-body Scope Guard (routing-away with the neighbor named); description-level NOT-for presence remains unasserted (the positive-trigger-vs-routing-negation seam, bc ADR #8; see the §6 L2 row for verification level).
- AC-4 — L3 conformance: a review/verification seat body carries the core three clauses (adjudication two additionally when the seat returns verdicts against a source); output conforms to its findings schema. Baseline snapshot §6 is grandfathered (D4). Enforcement: output side deterministic (shape-gates); clause presence advisory (grep-able).
- AC-5 — L4 conformance: a tier-1 artifact contains no prose re-statement of a deterministically-gated constraint without an enforcement-locus declaration. Enforcement: advisory (semantic — the duplication judgment is not grep-able).
- AC-6 — L5 conformance: capability changes pass the per-skill disconnect_check. Enforcement: deterministic (existing gates). — seam: skill-checker CLI.
- AC-7 — L6 conformance, three arms: (a) a wrapper asserts its assembled prompt text, or (b) carries the §5 L6 coverage note in/referenced-by its template header, or (c) is grandfathered — conforming via the spec-side §5 L6 note until its first wrapper change. The two current wrappers sit in arm c, mirroring D4's whole-inventory grandfathering idiom. Enforcement: advisory today (the coverage note itself is the honest artifact; a future gate could grep for it — recorded as ODP-2).

## 9. Non-Goals

- NOT a human-doc style guide (tier 2 keeps moderate formatting per its own contract).
- NOT an enforcement-machinery build-out: this spec maps enforcement loci; it mandates no new gates (ODP-2 records the candidate).
- NOT outcome-axis: never judges whether a prompt's strategy is correct — process and content shape only.
- NOT a retroactive mass rewrite of the current agent inventory (D4 whole-inventory grandfathering; conformance snapshot §6).
- NOT a prompt-engineering tutorial (no chain-of-thought recipes, no few-shot styling guides) — content CONTRACT, not technique.

## 10. Open Decision Points

- ODP-1 (RESOLVED 2026-09-14): the D5 promotion landed — L4 → workspace rule 14, L6 → rule 15, after this spec's own convergence run satisfied the dogfood-cycle condition.
- ODP-2 (deferred): promote AC-7's coverage-note grep into a deterministic wrapper gate (assert-on-prompt-text or note-presence check). Candidate home: the owning skill's self-test set. Blocked on ODP-1 sequencing and on ≥1 wrapper change touching assembly.
- ODP-3 (deferred): unify L3 clause wording across the seat family (7 strict carriers + 2 variant carriers + code-reviewer's zero-clause gap; snapshot §6). Lands incrementally per D4's touch-trigger; a dedicated sweep is a separate work item with its own convergence run.

## 11. Authority Chain and References

- authority_chain: [this spec, workspace CLAUDE.md, global ~/.claude/CLAUDE.md, skills/parallel-development/references/design-decisions.md, skills/blueprint-crafting/docs/design-decisions.md].
- conflict_rule: for restated layers (L1, L5) the CLAUDE.md rule wins; L4 and L6 are co-carried by workspace rules 14/15 since the 2026-09-14 promotion — the CLAUDE.md rule wins on conflict, this spec is the elaboration; L2 and L3 remain spec-mastered until their own promotion.
- ADRs cited (pd = parallel-development, bc = blueprint-crafting; per-skill numbering — each skill's design-decisions.md numbers its own):
  - pd #14 (Reviewer = code-reviewer, the pd Reviewer role)
  - pd #30 (security-specialist outer-ring-only; the Code Reviewer row's security routing defers to it)
  - pd #38 (honest same-family ceiling)
  - pd #41 (degradable substrate errors)
  - pd #42 (budget-honesty, amended by #52)
  - pd #52 (--max-turns knob, bounded observability)
  - pd #66 ($ARGUMENTS channel guard in commands/*.md)
  - pd #67 (web-claim-verifier; its csr-record carries the 17-round run incl. the state-line rule)
  - bc #8 (the activation-boundary test asserts the description surface, not a deterministic router)
  - bc #13 (researcher: dispatch only for multi-source web gathering)
  - bc #14 (agent tools:/disallowedTools tool-layer enforcement)
- Verified evidence (2026-09-13): grep counts and file lists in §6; wrapper construction facts in §5 L6.
