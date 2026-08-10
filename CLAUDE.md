# Skills Workspace — Maintenance Rules

Applied when working in the `solidforge/` repository (the SolidForge skills workspace).
Governs how to update and optimize the skills here (under `skills/` — `parallel-development`, `blueprint-crafting`, `cross-source-review`, `primary-source-verification`; future skills follow the same pattern).
Complements — does not duplicate — the global `~/.claude/CLAUDE.md` (Agent-Oriented Writing, Self-Review, Agent Definition Conventions).
Both apply; this file adds the skill-update-specific rules.

Authoritative for: skill source, `infra/` (hooks/scripts/templates/tests), `SKILL.md`, `references/`, and the registries + automated checkers each skill uses to self-validate.

## 1. A skill's own self-gates are the definition of done

Before committing any skill change, the skill's deterministic self-tests MUST pass green.
A skill that dogfoods a deterministic inner ring must pass its own inner ring.
A change is not done while any fail. For `parallel-development/`:

```bash
python3 skills/parallel-development/infra/test/disconnect_check.py  # structure + loading-chain
python3 skills/parallel-development/infra/test/smoke_gates.py       # gate behavior
python3 skills/parallel-development/infra/test/lint_self.py         # skill lints its own infra
python3 skills/parallel-development/infra/test/arm_copy_config.py   # arch-config gating + arm idempotency
python3 skills/parallel-development/infra/test/arm_report_gates.py  # gate-status report + LSP advisory
python3 skills/parallel-development/infra/test/arm_revert.py        # --revert reversibility (keeps user edits)
python3 skills/parallel-development/infra/test/plugin_layout.py     # plugin.json + hooks.json + agents well-formed
python3 skills/parallel-development/infra/test/run_record.py
python3 skills/parallel-development/infra/test/plan_queue_detect.py  # rich-path producer-marker detection (fail-safe)
python3 skills/parallel-development/infra/test/hetero_review_wiring.py  # different-family wrapper ↔ loop_state + adversarial-stalemate round-trip (ADR #40)
python3 skills/parallel-development/infra/test/drift_check.py             # rule-7 boilerplate drift (advisory; design-pattern-review-value.md D3)
python3 skills/parallel-development/infra/test/adapter_shape_check.py     # *_adapter.py violation-log shape contract (blocker)
```

Run the relevant subset at minimum; run the full set before commit. Tests skip gracefully when external tools (cargo, mvn, npm, checkstyle) are absent.

## 2. Follow the maintenance doc + registry/checker; do not edit the checker

Before changing a skill, read its maintenance guide and single-source-of-truth registry. For `parallel-development/`: `references/extending.md` (the per-language formula, worked exemplar, disconnect checklist) and `infra/test/platforms.json` + `disconnect_check.py` (what must exist per language). They encode the exact formula.
Add a capability by updating the registry; never edit the checker to add a language or decision point.

## 3. Never silently green — state coverage gaps honestly

When a gate or tool cannot fully enforce something, emit an explicit `coverage` note and degrade to a documented no-op — e.g., "NOT enforced deterministically — outer-ring concern." Faking a green gate violates the contract the convergence loop depends on.
Applies to weak language tooling (Rust/Java layer-direction) and best-effort heuristics (API-contract shape matching).

## 4. Deterministic inner ring; heuristics are advisory, not Blocker

Codable rules become deterministic gates that Block on a real violation. Best-effort or heuristic checks (path-scan, mtime staleness, fuzzy matching) emit `warning`, never `blocker` — a Blocker must be a real violation, not a guess. Keep the uncodable semantic residue in the outer ring (LLM review) or the test gate (contract tests).

## 5. Adding a capability → update EVERY enumeration, then doc-audit

A capability ripples through ~9+ files. The recurring failure mode is updating the code and forgetting a table, caveat, or enum. After adding a language/gate/role/tool, grep for the capability's enumerations and update all of them:

- strength tables (`extending.md`), gate tables (`install.md` "What each gate does"), maturity caveats (`maturity.md`), domain enums (`golden-paths.md`), role triggers (`role-agent-mapping.md`), per-platform rows (`arch-contracts.md`).

Treat a doc-audit pass as a required step, not an afterthought.

## 6. Record an ADR for non-obvious decisions (Context / Decision / Why / Rejected)

