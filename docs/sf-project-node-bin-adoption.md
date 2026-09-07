# SF_PROJECT_NODE_BIN adoption — pi 0.2.7 handoff verified, CC implementation plan

- Provenance: verifies + adopts `solidforge-pi/docs/outflow/sf-project-node-bin-handoff.md` (pi 0.2.7 → CC, 2026-09-04).
- Verification session: 2026-09-04, against CC HEAD `489b217` ("security: PATH-only tool resolution + fail-closed loop_state").
- csr round 1 (same-family leg, 2026-09-04): 7 findings — 2 blockers (incomplete CC site inventory; a second un-gated private venv executor in `arch_contract_python.py` — both in section 2.2's scope), 3 warnings, 2 notes; all 7 fixed in that revision. The round-1 site sweep found 3 ad-hoc resolution sites the session's own sweep missed (credited per-site below).
- csr round 2 (same-family leg, 2026-09-04): 6 findings — 1 blocker (pi-side site enumeration undercounted: pi carries site 1 too, so ALL SEVEN sites are pi-carried), 4 warnings (tsc docstring over-attribution; pi anchor range; site-7 shape generalization; argument-hint phrasing), 1 note (provenance gloss); all 6 fixed in that revision.
- csr round 2 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-04): verdict pass; 1 coverage finding (live-repro rows not captured) — resolved by re-executing the reproduction and capturing the transcript to evidence/.
- csr round 3 (same-family leg, 2026-09-05): 4 findings — 1 blocker (stale status line contradicting the run records), 2 warnings (live-repro transcript label broader than its content — the TODAY-split is code-anchored, not transcript-exercised; npx `--no-install` delegation arm un-gated, contradicting A3's closure claim), 1 note (sweep-scope certainty); all 4 fixed in that revision (the npx fix materially strengthened T2/A3/section 4/ADR obligations).
- csr round 3 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-05): verdict pass; 3 warnings — one independently verified FALSE and REJECTED (claimed site-7 path-prefix drift; the quoted text does not exist in the doc — the run's first hetero rejection), two fixed (section 2.4 enumeration aligned to A7's 5 docs; acceptance probes generalized toward all seven sites).
- csr round 4 (same-family leg, 2026-09-05): 5 findings — 1 blocker (status line stale again — the r3 different-family leg ran and its fixes are in the doc, but the status still said pending and the provenance block omitted the leg), 3 warnings (pi site-2 anchor under-covers the npx arm; section 4 header still said "unchanged" though the npx bullet is new; acceptance enumeration named probes for only 6 of 7 sites — site 3 missing), 1 note (row 5 path convention); all 5 fixed in that revision.
- csr round 4 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-05): verdict pass; 3 warnings (fast_gate canonical scope under-represented in row 4's TODAY-split — python/rust/java/go branches all route canonical; "complete inventory" vs disclosed scope; acceptance's "matching opt-in" unmapped per site) all fixed, 1 coverage (monorepo nested node_modules vs containment) clarified in section 4.
- csr round 1 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-04): verdict rewrite; 3 findings — 1 blocker ("gates refuse" imprecision, section 2.1 row 4), 1 warning (T3 `root` threading unspecified against CC's `resolve_tool(name)` signature), 1 coverage (cross-repo + web evidence not captured). Both defects independently verified against source by the orchestrator and fixed; the coverage finding is addressed by the evidence capture below.
- Evidence capture (rule 3 — cross-repo and web claims are stated honestly, not silently green): pi-side claims verified against the pi repo working tree at commit `9a3b4a5` (hash recorded in the run record); the pi test file, the fetched CC-docs excerpt, and the section-2.1 live-reproduction transcript are captured under `workspace/cross-source-review/runs/20260904-node-bin-adoption/evidence/` (gitignored run artifacts; the hash lives at `evidence/pi-commit.txt` and is re-stated in the convergence-record this run emits at its end). A reviewer without pi-repo or web access can audit those captures.
- Pipeline for this doc: author → cross-source-review (csr) → parallel-development (pd). psv gate NOT triggered (rule 13): load-bearing claims cite predominantly LOCAL code anchors; the one external citation (CC docs) is quoted verbatim below with fetch provenance.
- csr round 5 (same-family leg, 2026-09-05): ZERO blockers; 1 warning (java branch's "refuse" not strictly terminal — the explicit `GOOGLE_JAVA_FORMAT_JAR` env fallback at `fast_gate.py:173-176` is opt-in-like, outside A3's class) + 1 note (r1 hetero verdict `rewrite` unstated) — both fixed.
- csr round 5 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-05): verdict rewrite; 1 blocker ("ALL gates refuse only post-A2/A3" conflated A2's report-alignment with A3's gate-execution routing — AND/OR ambiguous, the OR reading false; fixed to separate the two), 1 warning (pi test file missing from section 8; fixed), 1 coverage REJECTED (requested CC-docs excerpt capture — already in place since round 1).
- Cap extension: the declared cap of 5 was reached with blocker history 3→1→1→1→1 (no two consecutive blocker-free rounds; core-claims coverage-verified satisfied — "core claims" = section 2.1's verification-table rows, the section 2.2 seven-site inventory, and the section 2.3-2.4 corrections; "coverage-verified" = each was checked by the review legs against source code, the pi tree, or the captured evidence, with residual unverifiables disclosed in the run record's coverage notes). Per the cap-hit escalation protocol (csr SKILL.md's convergence judgment: hitting the round cap without convergence escalates the decision to the human, never a silent pick) the human elected to extend to cap=7 to pursue the formal 2-clean-round streak (substantive convergence = ≥2 consecutive rounds with no new Blocker-class finding) — no further extension; the run accepts whatever state round 7 ends in.
- csr round 6 (same-family leg, 2026-09-06): ZERO blockers; 1 warning (forward reference — "the convergence-record carries the hash" before the record exists) + 2 notes (additive reading of "site 1 and the seven"; section-1 short path vs convention) — all 3 fixed.
- csr round 6 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-06): verdict pass; 3 warnings (swift branch unmentioned in row 4; "VERBATIM" overstates line-number identity; cap-extension terms unglossed) — all 3 fixed. Round 6 is the first fully blocker-free round: streak 1 of 2.
- csr round 7 (same-family leg, 2026-09-06): ZERO blockers; 2 warnings (the "ALL gate-execution sites" inclusive reading captured swift, which refuses today; "local-first" in the 2.2 heading + A3 row over-generalized for site 7) — both fixed.
- csr round 7 (different-family leg, minimax-cn / MiniMax-M3, 2026-09-06): verdict pass; 1 warning (section-8 pi path prefix dropped for sites 2-7) + 1 coverage (core-claims gloss lacked the concrete enumeration) — both fixed. Round 7 fully blocker-free.
- Status: **IMPLEMENTED** (2026-09-06) — csr SUBSTANTIVE-CONVERGED (rounds 6-7 blocker-free; blocker history 3-1-1-1-1-0-0), then pd plan-driven execution converged 6/6 items (T1-T6, per-item dual-ring, 14/14 self-gate battery green; queue: `docs/plan-queues/node-bin-adoption.queue.md` v2). ADRs #63-#66 recorded. Execution surfaced four consistency-completion legs beyond the plan's seven sites (tests-gate pytest/coverage; deps-gate pip-audit/govulncheck — the report-vs-gate agreement class; pinned by the site-8 probes in `detect_toolchain_test.py`, 26/26). csr record: `docs/sf-project-node-bin-adoption.csr-record.json`. Outcome axis remains human — `rightness: human_confirm_required`. Commit: manual (repo rule 9).

