# Solid Forge

**English** | [简体中文](README.zh-CN.md)

*A Loop Engineering system for AI coding agents — bundled as one Claude Code plugin.*

A Claude Code plugin bundling the **converge → specify → implement** pipeline plus two additive **outcome-axis** layers (cited-source verification + uncited-prior-art collision): the `cross-source-review`, `blueprint-crafting`, `parallel-development`, `primary-source-verification`, and `prior-art-search` skills, their cascaded subagents, and the deterministic convergence-loop hooks — installable as one unit and enableable per project.

## What it bundles

- **Skills**
  - `parallel-development` — parallel-development orchestrator with a deterministic convergence-repair loop: dual-ring gates (fast gate + architecture-contract gate), state-machine circuit breaker, Intent Blueprint with read-only guard, micro-step snapshots, golden-path registry. Python, Swift, Web/TS, Rust, Java.
  - `blueprint-crafting` — produces convergence-checked upstream artifacts (PRD, arch-design, iteration plan, executable summary, research) that parallel-development consumes as authoritative references.
  - `cross-source-review` — drives same-family + different-family cross-review of a doc to substantive convergence; the convergence layer upstream of blueprint-crafting (a requirements input before bc, a design doc, a wiki page) and reusable standalone. Its convergence records embed per-round findings + per-finding dispositions (audit-ready — a reader can re-judge every finding and what was done about it).
  - `primary-source-verification` — read-only, source-grounded per-claim verifier: extracts atomic source-admissible claims, fetches each cited primary source, and emits a per-claim verdict (verified / refuted / narrowed / unverifiable) plus an honest coverage disclosure (`oracle_verified_under_known_coverage`). The outcome-axis complement to csr — additive, NOT a sequential pipeline stage; never `correctness_converged`. **GATE MODE** (2026-08): for rule-13 docs (load-bearing citations against fetchable sources), a load-bearing-claims subset runs BEFORE csr as a cheap GO/NO-GO premise check — gate record explicitly non-authoritative; the full-M run after csr is the ONLY authoritative coverage record.
  - `prior-art-search` — read-only, search-grounded per-novelty-claim collision detector: extracts a doc's novelty claims, searches the prior-art corpus for each, and emits a per-claim collision verdict (collision / uncited-relevant / clear-under-search / inconclusive) plus an honest coverage disclosure (`collisions_under_known_coverage`). The second outcome-axis leg — backward-UNCITED (psv is backward-CITED); additive, never `novel_confirmed`.
- **Agents** (22, plugin-scoped as `solidforge:<name>`) — architect, backend-developer, frontend-developer, ios-developer, ios-tester, tester, code-reviewer, requirements-manager, devops-engineer, documentation-writer, security-specialist, graphiti-config-generator, playwright-test-planner / -generator / -healer, plan-reviewer, doc-reviewer, claim-extractor, claim-verifier, novelty-claim-extractor, collision-verifier, researcher. Per-role code patterns live in `parallel-development/references/agent-patterns/`.
- **Hooks** — `fast_gate.py` (PostToolUse), `blueprint_guard.py` + `counters.py` (PreToolUse). Scripts ship in the skill's `infra/` (Python stdlib-only) and run from the plugin root — they operate on `$CLAUDE_PROJECT_DIR`, so no per-project script copy.
- **Command** — `/solidforge:arm-tools`.

### Skill docs (`docs/`) — maintainer-facing design rationale

Each skill's `docs/` directory contains the design proposal, iteration plan, ADR log (`design-decisions.md`), and convergence records (`*.convergence.md`). These are **maintainer-facing** design rationale (why the skill works the way it does, what was cross-reviewed, what decisions were locked) — not user-facing docs. **Users only need `SKILL.md` + `references/`** to use a skill. The `docs/` are kept public for transparency: they're the convergence trail that backs every design decision, consistent with the project's own convergence-driven philosophy.

## Install + enable (Layer 1)

**From the repo URL** (the repo is its own marketplace — `.claude-plugin/marketplace.json`):

```text
/plugin marketplace add maskshell/solidforge
/plugin install solidforge@solidforge
/reload-plugins
```

or non-interactively: `claude plugin install solidforge@solidforge --scope project`.

Local dev (no marketplace):

```bash
claude --plugin-dir /path/to/solidforge
```

Session-only alternative: `claude --plugin-url <zip-url>` (zip archives only — no install record, no update tracking).

