# Subagent Review → Remediation Plan v2 (solidforge plugin)

> Converged via an adversarial review-fix loop (PASS 1 self-review → PASS 2 fresh-context audit found 3 blockers + 10 warnings, all grounded against source → PASS 3 rewrite). Outstanding items are disclosed as coverage notes, not hidden.

## Context

The skills (`parallel-development`, `blueprint-crafting`) and upstreams were restructured/integrated, but the bundled subagents were only internalized — not re-reviewed against the skills they serve. This plan is that review's output.

**Review conclusion (the three questions):**

1. **Alignment — sound, with one structural flaw and one contract gap.** The two skills are *correctly asymmetric*: `parallel-development` is a fan-out orchestration skill (orchestrator → per-task Coder inner-ring → `solidforge:code-reviewer` outer-ring); `blueprint-crafting` is a constrained-production skill running its four activities (author/rewrite/research/check) in the main context with *only* `solidforge:plan-reviewer` at the outer ring. `role-agent-mapping.md` maps all roles. Flaw: 5 `.patterns.md` files register as **ghost agents** (`solidforge:architect.patterns`, dead description) though the workspace's own `plugin_layout.py:169` treats them as non-agent companions. Gap: `solidforge:plan-reviewer`'s body says "read-only, never Edit/Write" but it has **no `tools:` frontmatter** → inherits all tools (prose-only contract).
2. **Missing roles — iOS (strongest), research + security (user-opted-in).** iOS/Apple is first-class in the skill but routed to generic `general-purpose`. blueprint self-authors research (ADR #3/#4); a solidforge:researcher subagent changes that (user accepted). `solidforge:code-reviewer` covers OWASP lightly.
3. **Naming — clean except the `.patterns` ghost suffix.** Consistent kebab-case role-nouns; descriptions follow description-as-router well.

**External benchmark** (Anthropic subagents docs; VoltAgent; wshobson/agents; obra/superpowers; systemprompt.io) confirms each point.

**Decisions (user):** relocate `.patterns.md` (de-ghost); contract-only tool fixes; add solidforge:ios-developer + solidforge:ios-tester + solidforge:researcher + solidforge:security-specialist.

**Roster reconciliation (rule 5 — count drift fixed):** live-registered agents today = **18** (13 real `.agent.md` + 5 ghost `.patterns.md`). After remediation = **17 real, 0 ghost**. The explicit 17:
`solidforge:architect, solidforge:backend-developer, solidforge:code-reviewer, solidforge:devops-engineer, solidforge:documentation-writer, solidforge:frontend-developer, solidforge:graphiti-config-generator, solidforge:plan-reviewer, solidforge:playwright-test-generator, solidforge:playwright-test-healer, solidforge:playwright-test-planner, solidforge:requirements-manager, solidforge:tester` (existing 13) + `solidforge:ios-developer, solidforge:ios-tester, solidforge:researcher, solidforge:security-specialist` (4 new).

## Step 0 — Persist this plan into the project

This plan lives in the harness scratch location (`~/.claude/plans/`). Per the user's decision, persist it to **`docs/subagent-review-plan.md`** (tracked, consistent with the workspace's tracked `design-decisions.md`/`arch-design.md` convention) before final review/approval. This is the only write before code changes; implementation (§A–§G) starts only after the user reviews the persisted plan and approves.

---

## A. De-ghost the `.patterns.md` reference docs (relocate out of `agents/`)

The loader registers any `.md` in the plugin's `agents/` as an agent (filename-derived name when frontmatter is absent). References under `skills/` are bundled files, not scanned → relocation de-ghosts.

- **Move + rename** into a new `references/agent-patterns/` subdir (the dir carries "patterns", so files drop the double suffix — `<role>.md`):
  - `agents/{architect,backend-developer,frontend-developer,code-reviewer,devops-engineer}.patterns.md` → `skills/parallel-development/references/agent-patterns/<role>.md`
  - Sibling to existing `references/<lang>-patterns.md` (language patterns stay directly in `references/`; role patterns in `agent-patterns/` — two kinds, two locations, no collision, one suffix convention: `-patterns.md` for language files, no suffix for role files whose dir already says "patterns").