Log contentious or non-obvious choices in `skills/parallel-development/references/design-decisions.md` with the rejected alternatives. Examples worth an ADR: advisory-vs-Blocker severity, detection-vs-registry-split, recursive-vs-shared-lib, flag-vs-block semantics. This prevents a future maintainer (or yourself) reverting a choice without re-deriving its rationale.

## 7. Mirror the closest exemplar; match the surrounding idiom

New code/docs match the nearest existing example: Rust gate → Java gate; `clippy.toml` → `checkstyle.xml`; `rust-patterns.md` → `java-patterns.md`.
Match comment density, naming, and the self-contained-script convention (each gate duplicates `run`/`have`/`emit`/`find_marker_dirs` rather than importing a shared lib, so each stays independently deployable). Do not introduce a new pattern when an existing one fits.

## 8. Explore before editing; preserve the loading chain

A skill's touch points span many files. Map the surface (Explore subagents, targeted greps) before changing, and verify the FULL loading chain after via the checker — not just the file touched. Every capability must be reachable at the decision-point doc a model reads at the point of need (progressive disclosure); a file existing somewhere is not enough. The checker enforces this; do not break it.

## 9. Commit only when asked; follow the repo's convention

Observe the existing commit format and message style. Here: `parallel-dev:` prefix, direct-to-main, descriptive body, `Co-Authored-By` trailer. Do not auto-commit or auto-push. One coherent commit per logical change.

## 10. Write skill docs for the AI agent as the first reader

This operationalizes the global `~/.claude/CLAUDE.md` "Agent-Oriented Writing" rule for the skill docs in this workspace (SKILL.md, `references/*`, design + plan docs).
A model tokenizing the doc is the primary reader — optimize for parse reliability, not human prose flow:

- Enumerations that are a checker's or registry's input unit → a bullet list, one item per line. Never `·` / `+`-joined prose. (A model extracts N items from N bullets more reliably than from one middot line; and the bullets map 1:1 to a future registry entry.)
- One joiner convention per document. Do not mix `·`, `+`, and `-` as item separators.
- Short declarative sentences. No parenthetical-within-parenthetical, and no em-dash chain that carries load-bearing logic — split it into bullets or a table.
- Gloss inline any cross-reference not loaded in the same context. An agent without the referenced doc must still understand the sentence — e.g. "Fault 1 (user's real need ≠ team's understanding)", "workspace rule 4 (heuristics are advisory, never Blocker)".
- Consistent terminology: one term per concept. Do not alternate field-name / concept / colloquial for the same thing — e.g. pick `process_converged` for the field, "process-axis convergence" for the concept; drop colloquial synonyms like "green".
- Prefer a table when each item has two or more attributes (field + meaning, risk + mitigation, anchor + where).

## 11. Skill-creator / eval workspaces live under `workspace/<skill>/`

skill-creator's default places its ephemera (iteration artifacts, snapshots, eval logs/results) at `<skill>-workspace/` as a sibling to the skill, which clutters the repo root.
In this workspace, redirect it to `workspace/<skill>/` instead — the sibling location is a tool default, not a contract. `workspace/` is gitignored, so the ephemera neither clutters the root nor gets committed. Apply this whenever running skill-creator (or any tool that drops a `<skill>-workspace/` sibling).

## 12. CodeGraphContext (CGC) — MCP code-graph queries

For call/inheritance/dependency questions that a graph query can answer, prefer CGC; do not infer relationships by guessing. For the tool list and parameters, rely on MCP's own descriptions — this rule covers usage strategy only.

### Division of labor and fallback

- Inter-symbol relations (calls, inheritance, imports, dependencies, call chains) → CGC graph queries
- Precise structural syntax patterns → ast-grep; plain-text existence checks → grep (baseline)
- Fallback chain: CGC → ast-grep → grep. CGC is only available when the repo is indexed; if unavailable, fall back and state that graph data was not used this run

### Usage constraints (things the schema won't tell you)

- Index before querying: for an unindexed repo use `add_code_to_graph` + `check_job_status`; re-index after major refactors or batch renames
- The graph is static analysis: reflection, string dispatch, and dynamic calls may be missed — verify critical paths against source
- Paths must be under the process cwd or `CGC_ALLOWED_ROOTS`; if a path is rejected, do not guess alternative paths — explain the limit and ask the user to adjust config
- Do not assert "no callers / no subclasses" without having queried the graph

### Troubleshooting