## 1. Inflow source (what pi reported)

The pi port's handoff reports four adoption points, all verified in section 2:

- `resolve_tool` node branch: `SF_PROJECT_NODE_BIN=1` resolves `node_modules/.bin/<name>`, with a realpath containment hard stop; PATH always wins.
- `arm.py tool_present`: route through `resolve_tool` (single source of truth) — pi's version had reported tools "present" that the gates would refuse to execute.
- `$ARGUMENTS` wiring in the arm-tools prompt/command template — pi's renderer silently dropped invocation flags.
- Port the test file `infra/test/detect_toolchain_test.py` (skill-rooted path, the handoff's own wording; the pi source is the section-8 entry). The handoff says "6 cases"; the file actually executes 10 checks (csr round 1 recount): 7 in `main()` — PATH-only default; node opt-in resolves; in-tree `.bin` symlink resolves (the dominant npm shape; containment-regression sentinel); escaping symlink refused; PATH wins; venv resolves under opt-in; venv ignored without opt-in — plus 3 in `arm_tool_present_truth()` — absent without opt-in; present under opt-in; `root` threading when cwd ≠ target.

## 2. Verification findings (2026-09-04 session)

### 2.1 Confirmed claims

| Handoff claim | Verdict | Evidence |
|---|---|---|
| CC `resolve_tool` has NO node_modules resolution path (not even opt-in) | confirmed | `skills/parallel-development/infra/hooks/lib/detect_toolchain.py:73-95` — PATH, then venv branch under `SF_PROJECT_VENV_TOOLS=1`, nothing else |
| CC `arm.py tool_present` is its own unconditional venv scan (pi bug #2's shape) | confirmed | `skills/parallel-development/infra/install/arm.py:69-76` |
| `npm install -D` tools then arm.py reports `absent (gate degrades)` | reproduced live | temp project with executable `node_modules/.bin/eslint` → `tool_present`=False, report line "eslint (Web gate): absent (gate degrades)" |
| tool_present vs CANONICAL resolve_tool mismatch (venv tools) | reproduced live | temp `.venv/bin/lint-imports` → `tool_present`=True while the CANONICAL `hooks/lib/detect_toolchain.resolve_tool` returns None without opt-in (`[.../.venv/bin/lint-imports]` with `SF_PROJECT_VENV_TOOLS=1`). TODAY the gates are SPLIT: fast_gate's python/rust/go branches route through the canonical resolver (`fast_gate.py:45,159,191`) and refuse; its swift branch is strictly PATH-only (`which_any`, `fast_gate.py:60-61`) both today and post-adoption — never project-local, out of scope by construction; its java branch routes canonical first (`:172`) then falls back to the explicit user-configured `GOOGLE_JAVA_FORMAT_JAR` env channel (`:173-176`) — an explicit opt-in-like channel, not project-local auto-resolution; fast_gate's WEB branch (site 1 of the seven section-2.2 ad-hoc sites) and the OTHER SIX — including `arch_contract_python.py`'s private resolver — still execute unconditionally. the seven project-local-executing sites refuse only post-A3 (A3 routes them through the canonical resolver); A2 aligns the STATUS REPORT with the same contract |
| CC has no `detect_toolchain` test | confirmed | `skills/parallel-development/infra/test/` inventory has no such file; `489b217`'s fail-closed probe was manual, not committed |
| pi shipped what handoff §2 describes | confirmed (with one handoff miscount) | pi `resolve_tool` has the `SF_PROJECT_NODE_BIN` branch + containment + PATH-wins; pi `tool_present` routes through `resolve_tool`; pi `prompts/arm-tools.md` wires ARGUMENTS; handoff §2.4's "6 cases" is a miscount of the shipped 10-check file (section 1) |

### 2.2 Correction 1 — CC web/python gates are NOT blind to project-local bins; SEVEN un-gated project-local execution sites survive `489b217`

The handoff frames CC's exposure as "the only project-local resolution path was the removed fallback" → node tools invisible to gates. That framing is wrong for the GATE EXECUTION paths, and the reality is MORE severe than the reported issue: those gates never routed through `resolve_tool` at all. Six of the seven sites below prefer `node_modules/.bin` over PATH; site 7 tries PATH first, then unconditionally executes project-venv binaries. None has an opt-in; none has containment. These are live instances of the execute-repo-committed-binaries class that `489b217`'s commit title ("PATH-only tool resolution") claims closed. (The handoff's invisibility framing DOES hold for arm.py's STATUS REPORT until A2 lands — section 2.1 row 3; the two directions are distinct.)

Inventory — complete within the sweep scope disclosed below — (swept by the verification session AND independently by csr round 1; "r1" = found by the csr round-1 same-family leg, missed by the session's own sweep):

| # | Site | Shape | Found by |
|---|---|---|---|
(Path convention: sections 1-4 cite repo-rooted paths; section 5 task bullets cite skill-rooted short paths under `skills/parallel-development/`.)
| 1 | `skills/parallel-development/infra/hooks/fast_gate.py:217-218` | eslint: local `node_modules/.bin` WINS over PATH | session |
| 2 | `skills/parallel-development/infra/scripts/arch_contract_web.py:70-78` | `depcruise_cmd`: local first, then PATH, then `npx --no-install` | session |
| 3 | `skills/parallel-development/infra/scripts/arch_contract_web.py:167-171` | eslint: local first | session |
| 4 | `skills/parallel-development/infra/scripts/arch_contract_web.py:202-207` | `_resolve_tsc`: local first | session |
| 5 | `skills/parallel-development/infra/scripts/arch_contract_tests.py:575-587` | `_resolve_vitest`: local first; docstring declares it MIRRORS `_resolve_tsc` | r1 |
| 6 | `skills/parallel-development/infra/scripts/spectral_adapter.py:124-133` | `resolve_spectral`: local first, then PATH; no npx fallback ("fetch-on-demand is NOT armed") | r1 |
| 7 | `skills/parallel-development/infra/scripts/arch_contract_python.py:83-97` | a SECOND private `resolve_tool`: PATH then UNCONDITIONAL `.venv/venv/env` scan (the pre-`489b217` shape, no opt-in at all); called at `:156` (`lint-imports`), `:192` (`pylint`), `:307` (`pyright`) | r1 |


Additional fact (verified against the pi repo): pi itself carries ALL SEVEN sites with the same resolution shapes — code identical at each anchor (verified at anchor granularity, no full-file byte diff); absolute line numbers shift slightly between the trees (e.g. site 1 at pi `fast_gate.py:215-216` vs CC `:217-218`) — site 1 at `solidforge-pi/.../hooks/fast_gate.py:215-216`; sites 2-7 as listed above, at the section-8 anchors — pi 0.2.7 fixed `resolve_tool` + `arm.py` + the prompt wiring only; it never collapsed its own gates' ad-hoc resolution. The residual hole is a blind spot BOTH repos share, not a pi-fixed feature awaiting a CC port. Item A3 below is therefore novel scope on both sides (and a candidate reverse-outflow note to pi after this lands).

Behavior-change note for sites 4-5: `_resolve_vitest`'s docstring justifies local-first by version coupling (the project's PINNED vitest must run — v1/v2/v3 config APIs differ, a PATH copy would version-diverge, and a devDep-only install without local resolution would false-skip); `_resolve_tsc`'s docstring states only the local-first order, no rationale. The same version-coupling concern applies to tsc as a matter of fact. Collapsing both into the PATH-wins + opt-in contract deliberately supersedes the pinned-version preference — see the trade-off recorded in section 6's ADR obligations.

Sweep scope: `skills/parallel-development/infra/` (hooks, scripts, install, tests) only; an independent round-3 grep corroborated completeness (all resolution-shape hits fall under parallel-development). The other skills (blueprint-crafting, cross-source-review, primary-source-verification) were spot-checked by grep only (no matches), not fully swept — stated as evidence-backed, not proven.

Consequence for this plan: adopting pi's resolve_tool node branch on CC is not merely a capability add — routing all seven ad-hoc sites through `resolve_tool` (plus gating the `npx --no-install` delegation arm, which reaches the same project-local binaries through npx's local-first semantics) closes the un-gated execution channels AND establishes the visibility contract the handoff wants. The adoption rationale is stronger than the handoff's own.

### 2.3 Correction 2 — the `$ARGUMENTS` silent-drop does not apply on CC

- Shape confirmed: `commands/arm-tools.md` contains zero `$ARGUMENTS` occurrences (the frontmatter's only argument-channel key is `argument-hint`; the body's "If the user passed `--with-tools`..." instruction has no declared channel for the typed flags).
- Behavior NOT a silent-drop on CC: current Claude Code appends typed arguments implicitly. Official docs (https://code.claude.com/docs/en/slash-commands, substitutions table; fetched 2026-09-04 by the verification session, quote verbatim): "`$ARGUMENTS` — All arguments passed when invoking the skill. When no placeholder receives an argument, Claude Code appends them as `ARGUMENTS: <value>`."
- Verdict: pi's silent-drop was its `substituteArgs` renderer's behavior. On CC this item downgrades from bug fix to optional hardening (explicit declaration makes the channel visible to reviewers and guardable by a layout assertion).

### 2.4 Side findings beyond the handoff

- `--lang` enum drift: `commands/arm-tools.md:3` (argument-hint) and `:20` enumerate `python|web|rust|swift|java` — missing `go`, which `arm.py:1254` (`known_langs`) and the `arm.py` docstring both support.
- Facade-doc gap predating this adoption: `SF_PROJECT_VENV_TOOLS` appears ONLY in `detect_toolchain.py` — README (both languages), USER_GUIDE (both languages), and `references/install.md` never mention it. `489b217` shipped a user-visible opt-in without its rule-5 doc-audit pass. This adoption must document BOTH env vars.

## 3. Decision — what CC adopts

| # | Item | Source | Priority | Rationale |
|---|---|---|---|---|
| A1 | `resolve_tool` node branch: `SF_PROJECT_NODE_BIN=1` + realpath containment + PATH-wins | handoff §2.1 | P1 | capability + trust contract, mirrors pi exactly |
| A2 | Route `arm.py tool_present` through `resolve_tool` | handoff §2.2 | P1 | fixes both status mismatches (node absent-vs-installed; venv present-vs-refused) |
| A3 | Collapse the SEVEN ad-hoc project-local resolutions (section 2.2 inventory: six local-first node sites + site 7's PATH-then-unconditional-venv) into `resolve_tool`, and gate the `npx --no-install` delegation arm under the same opt-in | NEW, beyond handoff AND beyond pi's own landed state | P1 | closes the direct-resolution sites AND the npx delegation channel of the execute-repo-committed-binary hole `489b217` missed (and pi's 0.2.7 equally missed); single source of truth |
| A4 | Port `detect_toolchain_test.py` (10 checks, section 1 enumeration) + CC-specific extensions | handoff §2.4 | P1 | deterministic coverage for A1-A3 |
| A5 | `$ARGUMENTS` explicit wiring in `commands/arm-tools.md` + a `plugin_layout.py`-style assertion | handoff §3 (downgraded) | P3 | no live bug on CC (section 2.3); robustness + guardability only |
| A6 | Fix `--lang` enum drift (`go`) in `commands/arm-tools.md:3,:20` | session finding | P3 | ride-along doc fix |
| A7 | Document both env vars in README, README.zh-CN, USER_GUIDE, USER_GUIDE.zh-CN, `references/install.md` | session finding (rule 5) | P2 | closes the pre-existing `SF_PROJECT_VENV_TOOLS` doc gap; ships the new opt-in documented |

Intended user-visible behavior change (callout for A2): a tool present ONLY in `.venv/bin` (or, post-A1, `node_modules/.bin`) now reports `absent (gate degrades)` unless the matching opt-in env is set — the report states what the gates can actually execute, matching pi fix #2's semantics.

## 4. Trust model (carried from handoff §4; the npx bullet below is new — csr round 3)

- Opt-in envs are a per-project, per-user trust statement: "I run gates in this repo and accept that its devDependencies define gate tooling."
- Default stays PATH-only everywhere; PATH always wins over both opt-in branches.
- Containment applies to the node branch only: a `.bin` entry whose realpath escapes `node_modules/` is refused even under the opt-in. Resolution only ever probes `<root>/node_modules/.bin/<name>` — nested workspace `node_modules` are never resolved by the gate path (out of scope by construction, not refused by containment); containment's only effect is refusing root `.bin` entries whose realpath escapes the root `node_modules/` (e.g. a symlink into a workspace package or a global store).
- The venv branch keeps no equivalent check deliberately (venv entries are conventionally real files, not symlinks; matches 0.2.4 semantics) — noted asymmetry.
- Residual TOCTOU (exists → realpath → spawn swap window) is accepted, informational: the threat model is repo-committed content, not a concurrent local process.
- npx delegation (`npx --no-install`) is opt-in-gated like direct local resolution: npx reaches the same project-local binaries via its own local-first semantics (a PATH TOOL is not PATH RESOLUTION). Under the opt-in, npx's internal behavior is an accepted informational residual.
- POSIX layout only; Windows `Scripts\`/`.cmd` shims out of scope, as in 0.2.4.

## 5. Task breakdown for pd

- T1 (A1): `infra/hooks/lib/detect_toolchain.py` — add the node branch to `resolve_tool` mirroring pi's post-0.2.7 implementation (diffable directly against `solidforge-pi`); containment = realpath under `<root>/node_modules/`; PATH wins. Also adopt pi's signature `resolve_tool(name, root=None)` (CC's current `resolve_tool(name)` takes no root; `root=None` → current `project_root()` behavior, so existing callers are unaffected).
- T2 (A3): collapse all seven section-2.2 sites into `dt.resolve_tool`:
  - `infra/hooks/fast_gate.py` `check_web` (lines 217-218) — eslint.
  - `infra/scripts/arch_contract_web.py` — `depcruise_cmd` (lines 70-78), eslint (lines 167-171), `_resolve_tsc` (lines 202-207).
  - `infra/scripts/arch_contract_tests.py` — `_resolve_vitest` (lines 575-587).
  - `infra/scripts/spectral_adapter.py` — `resolve_spectral` (lines 124-133).
  - `infra/scripts/arch_contract_python.py` — delete the private `resolve_tool` (lines 83-97); import the `hooks/lib/detect_toolchain` one for `lint-imports`/`pylint`/`pyright` (callers at lines 156, 192, 307).
  - Preserve each site's existing degrade path (coverage note, no silent green) when resolution returns None. The `npx --no-install` fallback in `depcruise_cmd` is NOT PATH-family resolution: npx delegates with its own local-first semantics and executes a project-local binary when one is installed, without the opt-in — gate that arm behind `SF_PROJECT_NODE_BIN=1` as well; without the opt-in, degrade to the existing coverage note instead of delegating. spectral keeps "npx fetch-on-demand is NOT armed" semantics.
- T3 (A2): `infra/install/arm.py` `tool_present` — import + call `resolve_tool(name, root=project_dir)` (the `root` kwarg added in T1; no env-var mutation, no cwd dependence), drop the private venv scan.
- T4 (A4): port pi's 10-check `detect_toolchain_test.py`; extend with CC-specific cases covering the seven collapsed sites — including the in-tree `.bin` symlink resolve case (the dominant npm shape; guards the containment from regressing into a blanket refusal) and a probe that `arch_contract_python.py` no longer executes a planted `.venv/bin/lint-imports` without `SF_PROJECT_VENV_TOOLS=1`.
- T5 (A7): document `SF_PROJECT_VENV_TOOLS` + `SF_PROJECT_NODE_BIN` in the five facade/reference docs listed in A7; state the PATH-wins + containment contract, the report-semantics change, and the tsc/vitest pinned-version note (set the opt-in so the project's pinned versions run).
- T6 (A5, A6): `commands/arm-tools.md` — wire `$ARGUMENTS` explicitly near the top with a parse instruction; add `go` to both `--lang` enumerations; extend `plugin_layout.py` with the wiring assertion.
- Acceptance: full pd self-gate suite green (rule 1 list) + the ported/extended test file green; planted-binary probes for EACH of the seven collapsed sites (and the gated npx arm) — ignored by the gates without the matching opt-in, honored under it (the `489b217` manual probe, now committed as tests). Opt-in mapping: sites 1-6 + the npx arm gate on `SF_PROJECT_NODE_BIN=1`; site 7 (and the venv half of the canonical resolver) gates on `SF_PROJECT_VENV_TOOLS=1`. The named anchors are the minimal regression set: `node_modules/.bin/eslint` (exercises BOTH site 1 fast_gate and site 3 arch_contract_web's concurrency check, which resolve the same path), `.venv/bin/ruff` (resolve_tool), `.venv/bin/lint-imports` (arch_contract_python — the site-7 probe); T4 extends the remaining site probes (depcruise / tsc / vitest / spectral — sites 2, 4, 5, 6).

## 6. ADR obligations (rule 6 — record during implementation)

- ADR (next free number): adopting BEYOND the handoff's scope AND beyond pi's landed state — collapsing the seven ad-hoc resolutions (A3) is a security-driven scope extension the handoff does not ask for and pi itself has not done; rejected alternative: port A1 only and leave the gate sites ad-hoc (leaves the hole open on both repos).
- ADR: uniform PATH-wins for version-coupled tools — collapsing sites 4-5 supersedes the pinned-version local-first preference (documented in `_resolve_vitest`'s docstring; factually applicable to tsc as well); under the contract, the project's pinned tsc/vitest runs when the user sets `SF_PROJECT_NODE_BIN=1` (and no PATH copy shadows it). Rejected alternative: keep a version-coupling local-first exception for sites 4-5 (a permanent trust-model hole at exactly two sites, and the exception would re-open the class the fix closes).
- ADR: gating the `npx --no-install` delegation arm under `SF_PROJECT_NODE_BIN` (csr round-3 finding) — a PATH tool is not PATH resolution; npx executes project-local binaries with its own local-first semantics. Rejected alternatives: (a) keep the arm un-gated as "PATH-family" (classification error — re-opens the exact class A3 closes whenever PATH lacks the tool but a repo-local install exists); (b) drop the arm entirely (loses the npx-cache reach for opted-in users for no security gain once gated).
- ADR: `$ARGUMENTS` wired for robustness, not as a bug fix (section 2.3); rejected alternative: skip A5 as dead weight (leaves the channel undeclared and unguardable).

## 7. Non-goals

- Windows `Scripts\`/`.cmd` shim support.
- Containment for the venv branch.
- Eliminating the TOCTOU residual.
- Changing `SF_PROJECT_VENV_TOOLS` semantics or the loop_state fail-closed behavior from `489b217`.

## 8. Sources

- Handoff: `solidforge-pi/docs/outflow/sf-project-node-bin-handoff.md` (pi 0.2.7).
- CC commit under review: `489b217` (this repo, HEAD at verification time).
- Claude Code substitutions doc: https://code.claude.com/docs/en/slash-commands (quoted in section 2.3).
- pi landed implementation: `solidforge-pi/skills/parallel-development/infra/hooks/lib/detect_toolchain.py`, `solidforge-pi/skills/parallel-development/infra/install/arm.py`, `solidforge-pi/skills/parallel-development/infra/test/detect_toolchain_test.py` (the 10-check file T4 ports), `solidforge-pi/prompts/arm-tools.md` (repo-root `prompts/`, NOT under `skills/parallel-development/`). pi's own un-collapsed gate sites — ALL SEVEN, evidence for section 2.2's both-repos claim (paths under `solidforge-pi/skills/parallel-development/`): `hooks/fast_gate.py:215-216` (site 1), `infra/scripts/arch_contract_web.py:70-78,167-171,202-207` (sites 2-4, ranges matching the section-2.2 shapes incl. the npx arm), `infra/scripts/arch_contract_tests.py:575-587` (site 5), `infra/scripts/spectral_adapter.py:124-133` (site 6), `infra/scripts/arch_contract_python.py:83-97` (site 7).