- **Update the 5 agent links**: each `.agent.md` links its companion. e.g. `agents/architect.agent.md:31` `[architect.patterns.md](architect.patterns.md)` → `[architect patterns](../skills/parallel-development/references/agent-patterns/architect.md)`. Same in `backend-developer.agent.md:41`, `frontend-developer.agent.md:49`, `code-reviewer.agent.md:44`, `devops-engineer.agent.md:36`.
- **`docs/external-skill-integration.md:68`** — prose mention of `frontend-developer.patterns.md`; verify the line, update to `references/agent-patterns/frontend-developer.md` (suffix dropped, consistent with §A).
- **`infra/test/plugin_layout.py`** — three edits, justified as a **structural move** (analogous to the Phase-4 skill-cutover that moved skills off the repo root and touched this checker's path logic via `_find_plugin_root`) — NOT as "EXPECTED_AGENTS is a registry" (that framing erodes rule 2). The edits add **no new decision-point logic**:
  1. `EXPECTED_AGENTS` (lines 50-64): add the 4 new agents → 17. This list is the **plugin-bundled** agent registry (already contains `solidforge:plan-reviewer`, a blueprint agent — precedent), not parallel-development's alone; update the line-49 comment + module docstring to say "plugin-bundled" so adding `solidforge:researcher` (also blueprint's) is consistent.
  2. Companion-coverage check (lines 183-193): the new link form `../skills/parallel-development/references/agent-patterns/<role>.md` contains slashes the old `([\w-]+\.patterns\.md)` class won't match. Replace with **`re.compile(r"references/agent-patterns/([\w-]+)\.md")`** and resolve each captured file under `PLUGIN_ROOT/skills/parallel-development/references/agent-patterns/` (`PLUGIN_ROOT` is in scope, line 39 — not `AGENTS_DIR`). The check's *purpose* (an agent referencing a companion must have it bundled) is preserved; only the location/regex moves. Update the docstring (line 10).
  3. The `.patterns.md` exclusion at line 169 becomes dead (no such files remain) — leave the guard as belt-and-suspenders, or drop it; note either way.
- **`README.md`**: line 12 roster (add 4 new) + line 89 tree (`17 agent defs (register as solidforge:<name>); per-role code patterns in skills/parallel-development/references/agent-patterns/`).
- **`.claude-plugin/plugin.json`** description: append the 4 new agents to the cascaded-subagents prose list.

*Loading-chain guard note (rule 3 — honest):* after relocation, the agent→companion link is validated **only** by the rewritten `plugin_layout.py` companion check. `disconnect_check.py` does NOT guard it — `disconnect_check.py:28` scans `references/` for per-language L4 files (`<lang>-patterns.md`) and their decision-point reachability; it has no knowledge of role-pattern companions or `agents/`. So the exact regex in edit 2 is the sole guard; get it right.

---

## B. Enforce solidforge:plan-reviewer's read-only contract at the tool layer

`agents/plan-reviewer.agent.md`: add frontmatter `tools: Read, Grep, Glob` so the body's "never edits/fixes" contract (lines 12-14, 60-62) is enforced mechanically. Per the official Claude Code subagents spec, plugin subagents **ignore** `permissionMode`/`hooks`/`mcpServers` but **honor** `tools`/`disallowedTools` — so `tools:` works; do not use `permissionMode`. Belt-and-suspenders: also set `disallowedTools: Edit, Write, NotebookEdit`. **Runtime verification (resolved tool list excludes Edit/Write) is ground truth** — if a future loader change stops honoring `tools:` for plugin agents, that step catches it and we fall back to `disallowedTools`-only.

**Coverage gap (rule 3 — disclosed, not hidden):** `solidforge:code-reviewer` is *not* actually scoped today — it has **no `tools:` frontmatter**; its "Available Tools" section is body prose, not enforcement (same gap §B fixes for solidforge:plan-reviewer). Per the user's "contract-only / no broad re-scoping" decision we **leave solidforge:code-reviewer as-is**; mechanical enforcement of its read contract is deferred. State this in the plan, do not claim solidforge:code-reviewer is "already scoped".

---

## C. Add `solidforge:ios-developer` + `solidforge:ios-tester` (parallel-development)

