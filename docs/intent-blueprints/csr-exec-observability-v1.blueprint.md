---
blueprint_version: v1
frozen_at: 2026-09-16
task: csr-execution-observability
status: frozen
---

# Intent Blueprint — csr execution-process observability + session-scoped run pointers

Origin: 2026-09-15 live csr run (`workspace/cross-source-review/runs/20260915-150240-coding-pass-protocol`,
round 12+ after stalemate extensions) exposed two gaps negotiated with the user over
three turns. (a) Observability is TELEMETRY-ONLY: ADR #52 heartbeats and the ADR #61
sidecar report THAT a leg is alive (counters, state boundaries), never WHAT the
reviewer is doing — the wrapper's `stdout_reader` parses every stream-json assistant
event and discards all content after counting
(`hetero_doc_review.py:660-676`); the same-family leg was backgrounded by driver
improvisation (no doc sanctions it — ADR #62 is scoped to the different-family leg;
the narration blueprints explicitly left same-family dispatch unchanged), hiding the
natively-streaming subagent activity. (b) `runs/LATEST` is a process-global slot
serving a session-scoped need: every `run-start` re-points it
(`csr_progress.py:207`), so concurrent sessions steal it (last-run-start-wins, never
flips back) and a human watching `--watch` silently switches runs mid-stream. User
requirements: observe csr execution in the main session like a subagent's execution;
the periodic refresh must hand out an execution-output watch command; "which run is
mine" must have a deterministic answer that needs no coordination protocol.

ADR #62 reconciliation (load-bearing for UC-1): #62's principle — report status
AUTOMATICALLY, zero-interaction — is unchanged and governs BOTH legs. #62's
mechanical argument (a synchronous call makes intra-leg narration impossible) was
derived from the SUBPROCESS shape and remains precisely correct for the
different-family wrapper, whose protocol #69 leaves untouched. A foreground subagent
is a different harness primitive: its activity streams into the conversation as
first-class content while it runs, satisfying the principle by a richer mechanism
than orchestrator-authored poll narration. #62's rejected-(d) (harness-level
streaming display of tool output — a CC feature request) is NOT contradicted: the
subagent stream is an existing harness primitive, not a feature request.

## Job To Be Done

- JTBD-1: When a csr run is executing, the user watching the orchestrating session
  wants to see WHAT the reviewers are actually doing (execution process, not just
  liveness counters), so they can trust, debug, or interrupt the run — without
  opening a second terminal, without asking the session anything, and without
  waiting for the leg to finish.
- JTBD-2: When several Claude Code sessions run csr concurrently on one repo, the
  user wants a deterministic answer to "which progress stream is MY run's" —
  obtained from their own session's conversation, not from a shared filesystem
  slot another session can silently re-point.

## Desired Outcome Metrics

- DOM-1: During EVERY leg, execution content is visible in the orchestrating
  conversation — live for same-family (foreground subagent stream), within one
  narration cadence (~2 min) for different-family.
- DOM-2: Every streamed different-family leg produces a non-empty
  `round<k>-<provider>.stream.jsonl` in its run dir; zero `*.stream.jsonl` false
  promises under `--no-stream` / `--dry-run` / missing `--progress-file`.
- DOM-3: Zero contract drift — check 9's four asserted literals survive the
  step-2 rewrite; single-run `status` output stays byte-identical
  (regression-diffed); `tele` counter values unchanged.
- DOM-4: Concurrent-session pointer ambiguity resolves WITHOUT any coordination
  protocol: the session states its own run-dir in-conversation; the all-runs
  view renders every active run with its artifact name.

## Core Use Cases

- UC-1: The user watching the orchestrating session sees the SAME-FAMILY leg's
  execution live as a subagent stream (foreground spawn; its own activity is the
  in-leg report), with zero setup.
- UC-2: The DIFFERENT-FAMILY leg's execution is observable as a tailable distilled
  log (assistant text + tool_use per block), and the leg's first narration hands
  the human the watch command — the zero-interaction channel advertises the
  interactive one.
- UC-3: "Which run is mine" resolves deterministically: the orchestrating session
  states its own `<run-dir>` path in-conversation at Frame and in the first
  narration; an all-runs view renders every active run; `runs/LATEST` is demoted to
  the single-active-run convenience and post-hoc archaeology.
