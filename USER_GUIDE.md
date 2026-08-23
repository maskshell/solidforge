# Solid Forge — User Guide

**English** | [简体中文](USER_GUIDE.zh-CN.md)

A loop-engineering system for AI coding agents. "Done" means the work passes a deterministic inner ring **and** an AI outer ring — not "the agent stopped". This guide ships you code in 30 seconds, then layers in the *why* (the maturity model) + the opt-in extensions. Overview: [README.md](README.md); install + feature doc: [install.md](skills/parallel-development/references/install.md); maturity framework: [maturity.md](skills/parallel-development/references/maturity.md) (self-contained).

## Ship in 30 seconds

Have a code task? Invoke pd directly — **the slash command guarantees the skill activates** (no routing surprise):

> /parallel-development implement a FastAPI endpoint for user registration

**`/parallel-development`** (pd) runs the convergence loop (lint → architecture-contract → supply-chain → tests → AI review), iterates until both rings pass clean, commits each converged stage on a feature branch (never `main`), and reports. You don't invoke agents or hooks directly — the skill orchestrates them. (The specify half is **`/blueprint-crafting`**, bc.) The bare phrasing `implement …` *usually* routes to pd too — but the explicit slash command is the 100% path; use it when you want certainty.

No plan needed for a single task. If you already have one, skip to [Workflows](#workflows).

## The skill pipeline

Five skills, one pipeline plus two additive outcome-axis layers (cited-source verification + uncited-prior-art collision):

| Skill | Job | Trigger |
| --- | --- | --- |
| **cross-source-review** (csr) | converge — drive same-family + different-family cross-review of a doc to substantive convergence | "cross-review this requirements doc", "converge this design doc", "different-family review this wiki page" |
| **blueprint-crafting** (bc) | specify — converged specs, arch-designs, iteration plans | "author a spec for …", "author an arch-design for …" |
| **parallel-development** (pd) | implement — code converged through the dual ring | "implement …", "fix …", "refactor …" |
| **primary-source-verification** (psv) | verify — per-claim CITED-source verification (additive outcome-axis layer, not sequential; gate mode: load-bearing subset GO/NO-GO before csr when rule-13 conditions hold) | "verify this doc's citations against primary sources", "fact-check this spec's arXiv claims" |
| **prior-art-search** | collision-check — hunt UNcited prior art for a doc's NOVELTY claims (additive outcome-axis layer) | "does this paper overclaim novelty", "hunt uncited prior art for these novelty claims", "is this framing already in the literature" |

```text
csr (converge a doc) → bc (specify) → frozen spec → pd (implement) → converged code
psv (verify each CITED citation claim vs its fetched source) — additive outcome-axis layer; authoritative full-M record after csr
psv-gate (load-bearing subset, GO/NO-GO) — optional, BEFORE csr when rule-13 conditions hold; gate record is NOT a coverage record
prior-art-search (hunt UNcited prior art for each NOVELTY claim) — second additive outcome-axis layer
```

psv and prior-art-search are the two outcome-axis legs — both additive, both run on any doc, after or beside csr. psv additionally has a **GATE MODE**: when rule-13 conditions hold (load-bearing citations against fetchable sources), run it BEFORE csr as a load-bearing-claims subset gate — the gate's GO/NO-GO is a batch signal, NOT a coverage record; the authoritative coverage disclosure comes only from the full-M run after csr. psv = backward-CITED (does each cited source actually support the claim?); prior-art-search = backward-UNCITED (does findable prior art already make a novelty claim the doc didn't cite?). They compose (a high-stakes doc may run both); they never merge, and neither emits a truth/novelty boolean (`oracle_verified_under_known_coverage` / `collisions_under_known_coverage`; never `correctness_converged` / `novel_confirmed`).

