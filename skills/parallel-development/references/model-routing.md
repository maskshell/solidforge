# Model routing — per-stage provider policy

> Single source of truth for WHICH model family runs at WHICH stage of the convergence loop. Authority: ADR #40 (`design-decisions.md §40`) + the operational plan (`docs/hetero-orchestration-proposal.md §3`). On conflict, ADR #40 wins.

## Routing policy (per stage)

| Stage | Mode | Provider (example) | Always? | Role |
| --- | --- | --- | --- | --- |
| author (main orchestrator) | interactive CC, unchanged | GLM 5.2 (BigModel) | yes | deep reasoning + format-reliable; no added risk |
| adversarial review (same-family) | in-process Agent tool | GLM (primary) | **yes (primary)** | fast, cheap, Claude-grade tool discipline, reliable floor |
| adversarial review (different-family) | non-interactive subprocess (`hetero_review.py`) | DeepSeek v4 pro | **opt-in (high-stakes)** | adversarial second opinion; cross-family blind-spot check |
| research (researcher / Explore fan-out) | non-interactive subprocess or tier | DeepSeek flash / GLM-4.7 | as needed | fan-out; cost-dominated |
| normalize / constraints-check / freeze / fast_gate / arch-contract | deterministic code | — (no model) | — | model-independent |
| inner-ring Coder (GREEN) | same-family (default) | GLM | yes | highest tool-call-reliability risk (Morph caveat); consider different-family LAST |

## different-family priority

**reviewer > research > Coder.** The reviewer is the safest different-family entry point (read-only + structured findings, narrow tool surface, tolerable occasional malformation). The inner-ring Coder carries the highest tool-call-reliability risk and is the LAST different-family candidate — it is same-family by default.

## Research-tier routing (Phase 3, P3-1)

The research / Explore fan-out tier is cost-dominated (multi-source gathering, broad read) — a cheap backend is the right tier. Route it to DeepSeek flash by reusing the SAME non-interactive-CC substrate as the different-family reviewer (proven by `hetero_review.py` Phase 1):

```bash
claude -p --settings profiles/deepseek.json --model flash \
  --output-format json --permission-mode bypassPermissions \
  --no-session-persistence --max-budget-usd <cap> \
  --allowedTools "WebSearch WebFetch Read Grep Glob" \
  -p "<research prompt>"
```

Notes:

- This is NOT a new engine — it reuses the profiles/deepseek.json provider config + the `claude -p` spawning pattern. The orchestrator spawns it directly for research fan-out (analogous to how it spawns `hetero_review.py` for the different-family review).
- The research prompt is NOT adversarial (unlike the reviewer) — it gathers + cites. Trust/provenance on research findings stays the blueprint-crafting `research_constraints.py` oracle (sources-cited / staging / cost-bounded), NOT the cheap backend's judgment.
- The per-item binding (WHICH plan-queue items route research to the cheap backend) is the Phase 3 P3-2 `hetero` hint on plan-queue items.
- Reliability caveat: the cheap-backend tool-call reliability on research tools (WebSearch/WebFetch) is a measured-by-dogfood property, not assumed (the Morph caveat, generalized from the reviewer tier).

## Opt-in trigger (the different-family reviewer)