- UC-4: Every existing contract is preserved: wrapper stdout stays the single
  result JSON; telemetry counters exact; heartbeats unchanged; EVENT_REGISTRY
  unchanged; `_run_streamed` signature + divergence contract table byte-true.

## Acceptance Criteria (BDD)

- AC-1: Given SKILL.md's step-2 protocol, When a csr run executes the same-family
  leg, Then `solidforge:doc-reviewer` is spawned FOREGROUND (explicitly NOT
  `run_in_background` — its streamed activity IS the in-leg report; no polling, no
  sidecar narration during this leg, ADR #69), with the `same-family-spawn` /
  `same-family-complete` appends unchanged; the sidecar section's leg-generic poll
  clause is narrowed to the different-family leg (during a foreground same-family
  leg the orchestrator's turn is blocked — the contract moves, not just narrows).
  — seam: SKILL.md step-2 same-family bullet + sidecar prose;
  `csr_progress_gates.py` check 9 — post-batch assertion set pinned (canonical,
  referenced verbatim by AC-3 and P6): the four existing literals
  (`run_in_background` / `wrapper.stderr` / `csr_progress.py status` /
  `runs/LATEST`) PLUS `stream.jsonl` and `ADR #69` in the step-2
  different-family bullet, PLUS `## 62.` AND `## 69.` in the workspace ADR log
  (the `## 62.` assertion STAYS — the ADR log is append-only, both hold), PLUS
  same-family assertions: the same-family bullet contains the literal
  `FOREGROUND` and does NOT contain `run_in_background`, and the sidecar
  section's poll clause names `different-family leg`
- AC-2: Given a streamed different-family leg launched with `--progress-file`, When
  stream-json assistant events arrive, Then each `message.content` block appends
  ONE distilled JSONL line to `<run-dir>/round<k>-<provider>.stream.jsonl` — text
  block → `{"kind":"text","text":...}` capped at 2000 chars; tool_use block →
  `{"kind":"tool","tool":<name>,"input_head":...}` capped at 300 chars — preceded
  by one spawn-start line carrying a bool `schema` field
  (`"--json-schema" in argv`, which self-identifies the structured-output retry);
  `stream_event` partials, `tool_result`/user/system events, and the result event
  are skipped; the path is a module-global `_STREAM_LOG_PATH` set in main()'s
  per-provider loop (NOT a `_run_streamed` kwarg or `guards` key — the divergence
  preserved-signature table stays byte-true). — seam:
  `csr_progress_gates.py` check 11 `stream-log-distillation` (new)
- AC-3: Given the FIRST narration of each different-family leg, Then it prints the
  session's OWN `<run-dir>` (one line: the run-dir path + `tail -f
  <run-dir>/progress.jsonl` + `tail -f <run-dir>/round<k>-*.stream.jsonl` for the
  execution stream); `csr_progress.py status workspace/cross-source-review/runs/LATEST
  --watch 5` is retained as the single-active-run one-liner; the all-runs view is
  `csr_progress.py status workspace/cross-source-review/runs/ --watch 5` (ADR #69);
  the four narration-contract literals (`run_in_background`, `wrapper.stderr`,
  `csr_progress.py status`, `runs/LATEST`) remain present in the step-2
  different-family bullet. — seam: `csr_progress_gates.py` check 9, extended per
  AC-1's canonical pinned assertion set (this seam recap is a POINTER, not a
  second enumeration)
- AC-4: Given a runs directory containing several run dirs, When
  `csr_progress.py status <runs-dir>` runs (also under `--watch`), Then it renders
  one labeled block per ACTIVE run (active = no `run-end` event in its
  progress.jsonl; blocks newest-first by mtime; label carries the dir name and
  last-event age — the operator's staleness signal, deliberately NO mtime
  threshold per workspace rule 4), collapses ended runs to one count line,
  EXCLUDES symlinked entries (`runs/LATEST` must not double-render the pointed-at
  run), and on zero active runs renders "no active runs" + the most-recent run's
  full block; `status <single-run-dir>` output stays byte-identical to the
  progress.jsonl-path form — the byte-identity oracle is a LITERAL frozen golden
  captured from the pre-change renderer BEFORE the renderer edit lands (never
  regenerated post-change; a post-change regeneration would compare the code to
  itself). The dispatch rule is pinned: a directory that
  contains its own `progress.jsonl` renders SINGLE-RUN (byte-identical to the
  file form, `--watch` included); any other directory is treated as a runs dir
  and scanned for `*/progress.jsonl` (symlinked entries excluded); a directory
  with neither its own `progress.jsonl` nor any `*/progress.jsonl` keeps today's
  `no file at <path>` message. Dispatch RESOLVES symlinks (isdir-follows-symlink
  semantics — `status runs/LATEST` keeps rendering the pointed-at run
  single-run, preserving AC-3's retained one-liner; the symlink exclusion lives
  ONLY in the runs-dir scan, never at dispatch). — seam:
  `csr_progress_gates.py` check 12 `multi-run-render` (new; its dispatch-edge
  fixture includes a symlinked single-run case)
- AC-5: Given `--no-stream`, `--dry-run`, or a missing `--progress-file`, Then NO
  `*.stream.jsonl` file is created anywhere (no false promise of an execution log
  that will never be written). — seam: `csr_progress_gates.py` check 5
  `wrapper-flag-surface` (extended)
- AC-6: Given the batch lands, Then ADR #69 is recorded in the workspace ADR log
  (`skills/parallel-development/references/design-decisions.md`, next free number);
  a dated divergence entry documents the csr-only stream-log extension
  (csr-first-not-ported + pd-port-candidacy, mirroring the ADR #61 entry's shape);
  `references/install.md`, `README.md`, `USER_GUIDE.md` reflect the new
  observability surface (facade docs, advisory severity per workspace rule 5);
  the stale next-free-ADR pointer at `docs/web-claim-verifier-proposal.md:49`
  ("#67") is corrected to "#70" AFTER ADR #69 lands. — seam: check 8
  `enumeration-sync` + manual doc-audit (advisory — semantic judgment, never a
  Blocker)

## Non-Functional Requirements

- NFR-1: `_run_streamed(argv, timeout_s, max_stream_bytes, provider)` signature and
  the divergence-log preserved-signature contract stay byte-true; the stream-log
  path travels as module-global `_STREAM_LOG_PATH` + `_STREAM_LOG_WARNED`
  (the `_PROGRESS_PATH` module-global is the ADR #61 rejected-(d) precedent).
- NFR-2: The `stdout_reader` hook is inert while `_STREAM_LOG_PATH is None` and
  NEVER mutates `tele` counters — `hetero_doc_guards.py:164-179` calls
  `_run_streamed` directly and asserts exact counter values.
- NFR-3: Every stream-log write is best-effort (ADR #61 doctrine): OSError → warn
  once on stderr, never raise, never kill the review.
- NFR-4: No new EVENT_REGISTRY event types; no new `^- \`backticked-lowercase\``
  bullets in the SKILL.md Run-progress sidecar section (csr_progress_gates check 1
  vocabulary sync blocks drift in either direction).
- NFR-5: Edit-safety against live runs: before the wrapper edit pass, verify no
  csr run is mid-flight (progress.jsonl tails / recent heartbeats); wrapper edits
  land as ONE continuous pass — never interleaved with an in-flight hetero leg
  (the import-time SyntaxError kill edge of ASSUME-1); all edits are
  inert-while-None by construction; ruff green
  (`skills/cross-source-review/ruff.toml`: E501 off, F on).
- NFR-6: No commit (workspace rule 9 — commit only when asked).

## Scope Boundary

- IN: `skills/cross-source-review/` — `infra/scripts/hetero_doc_review.py`
  (globals + `_stream_log_append` + `_run_streamed` hook + main() global set),
  `infra/scripts/csr_progress.py` (multi-run render + dispatch), `SKILL.md`
  (step-1/step-2 bullets + sidecar prose), `infra/test/csr_progress_gates.py`
  (checks 5/9 extended, 11/12 new, docstrings),
  `infra/scripts/hetero_doc_review.divergence.md` (new dated entry),
  `references/install.md`, root `README.md`, `USER_GUIDE.md`,
  `docs/web-claim-verifier-proposal.md` (stale pointer one-liner).
- IN: `skills/parallel-development/references/design-decisions.md` — ADR #69
  append ONLY (the workspace-canonical ADR log; append-only, no rewrites).
- OUT: everything else — see the exclusions section below.

## Constraints & Assumptions

- ASSUME-1: NO csr run is live while this batch lands (the 20260915-150240 run
  that motivated it converged 2026-09-15T23:20:42 after 13 rounds). The
  wrapper-process load model still governs: on-disk edits affect only the NEXT
  hetero-leg invocation. Before the wrapper edit pass, RE-VERIFY no csr run is
  mid-flight (progress.jsonl tails / recent heartbeats) — if one is, apply the
  NFR-5 discipline against it. The no-kill guarantee is scoped to SEMANTIC
  intermediates (helper present while `_STREAM_LOG_PATH` is still None →
  "no stream log"); the residual kill edge is import-time — a hetero-leg
  invocation starting against a mid-edit partial file dies with SyntaxError
  before `main()` — excluded only by the one-continuous-pass edit discipline,
  not by code.
- ASSUME-2: The harness streams a FOREGROUND subagent's activity into the
  orchestrating conversation (an existing primitive; where a harness lacks it,
  the same-family leg degrades to completion-time reporting — coverage note,
  not a contract change).
- ASSUME-3: `--output-format stream-json` assistant-event shape (message.content
  blocks: text / tool_use) is stable; the hook defends with isinstance checks
  and skips unknown block shapes rather than failing.
- ASSUME-4: One wrapper invocation per hetero leg per provider (sequential
  provider loop; structured-output retry re-spawns within the same invocation —
  same-file appends stay ts-ordered and self-identify via the `schema` flag).
- The CONSTRAINT set is the NFR section below (NFR-1..6) — not restated here.

## Decisions

- D1: Same-family leg spawns FOREGROUND. The subagent's own streamed activity is
  the in-leg report (UC-1); no polling during this leg. ADR #62 reconciliation
  as stated in the Origin section — principle unchanged, mechanism per
  substrate.
- D2: The hetero execution stream log is a DISTILLED per-assistant-block JSONL
  via module-global `_STREAM_LOG_PATH` — not a raw-stream dump, not a kwarg
  (signature + divergence table stay byte-true).
- D3: Pointer re-scoping — the session's own conversation is the session-scoped
  pointer channel (Frame statement + first narration); `csr_progress.py status
  <runs-dir>/` renders all runs; `runs/LATEST` keeps last-run-start-wins
  semantics, demoted to single-active-run convenience and post-hoc archaeology.
- D4: No new EVENT_REGISTRY event types and no new sidecar-section vocabulary
  bullets — the stream log is a FILE artifact, not a progress event (check 1
  vocabulary sync stays byte-true).
- D5: Activity classification is "no `run-end` event" ONLY — no mtime-staleness
  heuristic (rule 4); the last-event age line is the operator's staleness
  signal.

## Scope (explicit exclusions)

- No harness-level changes (CC display behavior — feature requests out of scope;
  ADR #62 rejected-(d) stands).
- No raw-stream persistence (byte-duplicates the `max_stream_bytes`-capped stdout;
  distillation IS the point).
- No polite-steal, no steal-warning text, no `LATEST-<slug>` per-run pointers
  (rejected — see ADR #69; the session's own conversation is the session-scoped
  channel).
- No mtime-staleness classification of "active" (heuristic threshold, rule 4;
  last-event age already renders).
- No port of the csr sidecar/stream-log to parallel-development (csr-only surface;
  pd-port candidacy recorded in the divergence entry for Phase B).
- Frozen history NOT rewritten: ADR #61/#62 bodies, csr-run-progress-v1/v2 and
  csr-narration-v1/v2 blueprints stay as-is — ADR #69 supersedes.

## Acceptance-Criteria -> Test Mapping

Declared at RED (ADR #58 carve-out). Collector = the gate script
(`csr_progress_gates.py`); names are check labels.

- AC-1 -> narration-contract
- AC-3 -> narration-contract
- AC-2 -> stream-log-distillation
- AC-4 -> multi-run-render
- AC-5 -> wrapper-flag-surface
- AC-6 -> enumeration-sync (pre-existing enumerations only) + check 9 canonical
  set (the ADR-log clause) + manual doc-audit (advisory — the divergence entry,
  facade docs, and #70 pointer fix are NOT deterministically asserted)
- AC-2 -> stream-render