csr is the convergence layer **upstream of bc** (and reusable standalone): it drives a same-family (same-family, fresh-context) + different-family (cross-family, e.g. DeepSeek) multi-round review of a doc-shaped artifact — a requirements input before bc, a design doc, a wiki page — to **substantive convergence** (the core claims coverage-verified AND no new Blocker for ≥2 rounds; NOT zero-finding). bc MAY call csr for a different-family pass on its draft. csr is NOT code review (pd), spec authoring (bc), or research gathering (bc's researcher); it converges PROCESS-AXIS quality (well-formed, consistent, citation-accurate), never whether the doc is "right" (outcome-axis — human). Its convergence records are audit-ready: every round embeds the reconciled findings + per-finding dispositions (what was found, and what was done about it). Provisioning + custom providers: [csr install.md](skills/cross-source-review/references/install.md).

Activation is by description (the model routes from your phrasing) — usually correct, but when reliability matters, invoke explicitly: `/cross-source-review`, `/blueprint-crafting`, `/parallel-development`, `/primary-source-verification`, `/prior-art-search`.

> **bc formalizes; the *right* requirement is yours to mine.** bc converges an artifact on its *constraints-profile* (structure / anchors / authority-chain) — that's **process-axis "quality met"** (符合输出规范 — the spec is well-formed). It does **not** own whether the spec captures your *real* need — that's **outcome-axis** (human only; `rightness: human_confirm_required` on every run-record; [bc SKILL.md](skills/blueprint-crafting/SKILL.md)). "Quality met" ≠ "satisfies the real need."
>
> So a bare `author a spec for X` (e.g. "write a POS spec") yields a **well-formed spec built on bc's own assumptions**, not your requirements. Surface the requirements first — dialogue, an existing doc, or bc's research for the researchable parts — **then** bc converges them into the frozen artifact pd implements. bc owns the convergence; **you own the outcome**. (`research …` is **not** a standalone bc trigger: research's value is *truth* — an outcome bc doesn't own; bc researches as an **input to authoring**, feeding the artifact it converges, but the findings' truth is yours to verify.)

> **csr converges the doc; the right content is still yours.** `/cross-source-review` (csr) drives a doc to *substantive convergence* — process-axis (well-formed, internally consistent, citation-accurate) via same-family + different-family cross-review. Like bc, it does **not** own whether the doc captures your real need (outcome-axis, human). Use it to converge the requirements/design doc **before** bc formalizes it, or standalone on any doc (a wiki page, a design doc) that needs cross-source adversarial review.

### Two-axis doc convergence: csr + psv (optional — for high-stakes, citation-heavy docs)

psv is **optional and additive**, not a required stage. Reach for it only for a **high-stakes, citation-heavy doc where a wrong citation would materially weaken the argument** (a spec/research citing arXiv, a design doc citing standards). When those conditions hold, run it TWICE: a load-bearing-claims GATE before csr (GO/NO-GO — the gate's GO is a batch signal, NOT a coverage record), then the authoritative full-M run after csr. Discriminator (ODP-5, 2026-08-10): the gate pays on docs whose load-bearing citations are predominantly EXTERNAL (arXiv/blogs/standards — the model's recall blind-spot zone) and on LONG-tier docs (expected csr investment ≥ 3 rounds); docs citing mostly local files — csr alone suffices, and short docs never pay the gate (~1.5 rounds cost vs ≤2 rounds max saved). For low-citation or low-stakes docs, csr alone suffices (psv returns `M=0 → no admissible surface`).

When you do use it, add psv in two passes — a load-bearing-claims **gate before csr** (GO/NO-GO; its load-bearing list becomes csr's core-claims frame), then the authoritative full-M run **after csr, before bc**:

1. **`/cross-source-review`** — process axis: well-formed, internally consistent, citation-structured, coverage-complete (recall-based).
2. **`/primary-source-verification`** — outcome-axis admissible surface: each citation claim verified against its **fetched** source (`verified` / `refuted` / `narrowed` / `unverifiable`) + an honest `oracle_verified_under_known_coverage` disclosure (fetch-based).

**Order (rule-13 docs): `psv(gate) → csr → psv(full M) → bc`** — the gate first (cheap premise check; NO-GO → rework sources before csr investment), the full-M record after csr (authoritative). Non-rule-13 docs: `csr → psv → bc` unchanged (psv an optional insert, not a fixed pipeline stage). psv catches citation misattributions csr's recall-based legs miss (it found real defects in peer skills' design docs this way); csr catches structural gaps psv doesn't. psv findings feed back into csr's re-convergence. Neither judges whether the doc is *right* — that stays human.

**Sibling outcome-axis layer — `/prior-art-search`:** where psv checks the doc's *cited* sources, prior-art-search hunts *uncited* prior art for the doc's **novelty** claims ("we introduce X", "first to Y", "no prior art"). Use it for a high-stakes doc whose novelty framing could overclaim — a design paper, a research doc — alongside or instead of psv. prior-art-search emits `collisions_under_known_coverage` (N collisions / U uncited-relevant / C clear-under-search / I inconclusive of M) and NEVER `novel_confirmed` (the absence-of-evidence limit: a zero-collision result is "no collision in what was searched," not "novel"). Its oracle — the searchable prior-art corpus — is weaker than psv's fetched source at two layers (comparison-side + selection-side), which is exactly why it stops at a coverage disclosure.

## Workflows

### Implement from a plan you already have

Hand it any plan-shaped doc — hand-written, a Cursor `.plan.md`, an architect's output:

> /parallel-development implement feature X per @my-plan.md

pd reads it, shows you the work queue (items, dependency graph, DoD source) for confirmation, then chains each item to convergence. You get converged code plus two artifacts: a per-item outcome summary printed to stdout (`plan_queue.py aggregate`), and a run-record file at `.claude/parallel-dev/runs/<task>-<stamp>.json` carrying steps, budget, and the `l4_assessment` (gitignored; the resume + audit record).

### Specify, then implement (the full pipeline)

Want it done right, end to end? **Mine the requirements first** (bc formalizes; it doesn't discover — see the [callout above](#the-two-skill-pipeline)), then specify, then implement against the frozen spec:

1. **Mine the requirements** — an interactive dialogue, an existing requirements/context doc, or bc's research for the researchable parts (multi-source web gathering). This is the *outcome-axis* step; the *right* requirement is yours. A bare `author a spec for X` skips this and lets bc generate plausible-but-assumed content instead.
2. `/blueprint-crafting author a spec for feature X` (+ the mined context) → bc converges and freezes the spec — the *process-axis* step: it shapes your requirements into a structured, anchor-complete, authority-consistent artifact.
3. `/parallel-development implement feature X per the spec @frozen/feature-x.queue.md` → pd detects the bc origin and takes the **rich path**: bc's resolved decisions and research flow forward (pd won't re-ask or re-imagine them), and the spec's acceptance criteria seed executable tests. No gap between "what was specified" and "what was built" — but the spec reflects only what step 1 surfaced.

### Cross-review a doc to convergence (csr)

Have a doc — a requirements input, a design doc, a wiki page — that needs adversarial cross-review before you trust it? `/cross-source-review` (csr) drives a same-family + different-family multi-round review to **substantive convergence**:

> /cross-source-review converge this requirements doc @reqs.md

csr alternates the same-family leg (`solidforge:doc-reviewer`, fresh-context, read-only) + the different-family leg (DeepSeek via `hetero_doc_review.py`), each fed the other's findings so it hunts the gap (not restatements), until the core claims are coverage-verified AND no new Blocker appears for ≥2 rounds. Cap-hit → `adversarial-stalemate`, escalated to you (never silent-pick). You get the converged doc + an honest convergence-record (process-axis verdict; outcome stays human).

**Arming — env-based, no arm command.** csr's gates are self-gates (they run on csr's own infra, not your project's), so your project installs nothing — only the different-family leg's provider token is needed: `export DEEPSEEK_ANTHROPIC_AUTH_TOKEN=sk-...` (or your project `.env`). The same-family leg needs nothing. Custom providers + the token-var naming rule: [csr install.md](skills/cross-source-review/references/install.md).

**The full pipeline with cross-review**: mine the requirements → `/cross-source-review converge @reqs.md` → `/blueprint-crafting author a spec …` → `/parallel-development implement …`. csr is optional — bc formalizes whatever input you hand it, converged or not; csr raises the input's quality first.

### One-shot bc → pd (skip the human review of the spec)

You can chain both skills in one prompt — bc produces the spec, pd consumes it, **no human review of the spec in between**:

> Using @context.md, have `/blueprint-crafting` produce a spec, then `/parallel-development` implement it
>
> （中文同样：`针对 @xxx.md，使用 /blueprint-crafting 输出规范给 /parallel-development 完成迭代`）

**Tradeoff — you're skipping the outcome-axis review.** bc's spec is process-axis-converged (well-formed), NOT outcome-validated (it may reflect bc's assumptions, not your real need — see the [callout above](#the-two-skill-pipeline)). Without the human review between bc and pd, bc's assumptions ride straight into code. **Lower-risk** when `@context.md` already carries the real requirements (bc formalizes a known-good input) — though bc is still a generative model and can misread even good input, so residual risk remains; **not** appropriate when the requirements are fuzzy and you needed bc to discover them (it can't — bc formalizes + researches the researchable parts, but your *real* need is upstream of it). For high-stakes work, keep the 3-step flow above with the review.

### Day-to-day pd tasks

All run the same convergence loop, one item:

| You want | Prompt |
| --- | --- |
| Fix a bug | `fix the bug in auth/login.ts where …` |
| Refactor | `refactor the payment module to use …` |
| Tests | `write e2e tests for the checkout flow` |
| Docs for code just written | `document the API I just implemented` |

**Tip**: if your spec or artifact is in Chinese, bc's anchor detection is bilingual (English + Chinese keywords) — no workaround needed.

## Why it works — the maturity model

This is the "why". The lever that decides whether an agent can run long unattended is **system-level flow control**, not a smarter prompt — single-step quality is near-saturated, but a long task's total pass rate is the *product* of per-step reliability (~95% per step collapses below 8% over fifty). Solid Forge's value is systematic defense of the long-run **degradation effects** that make long agent runs fail, graded on the **L1–L4 maturity ladder** (the *intrinsic flow-control axis*). Full framework + self-assessment: [maturity.md](skills/parallel-development/references/maturity.md).

### The four degradation effects (what long runs die of)

| Degradation | What happens | Mature defense | In Solid Forge |
| --- | --- | --- | --- |
| **Context Rot** | Redundant thinking + verbose tool output (thousand-line logs) fill the window; the agent forgets + degrades late. Attention is U-shaped — middle content is used least. | Explicit pruning + state-summary folding at tier transitions. | Context folding at the inner→outer transition — only a one-sentence folded summary + diff + blueprint cross the ring, never the inner stderr trail. |
| **Error Compounding** | A tiny per-step deviation (wrong file, failed regex, hallucinated path) is amplified exponentially down the step chain. | Structured self-correction + a separate reflection pass (diagnose ≠ fix). | Dual-ring self-correction: the fast gate PostToolUse `decision:block` → next-turn self-fix; structured 越权日志; the independent outer-ring reviewer is a second reflection pass. |
| **Goal Drift** | On large cross-module tasks the agent is pulled into a sub-problem and forgets the global goal. | An external, read-only intent anchor + periodic diff-against-original. | Frozen Intent Blueprint (three-layer read-only) + diff-to-blueprint → intent-drift verdict → hard rollback + reverse-prompt injection. |
| **Specification Gaming** *(orthogonal — see below)* | The agent optimizes a proxy spec ("passes tests", type-checks, self-review) instead of the real goal — silent semantic failure. The proxy/real-goal gap is **irreducible** (a specification problem). **Key tension**: L4's "proactive test self-verification" is *same-family* — a **carrier** of this degradation, not a defense. | An **different-family oracle** (an external source whose blind-spot set differs: production regression, formal spec, human semantic gate, a different model family). | The different-family extension (PARTIAL) — a different model family; overt gaming (delete/weaken tests) is also caught by the AC→test-name gate. |

The first three are *physical* consequences of probabilistic generation + bounded attention on a long sequence. The fourth is a **relationship** failure (proxy ≠ real goal) — orthogonal to flow control; it does **not** advance L1–L4.

### The L1–L4 ladder (intrinsic flow-control axis)

| Grade | Flow-control trait (degradation defended) | Deliverable | Run horizon |
| --- | --- | --- | --- |
| **L1 Single-Turn** | No loop, no state — driven by explicit user turn-taking. | Single-function generation, syntax fix. | 1 step |
| **L2 Fixed Loop** | ReAct loop but flow control is hardcoded; no exception handling → unexpected errors dead-loop or abort. *(Error compounding undefended.)* | Single-file bug fix, simple feature in clear context. | single-to-tens of steps |
| **L3 State Routing** | Prompt = state-machine control language; structured exception handling + degradation (test fails → reflection template). Error compounding partly defended. | Multi-file refactor, small independent module, initial TDD. | tens of steps |
| **L4 Autonomous Closed-Loop** | Deep runtime binding: proactively generates tests to self-verify, prunes memory for token efficiency, anchors intent against drift, **an external state machine forces convergence via a circuit breaker**. **All three physical degradations systematically defended** (spec-gaming is orthogonal — self-test carries it, doesn't defend it). | Multi-file defect fix or closed-loop feature, converged under the 3-degradation defense. | hundreds of steps |

Transitions: **L2→L3** is *hardcoded flow control → state-machine flow control*; **L3→L4** is *passive exception handling → proactive runtime governance + self-verification*. **L4 is the end of the intrinsic axis** — "a stronger agent" cannot cross it (the self-certification paradox below). **There is no L5**: the next lever (different-family) is on an orthogonal axis, not a higher grade (see below). Run horizons are observed-interval estimates (in provider-normalized *steps*, not wall-clock), not authoritative thresholds.

### Capacity vs demand (don't conflate)

- **Capacity** (what the grade measures) = the 3-degradation defense under convergence. Demand-independent — a self-edit on a familiar codebase CAN evidence it.
- **Demand** = task fuzziness / codebase novelty / difficulty / run-horizon. A demanding run **stress-tests** capacity; it does **not** define it. Defining the grade by difficulty is circular ("L4 = can do tasks that need L4").

### The orthogonal axis — verification-source decoupling (different-family)

*(The position paper developing this frame is vendored at [docs/papers/](docs/papers/README.md).)*

Specification Gaming is defended NOT by climbing L1–L4 but along a **second, orthogonal axis**: from **same-family** verification (the agent's own tests — shares the coder's blind spot) to an **different-family oracle** (an external source whose blind-spot set differs). This is **NOT L5** — numbering it so fakes same-axis progression; it is a different kind of lever. The **self-certification paradox**: an agent verifying itself with its own tests is self-certifying — verifier + verified share the blind spot, so a stronger agent still cannot catch spec-gaming. The oracle must be external.

Two failure shapes, two defenses:

- **Overt gaming** (delete the failing test, `@Ignore`, hardcode a bypass, shrink the test set) — agent-internal structural discipline catches it: the AC→test-name gate Blocks a naked delete; intent-drift → hard rollback.
- **Covert proxy optimization** (overfit fixtures, swallow exceptions, mock the dependency) — structural discipline *cannot* catch it; only the different-family oracle can.

Solid Forge wires a **PARTIAL** different-family oracle (the opt-in different-family extension below) — a cross-family adversarial review. PARTIAL because commercial model families share training-data/RLHF overlap; full defense needs production regression / formal spec / human semantic gate (future).

### Grading your own runs

The architecture has every L4 mechanism — the external state machine (hooks + circuit breaker) that forces convergence, context folding, the frozen intent anchor, TDD-by-default. But **the operational grade for YOUR runs is yours to observe, not ours to claim for you**: it depends on your LLM (different models differ), how you've armed the project, and your tasks' demand. Each run emits a run-record with an `l4_assessment` block — a provisional verdict (`l4-evidenced` / `not-yet` / `not-a-probe` / `inconclusive`) computed from that run's evidence; read it to judge where YOUR setup sits. What shapes the grade:

1. **Two different levers — enabling vs arming.**
   - **Enable the plugin** (Layer 1) = the L3→L4 lever. Without it, the skill runs methodology-only (agent follows SKILL.md, runs gates manually — advisory, ~L3). With it, the hooks + circuit breaker fire on every edit in the project — that external enforcement is the L4 trait. (Hooks fire on ALL edits, not just `/parallel-development`.)
   - **Arm the project** (Layer 2, `/solidforge:arm-tools`) = the **substance** lever. It provisions what the gates need to actually fire: arch-configs (rules) + gate dev-deps (engines). The critical combination is `--with-tools` — see [Arming](#arming-a-project-solidforgearm-tools) for the full flag table. Rules without engines (or vice versa) → tool-gates degrade to coverage notes; the state-machine enforcement still runs. Never a silent green.
2. **different-family defense is PARTIAL** (above). Mutation testing (the eventual engine-level different-family) remains future.
3. **Assertion-quality is a REMAINING GAP.** Test *presence* + execution *coverage* are defended; assertion *sufficiency* (does the test actually catch bugs?) is not — mutation testing is the eventual oracle.
4. **Default caps sit on the L3/L4 seam** (`cap_M=8` inner iterations, `time_cap_W=1800s`) — even the designed horizon straddles the line. The provider-independent **capability** limit is the **step cap** (`step_cap_S=200` work units); the token budget is approximate (hooks can't read real usage) and time is a cost/hang guard (wall-clock confounds provider throughput) — **neither is a capability signal**.
5. **Gate coverage is uneven across languages** (Rust/Java thinner; Go strong). Thin gates degrade honestly via a `coverage` note.

(The author's own model- + codebase-specific self-assessment — 13 caveats — lives in [maturity.md](skills/parallel-development/references/maturity.md); for reference. Your mileage varies with your LLM + project.)

## Arming a project (`/solidforge:arm-tools`)

Layer 2 setup — provisions the project-side files the gates + opt-in extensions need (the gate **substance**, not the enforcement — that's Layer 1, [enabling the plugin](#grading-your-own-runs)). Idempotent (safe to re-run) + never clobbers your existing files. `<project>` defaults to the current project.

| Invocation | What it provisions | Default? |
| --- | --- | --- |
| `/solidforge:arm-tools` (no flags) | • per-language arch-contract configs — **only for detected languages** (`.importlinter.ini` Python · `.dependency-cruiser.cjs` Web/TS · `.swiftlint.yml` Swift · `clippy.toml` Rust · `checkstyle.xml` Java · `.golangci.yml` Go; detection is recursive — a nested `frontend/`/`backend/` marker counts)<br>• Intent Blueprint templates → `docs/intent-blueprints/_templates/`<br>• L1 Constitution appended to `CLAUDE.md` (if absent)<br>• `.env.solidforge.example` (the different-family secrets placeholder — namespaced, no real tokens)<br>• `.gitignore` entries (`loop-state.json`, `runs/`, `.env`, `.env.solidforge`)<br>• an LSP + gate-status report (advisory; does NOT install language servers) | **yes — the default arming** |
| `--with-tools` | ALSO adds the gate dev-deps to the project's OWN package manager (ruff, import-linter, etc. — project-local, no global install) + the Gate-Toolchain note to `CLAUDE.md` | opt-in |
| `--with-tools --lang <python\|web\|rust\|swift\|java\|go>` | restrict `--with-tools` to ONE ecosystem (polyglot repos that want just one language's gate tools) | opt-in modifier |
| `--scaffold-configs [vale,semgrep,spectral]` | ALSO copies external-tool config templates (`.vale.ini` / `.semgrep.yml` / `.spectral.yaml`); bare flag = all three; runs `vale sync` if `vale` is scaffolded **and** on `$PATH` | opt-in |
| `--revert [--apply]` | removes what arming added — ONLY files still byte-matching the template (your edits are KEPT + warned). DRY-RUN by default; `--apply` executes. Exclusive of `--with-tools`. | inverse |

Notes:

- **Most critical combination**: `/solidforge:arm-tools --with-tools` — default arming gives the rules (arch-configs); `--with-tools` gives the engines (gate dev-deps). Both are needed for the first-party gates (fast-gate, arch-contract, supply-chain, test) to actually fire. If your project already has the gate tools (e.g. ruff in `pyproject.toml`), bare `/solidforge:arm-tools` (rules only) suffices.
- `--scaffold-configs` scaffolds **Vale / Semgrep / Spectral** only. Checkov / OASDiff / Trivy arm by installing the tool + writing its config yourself (the gate auto-detects it).
- Re-run `/solidforge:arm-tools` after a plugin update to re-provision arch-configs / constitution / templates if the skill text changed (your edits are preserved).
- Thedifferent-family extension's `.env.solidforge.example` is provisioned by the default arming; `cp` it to `.env.solidforge` + fill tokens to opt into different-family (see [different-family below](#different-family-different-family-adversarial-review-the-orthogonal-axis-lever)).
- Full authoritative list: [install.md](skills/parallel-development/references/install.md) Layer 2.

## Opt-in extensions (adopt anytime)

These are **cross-cutting capabilities**, not rungs on any ladder — add whichever you need, in any order; none is a prerequisite for a grade. The external-tool gates are `warning`-level advisory (they surface findings, don't block convergence); Impeccable adds a per-edit advisory detector + a convergence sweep; different-family is an **outer-ring** adversarial review whose findings feed reconciliation (not a mere advisory).

### External tools (Vale / Semgrep / Spectral / …)

1. Install the tool (`brew install vale` / `pip install semgrep` / `npm i -g @stoplight/spectral-cli` / …).
2. Scaffold a starting config (or write your own): `/solidforge:arm-tools --scaffold-configs [vale,semgrep,spectral]` — bare flag = all three; when `vale` is scaffolded **and `vale` is on `$PATH`**, arming also runs `vale sync` to fetch the style packages (the Vale gate no-ops without them).
3. `/solidforge:arm-tools` provisions the rest (arch-configs, constitution, templates).

Then `implement …` as usual — the loop detects the committed config and runs the tool's gate alongside its own. All external gates are **advisory**; you decide whether to escalate.

| Tool | What it gates |
| --- | --- |
| Vale | docs prose (terminology, voice, spelling, inclusiveness) |
| Spectral | OpenAPI spec linting (style + best practices) |
| Semgrep | source SAST (OWASP top-ten, injection, weak-crypto) |
| Checkov | IaC misconfig (open buckets, privileged containers) |
| OASDiff | API breaking-change detection |
| Trivy | dependency license compliance inventory |

A tool that's absent skips with a coverage note — never a silent pass. `--scaffold-configs` scaffolds the **first three** (Vale / Semgrep / Spectral); Checkov / OASDiff / Trivy arm by installing the tool + writing its config yourself (the gate auto-detects it).

### Frontend with design governance (Impeccable)

1. One-time: `/impeccable init` → author a `DESIGN.md` (design tokens, component inventory, a11y targets).
2. Then either `author a spec for the checkout page, referencing @DESIGN.md` (bc treats DESIGN.md as an authority-chain entry), **or** `implement the checkout page` (pd's Intent Blueprint carries a `visual_ref` to DESIGN.md; its tokens flow into the NFR + visual acceptance criteria).
3. Or chain both: `DESIGN.md` → spec (bc) → implement (pd).

Code passes both the convergence gates **and** Impeccable's design-fidelity check.

### Heterogeneous-source (different-family) adversarial review (the orthogonal-axis lever)

The *why* is the [orthogonal axis](#the-orthogonal-axis--verification-source-decoupling-different-family) above — a cross-family second opinion defends the spec-gaming degradation same-family review cannot. The *how*:

1. Arm the project: `/solidforge:arm-tools` copies `.env.solidforge.example` (a namespaced placeholder — never collides with your own `.env.example`).
2. `cp .env.solidforge.example .env.solidforge` + fill the token(s) you need, e.g. `DEEPSEEK_ANTHROPIC_AUTH_TOKEN=sk-...`. The var name is a convention: `<UPPERCASE-PROVIDER>_ANTHROPIC_AUTH_TOKEN` (matches `profiles/<provider>.json`).
3. Run a one-shot adversarial review, or mark a plan item `hetero: on` so pd adds it per-item (`<plugin-root>` is where the Solid Forge plugin is installed — find it via `/plugin` or your plugin config):

```bash
python3 <plugin-root>/skills/parallel-development/infra/scripts/hetero_review.py \
  --diff <file-or-ref> --blueprint <blueprint-ref>
```

Omit `--profile` — the wrapper resolves the provider(s) from `HETERO_PROFILE` (`<project>/.env.solidforge` / env, comma-list = dual-different-family, default `deepseek`); a hardcoded `--profile` silently drops every other configured provider (ADR #48/#5).

Reconciliation: both sources report → high-confidence adopt; same-family-only → adopt; **different-family-only → strong signal, escalate**; neither → pass. The one-shot command above is one different-family leg; **multi-round debate is orchestrator-driven** (the orchestrator alternates same-family ↔ different-family legs, counting rounds via `loop_state`). A debate that hits the round cap without convergence is recorded by the orchestrator as `adversarial-stalemate` (via `loop_state`) and escalated to you — never silently picks a side. **Add a provider** with no code change: drop `profiles/<name>.json` + set `<UPPERCASE-NAME>_ANTHROPIC_AUTH_TOKEN`. **Dual-different-family**: `--profile deepseek,qwen3`. Decision anchor: ADR #40; policy: [model-routing.md](skills/parallel-development/references/model-routing.md).

## Under the hood (read when curious)

**The convergence loop, briefly.** Each item runs until both rings pass:

- **Inner ring** (deterministic): the **fast gate** (lint/format; format failures block with commit-stratified remediation — the pure-format change isolates into a standalone `style:` commit so the logic diff stays reviewable) is a PostToolUse hook that fires on **every edit**; at the **inner convergence point** the architecture-contract gate (layering / dependencies / concurrency) → supply-chain gate (leaked secrets + dependency vulnerabilities) → test gate (failing-test + AC→test-name mapping + coverage) → API-contract gate (frontend↔backend, mixed repos) run once. See [install.md](skills/parallel-development/references/install.md) "What each gate does" for the full set. A real violation blocks; a missing tool degrades to a coverage note (never a silent green).
- **Outer ring** (AI): an independent reviewer checks the diff against the frozen Intent Blueprint (use cases + acceptance criteria + NFR) — it catches drift an LLM can't see by reading code alone.

**Circuit breaker.** Distinct triggers, distinct actions (priority: hard-terminate > escalate > degrade > suspend): the same root-cause fingerprint ≥ N=3 → **escalate** (→ outer ring); inner iterations ≥ M=8 → **degrade** (→ narrow scope) → **suspend** (→ you) if budget ≥ 80%; **step cap → hard-terminate** (a *capability* signal — `step-capped` → `not-yet`); **token / time / cost cap → hard-terminate** (a *resource* guard — `resource-capped` → `inconclusive` on capability). A PreToolUse hook (`counters.py`) **DENIES** edits once the status is terminal — the loop cannot thrash past the breaker; it is a physical intercept, not a prompted suggestion.

**Blueprint drift → hard rollback + reverse-prompt injection.** If the Coder drifts from the original intent (hardcodes a value to pass a test, silently drops a use case), the outer ring catches it, rolls back to the last snapshot, **and injects a reverse prompt** (the lost use case + the error path that caused the drift) so the agent re-anchors on the original goal. The Intent Blueprint is read-only — it changes only through an explicit revision channel.

**Resume.** pd's runtime state is gitignored. If your session ends mid-convergence, re-entering resumes at the first non-converged item — no lost progress.

**Commit policy.** Default is `auto-per-stage` (one commit per converged stage on a feature branch, never `main`, no confirmation needed). Override with `loop_state.py init --commit manual` if you prefer to commit yourself.

## Quick reference

| You want | Prompt | Skill |
| --- | --- | --- |
| Code, single task | `implement …` | pd |
| Code from a plan | `implement feature X per @plan.md` | pd |
| A spec / arch-design / iteration-plan | `author a spec for …` | bc |
| Cross-review a doc to convergence | `cross-review this requirements doc @doc.md` | csr |
| Converge → specify → implement (with cross-review) | (1) `/cross-source-review converge @reqs.md` → (2) `/blueprint-crafting author a spec …` → (3) `/parallel-development implement …` | csr → bc → pd |
| Specified **and** implemented | (1) `/blueprint-crafting author a spec …` → (2) `/parallel-development implement per the frozen spec` | bc → pd |
| One-shot bc → pd (**skip spec review**) | `Using @ctx.md, have /blueprint-crafting produce a spec, then /parallel-development implement it` | bc → pd (no review — bc's assumptions ride through unchecked) |
| Code + external tool (Vale/Semgrep/…) | `/solidforge:arm-tools --scaffold-configs …` → `implement …` | pd + tool |
| Frontend with design governance | `/impeccable init` → `implement …` | pd + Impeccable |
| different-family (cross-family) adversarial review | `/solidforge:arm-tools` → fill `.env.solidforge` → `hetero_review.py …` (omit `--profile`; wrapper uses `HETERO_PROFILE`, default deepseek — or item `hetero: on`) | pd + hetero |
| Fix / refactor / tests / docs | `fix …` / `refactor …` / `write e2e tests …` / `document …` | pd |

---

*Solid Forge is a Claude Code plugin. Skills activate by description; invoke explicitly (`/cross-source-review`, `/blueprint-crafting`, `/parallel-development`, `/solidforge:arm-tools`) when reliability matters. Overview: [README.md](README.md); authoritative install + feature doc: [install.md](skills/parallel-development/references/install.md); maturity framework: [maturity.md](skills/parallel-development/references/maturity.md).*