The different-family reviewer runs ONLY on high-stakes items; default items pay zero added cost (same-family only). The trigger conditions (ADR #40 (b)):

- ADR-level decisions.
- security- or correctness-sensitive diffs.
- a same-family verdict that is partially-satisfied or low-confidence.

This trigger list is the ADR #40 (b) prose — a **human-judged classifier, NOT an automated one**. The orchestrator (interactive CC) decides per item; there is no deterministic gate that forces different-family. Per-item automation (a `hetero` hint on plan-queue items) lands in Phase 3 (P3-2) and is itself a recommendation the human judge can override.

## Substrate

different-family runs as a non-interactive Claude Code subprocess spawned by `infra/scripts/hetero_review.py`:

```bash
claude -p --settings profiles/<backend>.json --model <alias> \
  --output-format json --json-schema <violation-log.schema.json> \
  --permission-mode bypassPermissions --no-session-persistence \
  --max-budget-usd <cap> [-p "<adversarial prompt>"]
```

The subprocess inherits SKILL.md / hooks / Skills / MCP — the skill substrate is NOT stranded. Provider config is process-level (`--settings`), so the different-family backend crosses providers without an aggregator proxy. The wrapper drives `loop_state` truthfully around the subprocess (ADR #39, ADR #40 (g)). See [convergent-loop.md](convergent-loop.md) § different-family adversarial review for the multi-round debate loop + cap + termination semantics.

**Provider profile + API key** (provider-template + token-injection pattern):

- `profiles/<provider>.json` (committed templates — `deepseek`, `bigmodel`, `qwen3`, `minimax`, ...). Each carries ROUTING ONLY (`ANTHROPIC_BASE_URL` + model aliases) — NO `ANTHROPIC_AUTH_TOKEN` field, NO `${...}` ceremony.
- **Token var = convention**: `<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN` — `deepseek` → `DEEPSEEK_ANTHROPIC_AUTH_TOKEN`, `qwen3` → `QWEN3_ANTHROPIC_AUTH_TOKEN`, `openai-compat` → `OPENAI_COMPAT_ANTHROPIC_AUTH_TOKEN`. Override the name via the template's optional `_token_env` (rarely needed).
- The token is NOT in the profile. Set it in your shell (`export DEEPSEEK_ANTHROPIC_AUTH_TOKEN=...`), in the arm-provisioned `.env.solidforge` (shell wins), or in your app `.env`. The wrapper reads all three (`shell > .env.solidforge > .env`), INJECTS the token as `ANTHROPIC_AUTH_TOKEN` into a throwaway chmod-600 temp settings file, passes it to `claude -p`, and unlinks it (Claude Code does NOT expand `${VAR}` itself — verified CC v2.1.201). `cp .env.solidforge.example .env.solidforge` to start (the `.example` is committed; `.env.solidforge` is gitignored).
- **Namespace isolation (sole source)**: the `_ANTHROPIC_AUTH_TOKEN` suffix is the ONLY var the wrapper reads for a provider's token. The provider's native `<FILENAME>_API_KEY` (e.g. `DEEPSEEK_API_KEY`) is NEVER read — it may be set in the same env for a different tool/SDK (possibly a different key/quota), so reading it would risk a credential meant for another use. A project may carry both `DEEPSEEK_API_KEY` (its own native-SDK use) and `DEEPSEEK_ANTHROPIC_AUTH_TOKEN` (this substrate) without collision — by design. See the namespace-isolation ADR.
- **Provider selection**: `--profile deepseek` (a NAME, not a path) or `export HETERO_PROFILE=deepseek`. Default `deepseek`.
- **Add a provider** (zero code change): drop `profiles/<name>.json` with routing only + `export <UPPERCASE_NAME>_ANTHROPIC_AUTH_TOKEN=...` → `hetero_review.py --profile <name>` works. See `profiles/qwen3.json` for a worked example.
- **Dual-/multi-different-family** (extensibility): `--profile deepseek,qwen3` runs each backend independently and merges findings (omit `--profile` to fall back to `HETERO_PROFILE` from `<project>/.env.solidforge` / env, default `deepseek` — a hardcoded `--profile` silently drops other configured providers, ADR #48/#5) (each finding tagged with its `provider` for N-way reconciliation). Pick two providers NEITHER of which is the orchestrator's primary — e.g. in a GLM-orchestrated project, `deepseek` + `qwen3` (BigModel is same-family there, so it is not a true different-family in that project).
- Set `--budget-usd` with headroom (default 4.0, under the global 5.0 cap) — it is a runaway backstop, NOT real cost: for non-Anthropic backends the API returns tokens only (no price field), so CC's USD is structurally disconnected from provider spend (ADR #42; the earlier "over-reports vs DeepSeek cache-aware billing" framing, ADR #40 (h)(i), understated this to a DeepSeek quirk). The reliable provider-independent bounds are CC's turn limit + `step_cap_S`. A cold multi-tool review is token-heavy regardless, so keep headroom; if a review still trips the cap it DEGRADES (verdict stays pass/rewrite from the other providers; ADR #41), not rewrites.
- **Subprocess timeout**: `--timeout <seconds>` (default 600, or `$HETERO_TIMEOUT`). The opus-tier alias on a cold large diff (the deepseek profile maps `opus`/`sonnet` → `deepseek-v4-pro[1m]`, the 1M-context model) can exceed 600s and return a `hetero-subprocess-timeout` malformation. For a known-cold large review: raise `--timeout` (e.g. 1200–1800s) to keep the pro tier, OR drop to `--model haiku` (→ `deepseek-v4-flash`) for that call. Do NOT remap the profile alias to dodge a timeout — cold-start is transient (DeepSeek auto-caches ~99% after the first call; ADR #40 (h)(i)), and a global alias remap permanently sacrifices review depth on warm calls (ADR #43). Set `HETERO_TIMEOUT` in `.env.solidforge` to fix the cap per-project.

## Reconciliation (same-family + different-family findings)

| Findings | Action |
| --- | --- |
| both same-family + different-family report | high-confidence; adopt |
| same-family only | adopt (primary status) |
| different-family only | strong signal (cross-family independent find = same-family blind spot); escalate for adjudication |
| neither | pass |
| different-family DEGRADED (substrate error: budget/turn cap, provider overwhelm) | adopt the same-family primary (different-family contributed nothing); `degraded:true` + a persisted `hetero-degraded-<subtype>` fingerprint distinguish it from a clean pass (ADR #41) |

## Cost model

- Default item (low/medium risk): same-family reviewer only — zero added cost.
- Opt-in item (high-stakes): same-family + different-family × ≤ cap rounds + reconciliation.
- Deterministic stages, author, research: unchanged (same-family) except the opt-in research-tier routing (Phase 3, P3-1).

Note (ADR #42 / #41): `--budget-usd` is a runaway breaker, not an accounting figure — for non-Anthropic backends CC's `total_cost_usd` is structurally fictional (the API returns tokens, not price; the earlier "over-reports vs DeepSeek cache-aware billing" framing, ADR #40 (h)(i), was a DeepSeek-specific understatement of a general truth). It defaults to 4.0 (headroom under the global 5.0 cap); the reliable provider-independent bounds are CC's turn limit + `step_cap_S`; DeepSeek auto-caches (~99% hit rate via its own Context Caching — Phase 0 RESULT). A review that still trips the cap DEGRADES (`degraded:true`, persisted `hetero-degraded-error_max_budget_usd` fingerprint), not rewrites.

## Out of scope

- different-family as the PRIMARY reviewer (rejected — it would drop the reliability + cost floor; ADR #40 (b) Rejected).
- cap-hit silent-pick ("timeout → trust same-family") — rejected; cap-hit escalates to human (ADR #40 Rejected (f)).
- The inner-ring Coder as an different-family candidate before the reviewer + research tiers are proven.