Then enable per project (`/plugin`) or globally.
Enabling activates the skills, the scoped agents, and the hooks. Plugin agents are priority 5 — user `~/.claude/agents/` same-named globals take precedence, so the skills spawn the plugin agents by their scoped names (`solidforge:<name>`).

## Arm a project (Layer 2)

Plugins do not mutate host-project build files, so enabling does NOT provision gate tools or arch-configs. Run, in a target project:

```cli
/solidforge:arm-tools            # provision arch-configs + constitution + templates + gate-status
/solidforge:arm-tools --with-tools   # also add version-matched gate tools to project dev deps
```

This copies the per-language arch-configs (`.importlinter.ini`, `.dependency-cruiser.cjs`, `.swiftlint.yml`, `clippy.toml`, `checkstyle.xml`), appends the L1 Constitution + Gate
Toolchain note to the project `CLAUDE.md`, copies the intent-blueprint template, and adds `.gitignore` entries for the loop's runtime state. `--with-tools` adds the gate tools to the project's own dev deps (uv/poetry/pip/npm/pnpm/yarn); system-only tools print install commands. Reversible: `arm.py --revert` (dry-run; `--apply` to execute).

See `parallel-development/references/install.md`.

Frontend project wanting design governance? Also arm Impeccable in the same project: `npx impeccable install` then `/impeccable init` (companion, not bundled — see below).

## Companion plugins (recommended, not bundled)

Solid Forge does not reinvent capabilities that exist as maintained official plugins (`claude-plugins-official`):

- **Code intelligence (LSP)** — `arm-tools` recommends the matching official LSP plugin per detected language (`pyright-lsp`, `rust-analyzer-lsp`, `swift-lsp`, `jdtls-lsp`, `typescript-lsp`) plus the language-server binary. Not hard-declared — opt in per language.
- **Security** — `security-guidance` complements Solid Forge's own `arch_contract_deps` gate (secrets + dep vulns inside the loop) with continuous session-wide review.
- **Dev workflows** — `commit-commands` and `pr-review-toolkit` are additive companions (Solid Forge has its own commit policy via `loop_state.py init --commit` and a `code-reviewer` agent).
- **Frontend design governance — Impeccable** (`pbakaus/impeccable`, `claude-plugins-official`).
  For frontend projects, arm it (`npx impeccable install`, then `/impeccable init` to write DESIGN.md/PRODUCT.md) and the convergence loop integrates it: Impeccable's 44-rule detector becomes the design-fidelity gate (advisory findings per edit and a convergence sweep), its `DESIGN.md` becomes the frozen design anchor the implementer codes against, and `/impeccable critique` augments the outer-ring review.
  Pixel-precise teams opt in to hard-rollback on visual drift.
  See `parallel-development/references/external-skills.md`.
- **API-contract governance — Spectral** (`@stoplight/spectral-cli`).
  For projects with an OpenAPI/Swagger spec, arm it (`brew install spectral-cli` or `npm i -g @stoplight/spectral-cli`) and the convergence loop integrates it: `spectral_adapter.py` becomes the API-ruleset gate (advisory convergence sweep linting the spec against `spectral:oas` + `.spectral.yaml`), complementary to `arch_contract_api.py` (presence/path checks). Depth-2: the spec freezes as a Phase-0 anchor the implementer codes against.
  See `parallel-development/references/external-skills.md`.
- **Source SAST — Semgrep** (`semgrep`).
  Arm it (`brew install semgrep` or `pip install semgrep`) and the convergence loop integrates it: `semgrep_adapter.py` becomes the source-SAST gate (advisory convergence sweep over source for CVE-pattern code — OWASP top-ten, injection, traversal, weak-crypto — via `.semgrep/` or `--config auto`), complementary to `/security-review` (LLM) and `arch_contract_deps` (secrets + dependency CVEs). Findings are advisory (SAST is false-positive-prone).
  See `parallel-development/references/external-skills.md`.
- **Docs prose governance — Vale** (`vale`).
  Arm it (`brew install vale` / GitHub release) with a committed `.vale.ini` + `styles/` and the convergence loop integrates it: `vale_adapter.py` becomes the prose-quality gate (advisory convergence sweep over docs for terminology/voice/spelling/inclusiveness). This fills the docs-QUALITY axis — blueprint-crafting checks upstream-doc structure and the language arch gates lint code, but neither lints prose.
  See `parallel-development/references/external-skills.md`.