- If MCP is connected but results are clearly wrong: suggest the user run `cgc doctor` / `cgc list` in the terminal (shares the same `~/.codegraphcontext/` data as MCP); this rule does not require the agent to start the MCP service itself

## 13. Per-claim source verification (psv) — OPTIONAL additive tool, not a pipeline stage

`primary-source-verification` (psv) is an optional, additive outcome-axis tool — NOT a required step for any doc. The baseline pipeline (`csr → bc → pd`) is unchanged; psv is inserted only when it adds value.

**Reach for psv when ALL hold:**

- the doc makes **load-bearing** citation claims against **fetchable** primary sources (arXiv, Crossref, standards, repos) — not passing mentions;
- a wrong citation would **materially weaken** the argument (a design paper's thesis, a research doc's conclusions);
- sources are fetchable (paywalled/unfetchable → psv returns `unverifiable`, low yield).

**Skip psv (csr alone suffices)** when the doc is low-citation or interpretive-only (`M=0` → "no admissible surface"), the citations are low-stakes/well-known, or it is already verified.

**When used** (the reach conditions above hold — recommended-default, 2026-08-09), run psv TWICE: first as a cheap load-bearing-claims GATE before csr, then after csr as the authoritative full-M record: `psv(gate: load-bearing subset, GO/NO-GO) → csr → psv(full M) → (address refuted/narrowed; csr re-converge if restructured) → bc → pd`. The gate is a batch signal on the load-bearing claims only (NO-GO iff any is refuted or unverifiable, or ≥2 narrowed; bounded re-gate ≤2, not a debate loop); the gate record is explicitly NOT a coverage record — the full-M run after csr is the ONLY authoritative `oracle_verified_under_known_coverage`. The gate catches citation problems csr's recall-based legs share the model's blind spot on, before csr investment; csr catches structural gaps psv doesn't. Gate discriminator (ODP-5 resolved 2026-08-10): the gate's value concentrates on docs whose load-bearing citations are predominantly EXTERNAL (arXiv/blogs/standards — the recall blind-spot zone); for docs citing mostly local files (two known q≈0 samples), csr alone suffices. The gate defaults to LONG-tier docs (expected csr investment ≥ 3 rounds) — on short docs the gate cost (~1.5 rounds) exceeds the maximum saved investment (≤2 rounds), so it never pays there. When the reach conditions do NOT hold: csr alone suffices (`csr → psv → bc` unchanged). psv NEVER judges whether the doc is right (outcome-axis — human); its signal is `oracle_verified_under_known_coverage`, never `correctness_converged`. It dogfoods on its own and peer skills' design docs. See [USER_GUIDE § Two-axis doc convergence](USER_GUIDE.md).

## Self-review

After adding or modifying any file under this workspace, re-read the change against every rule above (plus the global CLAUDE.md) and verify compliance — especially rules 1, 5, 8, and 10, which are the ones most often missed.

## L1 Constitution (uncodable red lines)

Red lines that cannot be encoded as deterministic architecture-contract rules live here. These are Blockers: a violation returns the work for rewrite. Codable red lines (circular dependencies, layer isolation, concurrency baselines) are enforced deterministically by the inner Architecture-Contract Gate — do not duplicate them here; declare them in the project's arch-contract config (.importlinter.ini / .dependency-cruiser.cjs / .swiftlint.yml).

- Abstraction level must be appropriate: a helper must not leak domain logic into a generic utility, and a high-level policy must not reach into a low-level primitive directly.
- Naming must reflect intent, not implementation accident. A name that contradicts what the code does is a Blocker.
- No emergent coupling: two modules that are not explicitly wired must not secretly depend on each other's internal behavior or ordering.
- No "delete the error" fixes: removing a failing module, hardcoding a value to turn a test green, or wrapping logic in a bare catch to silence a failure are Blockers (the fast gate + blueprint diff catch most of these).
- All authentication/authorization that cannot be statically proven to flow through the unified gateway is a Blocker.

When a Reviewer flags one of these, the convergence loop treats it as an outer- ring Blocker and returns the change for rewrite — not a Warning.

## Deterministic Gate Toolchain

The convergence-loop gates degrade gracefully and never report a silent green when a tool is absent. To arm them on a new machine or in CI, restore/install the gate tools for the ecosystems this project uses:

- Python: `uv sync` — ruff / import-linter / pylint are in dev deps (uv.lock)
