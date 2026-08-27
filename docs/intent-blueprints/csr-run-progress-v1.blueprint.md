---
blueprint_version: v1
frozen_at: 2026-08-27
task: csr-run-progress-observability
status: frozen
---

# Intent Blueprint — csr run-progress observability (sidecar + renderer)

Origin: user-approved design (2026-08-27 session, 方案1+方案2). Problem: a csr run
(same-family + different-family multi-round review) is externally opaque — the ADR #52
heartbeat goes to the wrapper subprocess's stderr, captured inside the invoking
session's pending tool call; nothing refreshes for an outside observer until the run
ends. Scope: extend the ADR #52 liveness contract from the wrapper layer to the whole
run via an append-only per-run progress sidecar + a read-only status renderer.

## Core Use Cases

- UC-1: An external observer (human at another terminal, or another session) can watch
  a csr run live — every orchestrator state boundary (round start/leg/reconcile/round
  end/terminal) and every wrapper heartbeat lands as one JSONL line at a well-known
  per-run path.
- UC-2: The observer can render one-screen state (round k of cap, current phase + age,
  per-leg counts, reconcile totals, terminal state) from that file without reading raw
  JSONL.
- UC-3: Observability is strictly additive — progress-write failure NEVER kills or
  blocks a review; the wrapper's result contract (stdout single JSON, exit codes) is
  unchanged.
- UC-4: The event vocabulary is single-sourced (registry in code ↔ SKILL.md
  enumeration ↔ supporting-doc mentions) and gate-checked, so drift is a Blocker.

## Acceptance Criteria

- AC-1: Given a run dir, When the orchestrator appends each registry event via
  `csr_progress.py append --file <progress.jsonl> --type <t> [--field k=v ...]`, Then
  every event lands as exactly one JSONL line carrying `ts` + `type` + coerced fields
  (int/float/bool/str), and invalid usage — unknown type, missing required field,
  unknown field — exits non-zero (loud, rule 3). — seam: `csr_progress.py append` CLI
  (catches shape/typo drift at the write boundary; misses nothing downstream — status
  tolerates whatever is already on disk)
- AC-2: Given any progress.jsonl — including one with a torn/partial last line (the
  concurrent `tail -f` reality) and unknown event types — When `csr_progress.py status`
  runs, Then it renders run header (artifact/tier/cap), round k of cap, current phase +
  last-event age, same-family + hetero leg counts, reconcile totals, terminal state
  (RUNNING / CONVERGED / ADVERSARIAL-STALEMATE / CAP-HIT / ABORTED), and an unparsed
  count, without crashing. — seam: `csr_progress.py status` CLI (catches render
  robustness; misses semantic correctness of derived counts — outer-ring)
- AC-3: Given `hetero_doc_review.py --progress-file <path>`, When the wrapper runs
  (offline `--dry-run`, or a streamed child), Then it appends `hetero-leg-start` /
  `hetero-heartbeat` (stream mode) / `hetero-leg-end` lines to that path in addition to
  the stderr heartbeat, AND stdout stays the single result JSON with unchanged exit
  codes, AND an unwritable progress path degrades to a one-line stderr warning without
  raising. — seam: `hetero_doc_review.py --progress-file` CLI + the progress file
  (catches the wrapper half of UC-1/UC-3; the orchestrator half is SKILL.md contract +
  AC-4 sync)
- AC-4: Given the shipped state, When `csr_progress_gates.py` runs, Then the registry
  keys equal the SKILL.md event-vocabulary bullets exactly (both directions), the
  wrapper divergence is recorded in `hetero_doc_review.divergence.md`, and
  `disconnect_check.py` REQUIRED_FILES + SKILL.md/install.md self-check lists include
  the two new files — any drift is a Blocker. — seam: `csr_progress_gates.py` gate
  (catches enumeration drift; misses prose quality — doc-audit advisory, rule 5)

## Non-Functional Requirements

- NFR-1: stdlib-only, self-contained scripts (rule 7 — no shared-lib import between
  csr_progress.py and the wrapper; each duplicates its tiny append helper).
- NFR-2: ruff clean under the per-skill config (E4/E7/E9/F) and `ruff format --check`
  at line length 88 (per-skill format standard).
- NFR-3: progress appends are O(line) with flush; status is a single streaming pass
  (a multi-hour run's heartbeat log stays cheap to render).
- NFR-4: failure isolation — every progress-write path is best-effort (OSError
  caught); a progress failure never alters the wrapper's verdict/exit path.

## Scope (explicit exclusions)

- pd's `hetero_review.py` is NOT touched (csr files_touched boundary); the divergence
  is logged as a csr-first candidate port (Phase-B evidence).
- No changes to `converge.py`, schemas, or the convergence-record format (the sidecar
  is operational telemetry, not a record artifact).
- No daemon/socket/file-watch service — a plain file + `tail -f` / `status --watch`.
- run-id naming is an orchestrator convention documented in SKILL.md
  (`workspace/cross-source-review/runs/<stamp>-<slug>/progress.jsonl`, gitignored per
  workspace rule 11), not enforced by code.

## Acceptance-Criteria -> Test Mapping

Declared at RED (ADR #58 carve-out). The collector here is the gate script itself
(standalone self-gates, rule 7 — no pytest collector in csr infra); names are
`csr_progress_gates.py` check labels.

- AC-1 -> append-valid
- AC-1 -> append-invalid
- AC-2 -> status-render
- AC-3 -> wrapper-flag-surface
- AC-3 -> wrapper-heartbeat-tee
- AC-3 -> wrapper-best-effort
- AC-4 -> registry-vocabulary-sync
- AC-4 -> enumeration-sync