iOS/Apple is first-class (Xcode/Swift/SwiftUI/XCTest/XCUITest/SPM/Simulator) but routed to `general-purpose`. Add dedicated agents for parity with Web.

- **`agents/ios-developer.agent.md`** — mirror `frontend-developer.agent.md` structure. Body: SwiftUI/UIKit views, SPM/Xcode project structure, Swift concurrency (async/await, actors, Sendable), XCTest unit tests, Simulator/device build & run. Reference the existing `references/ios-patterns.md` + `references/memory-protocol.md`. Description (description-as-router): "Expert iOS/macOS developer specializing in Swift, SwiftUI, and the Apple toolchain. Use when: (1) Building SwiftUI/UIKit views or features, (2) SPM package or Xcode project setup, (3) Swift concurrency (async/await, actors), (4) XCTest unit tests, (5) Simulator/device build & run. Route here instead of general-purpose for any Apple-platform task."
- **`agents/ios-tester.agent.md`** — mirror `tester.agent.md`. Body: XCUITest UI/E2E, `.xcresult` analysis via `xcrun xcresulttool`, flaky-XCUITest maintenance (>30%-failure halt per `SKILL.md:224`). Description: "Expert iOS/macOS QA engineer for XCTest and XCUITest. Use when: (1) XCTest unit tests, (2) XCUITest UI/E2E tests, (3) Parsing .xcresult bundles, (4) Diagnosing flaky UI tests, (5) iOS test-strategy design."
- **Boundary**: solidforge:ios-developer owns impl + XCTest unit; solidforge:ios-tester owns **XCUITest UI/E2E + xcresult** (solidforge:ios-tester ≈ `solidforge:playwright-test-*`, the platform E2E specialist — not a second unit-tester). Both inherit broad tools (implementers); omit `model`.
- **`role-agent-mapping.md` doc-audit (rule 5 — full surface, not just one row)**:
  - Line 329 "Test Engineer" conditional row (single row, iOS branch → `general-purpose`): rewrite iOS branch → `solidforge:ios-tester`; Web/Backend stays `solidforge:tester`. (There is no separate "Test Engineer (iOS)" row.)
  - **Lines 354-374 "E2E Test Engineer"** (line 367 routes iOS XCUITest → `general-purpose`): rewrite to route iOS XCUITest → `solidforge:ios-tester`; Web stays `solidforge:playwright-test-*`. (Without this, solidforge:ios-tester's defined scope is contradicted — blocker B2.)
  - "iOS Developer" row → `solidforge:ios-developer`.
  - **"Apple Platform Architect" (lines 309-326, → solidforge:architect)**: add a disambiguation note vs solidforge:ios-developer mirroring the existing solidforge:architect/solidforge:frontend-developer/design fork at line 56 — Apple Platform Architect owns module/architecture decisions; iOS Developer owns implementation.
  - Contents TOC (lines 5-21): add entries for solidforge:ios-developer, solidforge:ios-tester.
- **Other iOS enumeration hits (rule 5 — these are MORE load-bearing than the role row)**:
  - `SKILL.md:329-334` — 3 TaskCreate examples hardcode `agent: general-purpose` for iOS + a "use general-purpose for iOS" note → update to solidforge:ios-developer/solidforge:ios-tester.
  - `references/feature-dev.md` (~8 hits), `references/bug-fix.md` (~5), `references/refactoring.md` (~6), `references/parallel-patterns.md:176` (`"agent_type": "general-purpose"` iOS JSON example) → update worked examples to the new agents (or defer with a coverage note; do not silently leave them).
  - `references/extending.md:48` ("Swift uses general-purpose with an iOS prompt") — the per-language formula doc (rule 2's exemplar) → update to solidforge:ios-developer/solidforge:ios-tester.
  - `references/golden-paths.md`, `references/arch-contracts.md` — verify iOS rows name the new agents at the decision point.

---

## D. Add `solidforge:researcher` (blueprint-crafting) — sourcing/convergence split

blueprint-crafting self-authors research (ADR #3/#4). The solidforge:researcher moves only **verbose multi-source web gathering** into an isolated context; the **convergence oracle stays in the skill** (`research_constraints.py`); **conclusion truth stays outcome-axis (human)**.

- **Integration path (corrected — do NOT claim the normalizer accepts `research-notes`; it does not).** `normalizer.py:240-244` has 3 parsers (`cursor-plan`/`work-package`/`rich-md`), all emitting an `items[]` shape — none emit the `research.{claims,sources,cost_ledger,staging}` sub-object that `research_constraints.py:41-47` reads. Research artifacts therefore already use a plan-model shape the normalizer's item-parsers do not produce. So: the solidforge:researcher **emits the `research` sub-object directly** (the exact shape `research_constraints.py` consumes: `claims[]{text, source_refs[]}`, `sources[]{source_id, fetched, provenance}`, `cost_ledger{budget, used}`, `staging{in_staging, converged}`); the convergence loop (the skill, main context) places it into `plan_model["research"]`, **bypassing the normalizer** — consistent with how research artifacts already acquire that field. No normalizer code change; no new parser. Read `research_constraints.py:41-127` before authoring so every emitted field maps to a check.
- **Doc fix (the aspirational `research-notes` mention):** `SKILL.md:52` and `arch-design.md:65` list `research-notes` among normalizer source formats — that is diagram-prose intent, never implemented. Annotate (not silent): note that research artifacts bypass the item-normalizer and populate `plan_model["research"]` directly (now via the solidforge:researcher subagent for sourced gathering).
- **`agents/researcher.agent.md`** — mirror `plan-reviewer.agent.md`'s *discipline* (fresh independent context, schema'd output, narrow role, explicit "what is NOT your job") but it is a *producer* (gathers+cites), not a reviewer. Body: gather web + codebase sources; return the `research` sub-object; **never** judge conclusion truth. Tools **scoped from creation** (new-agent design, not the declined broad re-scoping): `tools: WebSearch, WebFetch, Read, Grep, Glob` (web + read-only; no Edit/Write — it returns a JSON sub-object, never mutates files). Description: "Research agent for the blueprint-crafting skill. Gathers web + codebase sources for an upstream artifact's open questions and returns the research sub-object (cited claims + provenance-tagged sources + cost ledger). Use when: (1) researching X for a spec/arch-design, (2) gathering sources for a research artifact, (3) surveying library/API options with citations. Spawn only for multi-source web gathering. Output feeds research_constraints (sources-cited/staging/cost/provenance). Never judges conclusion truth — outcome axis, human only."
- **Trigger condition (bounds the ADR #3 change):** dispatch `solidforge:researcher` only for **external multi-source web gathering** (verbose fetch output that would bloat main context). Trivial lookups / codebase-only research keep self-authoring per ADR #3. Researcher is an opt-in context-isolation tool, not a mandatory detour.
- **Disambiguate vs `deep-research` skill:** `solidforge:researcher` = in-convergence sourcing feeding `research_constraints.py` (process-axis convergeable); `deep-research` = heavyweight standalone cited-report harness, **not** in the convergence loop, for full reports. Rejected: route blueprint research to `deep-research` (it emits a report, not the `research` sub-object, and does not pass `research_constraints.py`).
- **Doc-audit (rule 5)**: `SKILL.md` converge pipeline (line ~70) — note the research activity dispatches `solidforge:researcher` for sourcing (first grep `infra/test/` to confirm no test asserts that pipeline string verbatim; if one does, update in lockstep). `docs/arch-design.md` role/component table (line ~161) — add `solidforge:researcher` if it enumerates subagents. `plugin_layout.py` EXPECTED_AGENTS — add `solidforge:researcher` (plugin-bundled; solidforge:plan-reviewer precedent). solidforge:researcher does **not** reference parallel-development's `memory-protocol.md` (verified: blueprint-crafting has no `memory-protocol.md` of its own — grep `skills/blueprint-crafting/`; solidforge:researcher follows solidforge:plan-reviewer's no-memory-protocol convention).

---

## E. Add `solidforge:security-specialist` (parallel-development) — outer-ring security review

Dedicated security review beyond `solidforge:code-reviewer`'s OWASP coverage.

- **Inner-ring vs outer-ring division (do not duplicate the deterministic gates):** the workspace already integrated **inner-ring deterministic rule-gates** that Block on real violations — `semgrep_adapter.py`, `license_adapter.py` (Trivy), `iac_adapter.py` (Checkov). `solidforge:security-specialist` is strictly **outer-ring** — the semantic review those gates cannot encode: auth/authz logic flaws, access-control design, secret-handling across files, threat modeling, and triaging gate output into severity-ranked findings. It must NOT re-run what the gates already enforce.
- **`agents/security-specialist.agent.md`** — mirror `code-reviewer.agent.md` (read-only reviewer, structured findings, language-specific guidelines). Body: OWASP Top 10, auth/authz, secrets, dependency-vuln (semgrep/trivy), IaC (checkov), threat modeling. Read-only — reports findings by severity, does not fix. Tools scoped from creation: `tools: Read, Grep, Glob, Bash, mcp__ast-grep__find_code, mcp__ast-grep__find_code_by_rule` (read + run scanner adapter scripts via Bash; no Edit/Write). References `references/memory-protocol.md`. Description: "Expert security engineer for vulnerability assessment and secure coding. Use when: (1) Security review before production, (2) OWASP Top 10 / auth/authz review, (3) Secret + dependency-vuln scanning (semgrep/trivy), (4) IaC security (checkov), (5) Threat modeling. Read-only — reports findings, does not fix. Route here (not solidforge:code-reviewer) for dedicated security review."
- **`role-agent-mapping.md` doc-audit**: add "Security Specialist → solidforge:security-specialist" role row after Code Reviewer (trigger: auth/secrets/public surface/IaC) **+ a Contents TOC entry (lines 5-21)**; scope the Code Reviewer row's existing security mention to defer to solidforge:security-specialist for dedicated security work. `plugin_layout.py` EXPECTED_AGENTS — add `solidforge:security-specialist`.

---

## F. Cross-cutting doc-audit (rule 5) + naming

**Doc-audit method**: grep each skill's `references/` + root `README.md` + `.claude-plugin/plugin.json` for the existing agent names and `general-purpose` (iOS), and update every enumeration hit. High-priority surfaces already named per-section: `role-agent-mapping.md` (rows + TOC), `SKILL.md:329-334`, `feature-dev.md`/`bug-fix.md`/`refactoring.md`/`parallel-patterns.md`/`extending.md`, blueprint `SKILL.md`+`arch-design.md`, `plugin_layout.py`, `README.md`, `plugin.json`.

**Naming convention (rule 10):**

- Form: `<role>` or `<domain>-<specialist>`, kebab-case, role/specialist **noun** (solidforge:architect, solidforge:backend-developer, solidforge:ios-developer, solidforge:security-specialist, solidforge:researcher). No verb-form agents.
- Reviewer/diagnose agents end `-reviewer`/`-specialist` and are read-only (`solidforge:plan-reviewer`, `solidforge:code-reviewer`, `solidforge:security-specialist`).
- Specialist tester family: `<tech>-test-*` (`solidforge:playwright-test-planner` / `solidforge:playwright-test-generator` / `solidforge:playwright-test-healer`, `solidforge:ios-tester`); generalist stays `solidforge:tester`.
- Reference-doc suffix: `-patterns.md` reserved for `references/<lang>-patterns.md`. Role patterns live in `references/agent-patterns/<role>.md` (**suffix dropped** — the dir carries "patterns"). No agent file lacks `name:`+`description:` frontmatter.
- One joiner (`-`), one term per concept; plugin-scoped `solidforge:<name>` disambiguates from same-named globals.

---

## ADRs to record (rule 6)

1. **blueprint `docs/design-decisions.md` — researcher sourcing/convergence split** (modifies ADR #3/#4). Context · Decision (solidforge:researcher emits `research` sub-object directly; loop injects into `plan_model["research"]`, bypassing normalizer; convergence oracle stays in `research_constraints.py`; truth stays outcome-axis) · Why (context isolation for verbose web gathering; preserves constraints-profile) · Rejected: (a) main-context self-authoring = ADR #3 status quo; (b) solidforge:researcher that judges truth = violates outcome-axis; (c) solidforge:researcher with Edit/Write to stage its own output = staging must be human-gated (ADR #4); (d) implement a `parse_research_notes` normalizer parser = scope-creep, unneeded since research artifacts bypass item-normalization. **Coverage note:** solidforge:researcher assumes blueprint-crafting wins activation; the blueprint-vs-`deep-research` **skill-level** activation collision is orthogonal and unaddressed here.
2. **parallel-dev `references/design-decisions.md` — solidforge:ios-developer/solidforge:ios-tester replace the general-purpose fallback** (rejected: keep general-purpose + prompt; broaden `solidforge:tester` to cover iOS instead of a dedicated solidforge:ios-tester).
3. **parallel-dev `references/design-decisions.md` — security-specialist** (outer-ring only; rejected: solidforge:code-reviewer-only; second inner-ring scanner = redundant with the deterministic gates).
4. **parallel-dev `references/design-decisions.md` — `.patterns.md` relocation: reference-docs-not-agents** (filed in parallel-dev because all 5 companions belong to parallel-dev agents; rejected: promote-to-frontmatter'd-agents; leave-as-is).
5. **blueprint `docs/design-decisions.md` — plan-reviewer `tools:` frontmatter.** *Plugin-level concern* (tools/disallowedTools honored for plugin agents; permissionMode/hooks/mcpServers ignored) applying to any plugin agent; filed in blueprint (solidforge:plan-reviewer's home) with a cross-ref note that it is plugin-wide (no plugin-level ADR log exists today).

---

## Verification (rule 1: skill self-gates must pass)

parallel-development self-gates (skip gracefully when external tools absent):

```bash
python3 skills/parallel-development/infra/test/plugin_layout.py     # 17 plugin-bundled agents + relocated companions well-formed (exact regex from §A)
python3 skills/parallel-development/infra/test/disconnect_check.py  # language L4 loading chain (does NOT guard agent companions — see §A note)
python3 skills/parallel-development/infra/test/smoke_gates.py
python3 skills/parallel-development/infra/test/lint_self.py
python3 skills/parallel-development/infra/test/arm_copy_config.py   # mutates — run last / in a throwaway dir
```

blueprint-crafting self-gates (solidforge:researcher addition must not break convergence):

```bash
python3 skills/blueprint-crafting/infra/test/end_to_end.py
python3 skills/blueprint-crafting/infra/test/research_constraints_goldens.py
python3 skills/blueprint-crafting/infra/test/plan_reviewer_precision.py
python3 skills/blueprint-crafting/infra/test/disconnect_check.py
```

Manual checks:

- **De-ghost (deterministic + runtime)**: (1) `ls agents/*.patterns.md` empty post-relocation; (2) reload plugin (new session) — `solidforge:architect.patterns`/`.backend-developer`/`.frontend-developer`/`.code-reviewer`/`.devops-engineer` gone; the 4 new agents appear with descriptions.
- **solidforge:plan-reviewer contract**: resolved tool list excludes Edit/Write (ground truth; if not, fall back to `disallowedTools`-only — §B).
- **solidforge:researcher ↔ constraints**: a dry research run emits the exact `research` sub-object shape `research_constraints.py:41-127` consumes (no normalizer in the path).
- **Routing smoke**: Apple-platform request → solidforge:ios-developer (not general-purpose); XCUITest → solidforge:ios-tester; "research X for the spec" within blueprint → solidforge:researcher; secrets/auth review → solidforge:security-specialist.

## Coverage gaps disclosed (rule 3 — not hidden)

- solidforge:code-reviewer's read contract stays prose-only (no `tools:` frontmatter) per the user's contract-only decision (§B).
- blueprint-vs-deep-research skill-level activation collision unresolved (ADR #1 coverage note).
- blueprint-crafting has no memory-protocol.md of its own (verified); solidforge:researcher follows solidforge:plan-reviewer's no-memory convention.

## Out of scope / intentional non-changes

- No broad tool-scoping of existing implementer agents (user: contract-only).
- No model tiering (global rule: don't hardcode model).
- No dedicated orchestrator subagent — both skills keep orchestration in the main context.
- blueprint-crafting keeps `solidforge:plan-reviewer` as its only *review* subagent; `solidforge:researcher` is a producer, not a second reviewer.
