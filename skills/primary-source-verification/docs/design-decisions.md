# primary-source-verification — Design Decisions (ADR log)

> Non-obvious decisions (workspace rule 6). Context / Decision / Why / Rejected.
> Master authority: `proposal.md`; execution blueprint: `iteration-plan.md`.

## ADR #1 — psv is a single extract→fetch→verdict→coverage pipeline, NOT a same+异源 debate loop

- **Context:** csr (cross-source-review) converges a doc via same-family + different-family multi-round debate; its oracle for cited works is model recall + a different-family second opinion. psv's oracle is the FETCHED source text.
- **Decision:** psv is a single pipeline (extract → fetch → verdict → coverage). It does NOT port csr's heterogeneous `claude -p` substrate and has no debate loop / cap / stalemate.
- **Why:** the oracle is a fetched document, not a model. The decoupling comes from the source being externally authored (§4.1 decoupling criterion), not from a different model family. A debate loop would add cost without changing the oracle.
- **Rejected:** (a) mirror csr's two-leg loop — wrong oracle type; (b) port csr's hetero substrate — would inherit an LLM-token surface psv doesn't need (see ADR #4).

## ADR #2 — the fetched-quote invariant is a STRUCTURAL-PROXY gate, not a semantic proof

- **Context:** the load-bearing honesty rule is "a refuted/narrowed finding MUST cite a fetched-source quote; a quote-less one is downgraded to `claim-unverifiable`."
- **Decision:** `fetched_quote_gate.py` / `enforce_fetched_quote` check a structural proxy (evidence non-empty AND contains a quote marker — a `"`, a `'` of sufficient length, or `fetched`/`source:`). A model could fabricate a quote that passes the proxy.
- **Why:** JSON/python cannot semantically prove a quote is genuine. The proxy catches the "no quote at all" case (the common failure), and its limit is DISCLOSED in the coverage-record's `coverage` notes (rule 3: never silently green). This matches csr's gate honesty posture.
- **Rejected:** (a) no check (silent green — violates rule 3); (b) require a verifiable byte-range into the fetched blob — out of Phase-A scope, fragile across source formats.

## ADR #3 — `coverage-record` is a SEPARATE schema; `correctness_converged` is forbidden

- **Context:** psv's top-line signal is `oracle_verified_under_known_coverage` (N/R/W/K of M), not a boolean.
- **Decision:** a separate `coverage-record.schema.json` (analogous to csr's split: doc-findings for per-claim defects vs convergence-record for the verdict). `signal` is a `const`, `rightness` is a `const: human_confirm_required`, and `additionalProperties: false` + the policy gate make `correctness_converged` unrepresentable.
- **Why:** the category error the spec-gaming paper §3.3 names is flattening process + outcome into one boolean; the schema must make that flattening structurally impossible, not merely discouraged.
- **Rejected:** a single combined object with a `converged: true/false` field — exactly the category error.

## ADR #4 — psv's credential surface is NOT csr's `_ANTHROPIC_AUTH_TOKEN` namespace

- **Context:** proposal §8 said "provider-token isolation per the csr install.md pattern"; outer-ring novel-1 caught that csr's pattern targets csr's heterogeneous LLM substrate, which psv disclaims.
- **Decision:** open sources are fetched credential-free (stdlib `urllib`); paywalled (401/403) → NOT fetched, claim returned `unverifiable`; the claim-vs-text comparison runs in the same-family Claude runtime (no isolated LLM token). Any future paywalled-fetch credential is a separately-named HTTP surface.
- **Why:** csr's `_ANTHROPIC_AUTH_TOKEN` suffix scopes a credential to csr's Anthropic-gateway substrate; psv has no such substrate. Inheriting the namespace would imply a surface that doesn't exist.
- **Rejected:** inherit csr's token-isolation verbatim — the precondition (a `claude -p` substrate) does not hold.

## ADR #5 — M=0 escalation is DISTINCT from K>0

- **Context:** the degenerate case — a doc with zero source-admissible claims (purely interpretive) — yields N=R=W=K=0; the sum invariant holds trivially and "0 verified of 0" can be misread as a silent green ("perfect verification").
- **Decision:** `build_coverage` emits a dedicated escalation "no source-admissible claims extracted — psv has no surface on this artifact" when M=0, distinct from the per-claim K>0 escalations. `coverage_policy_check.py` exercises both.
- **Why:** "psv had no surface" ≠ "psv verified everything." Conflating them is a silent-green anti-pattern (rule 3).
- **Rejected:** treat M=0 as a vacuous pass.

## ADR #6 — `claim-unverifiable` KIND ≠ `coverage-gap` KIND ≠ `coverage` SEVERITY

- **Context:** three "could not" notions collide: a claim no source can settle, a missing section in the artifact, and a reviewer's own disclosure.
- **Decision:** `claim-unverifiable` is a KIND (a claim the fetched source could not adjudicate — escalate); csr's `coverage-gap` is a KIND (a missing-section defect in the artifact); `coverage` is a SEVERITY (the reviewer's honest "could not verify X"). The three are distinguished in the schema description, the kind description, and the severity description.
- **Why:** conflating them would let a per-claim "could not adjudicate" hide as a structural defect or vice versa, weakening the honesty contract.
- **Rejected:** reuse csr's `coverage-gap` kind for unverifiable claims — conflates the two.

## ADR #7 — the same-family legs are plugin-level agents (repo-root `agents/`), not skill-internal

- **Context:** psv needs fresh-context same-family agents (claim-extraction, claim-verifier) to avoid orchestrator bias.
- **Decision:** `agents/claim-extractor.agent.md` and `agents/claim-verifier.agent.md` live at the repo-root `agents/` (registered as `solidforge:claim-extractor` / `solidforge:claim-verifier`), mirroring csr's `solidforge:doc-reviewer`.
- **Why:** that is the established solidforge plugin convention (rule 7); skill-internal `agents/` is optional and csr does not use it for its leg.
- **Rejected:** skill-local `skills/primary-source-verification/agents/` — diverges from the csr exemplar with no benefit.