- **API breaking-change detection — oasdiff** (`oasdiff`).
  Arm it (`brew install oasdiff`) and the convergence loop integrates it: `oasdiff_adapter.py` becomes the backward-compat gate (advisory sweep diffing each tracked OpenAPI spec against its git HEAD version — removed required fields, changed types, deleted endpoints). Complementary to Spectral (spec style) and `arch_contract_api` (presence/path); neither of those diffs versions.
  See `parallel-development/references/external-skills.md`.
- **Dependency license compliance — Trivy** (`trivy`).
  Arm it (`brew install trivy`) and the convergence loop integrates it: `license_adapter.py` becomes the license-compliance gate (advisory sweep inventorying dependency licenses from lockfiles). Complementary to `arch_contract_deps` (secrets + dependency CVEs) — the legal/compliance axis. Without a project policy it is a raw inventory; copyleft/compatibility analysis stays human.
  See `parallel-development/references/external-skills.md`.
- **IaC misconfig — Checkov** (`checkov`).
  Arm it (`brew install checkov` / `pip install checkov`) and the convergence loop integrates it: `iac_adapter.py` becomes the infra-misconfig gate (advisory sweep over Terraform/Kubernetes/Dockerfile — open buckets, permissive security groups, privileged containers). Opt-in for infra-bearing projects (no-op when no IaC files); out of the app-language platform model.
  See `parallel-development/references/external-skills.md`.
- **Built-in harness — Dynamic Workflows (`ultracode`)** (Claude Code built-in, not a plugin).
  Complements the convergence loop at a different layer: the loop is per-feature engineering convergence (gated + breakered + cost-predictable); `ultracode` workflows (keyword in prompt, or `/effort ultracode`) are script-driven, high-token orchestration for UNKNOWN-SIZE / one-off / cross-cutting work the per-feature loop does not cover — repo-wide bug sweeps, large migrations, cross-checked research, adversarial multi-reviewer panels. Do NOT replace the convergence loop with a workflow: its verdict dispatch is a semantic model judgment, not code routing (ADRs #32, #33).

## MCP prerequisites (external servers, not bundled)

Referenced by `parallel-development` (blueprint-crafting is MCP-free). Not bundled in `.mcp.json` — they are user-run servers; declare per setup:

- **graphiti** — OPTIONAL. Cross-session memory + golden paths. The skill degrades gracefully when unreachable (skips memory ops). The bundled `graphiti-config-generator` agent helps configure it.
- **playwright-test** — REQUIRED for E2E. Powers the three `playwright-test-*` agents' `mcp__playwright-test__*` tools.
- **ast-grep** — OPTIONAL. Automated code-review patterns (also usable as the `@ast-grep/cli` CLI, so the MCP is one of two paths).

## Paper

The position paper *Specification Gaming as an Orthogonal Failure Axis in Autonomous Coding Loops* is vendored at [docs/papers/](docs/papers/) — text authority + PDF + LaTeX + its own convergence/verification trails. It is load-bearing for this workspace twice over: the orthogonal-axis frame (same-family vs different-family oracle) behind the [USER_GUIDE verification model](USER_GUIDE.md), and the origin of `primary-source-verification` — the paper's own cross-source-review pass let citation misattributions slip that only independent primary-source spot-checks caught, which is exactly the gap that skill closes. The snapshot is sync-managed from the canonical knowledge base, never drifted silently ([docs/papers/README.md](docs/papers/README.md)).

## Layout

```text
solidforge/                      (repo root = plugin root)
  .claude-plugin/plugin.json     manifest (name=solidforge, version, description)
  skills/
    parallel-development/        convergence-loop implementation skill
    blueprint-crafting/          specify-side skill (Intent Blueprint → plan-model)
    cross-source-review/         cross-source doc-convergence skill (same-family + different-family → substantive convergence)
    primary-source-verification/  per-claim source-verification skill (outcome-axis; fetch-based, backward-CITED, additive to csr)
    prior-art-search/             per-novelty-claim prior-art collision skill (outcome-axis; search-based, backward-UNCITED, additive to csr+psv)
  agents/                        22 agent defs (register as solidforge:<name>); per-role code patterns in skills/parallel-development/references/agent-patterns/
  hooks/hooks.json               PreToolUse + PostToolUse → ${CLAUDE_PLUGIN_ROOT}/skills/.../hooks/*.py
  commands/arm-tools.md          /solidforge:arm-tools (Layer 2)
```

Status: the plugin loads as `solidforge@skills-dir` (repo root = plugin root). Skills live under `skills/`; agents register as `solidforge:<name>` and spawn refs use the scoped form.
Per-project arming (`enable` + `/solidforge:arm-tools`) is the user's step — see § Arm a project above.
