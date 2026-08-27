---
blueprint_version: v1
frozen_at: 2026-08-27
task: csr-in-session-narration
status: frozen
---

# Intent Blueprint — csr zero-interaction in-session status narration

Origin: user first-principles restatement (2026-08-27): when csr runs, it must report
current status to the user AUTOMATICALLY (periodic or streaming), with ZERO special
interaction — no manual status request, no manual cron, no external terminal. ADR #61
solved external observability (sidecar file); the interacting user still sees silence
during a long leg because the synchronous wrapper call blocks the orchestrating
session mid-turn, and mid-turn no text can stream.

## Core Use Cases

- UC-1: The user interacting with the orchestrating session sees live status during
  long legs WITHOUT any action on their part — reporting is a property of running
  the skill (protocol step), not external tooling they set up.
- UC-2: The result contract is preserved — stdout stays the single result JSON; the
  sidecar (ADR #61) remains the telemetry channel; no wrapper code change.
- UC-3: Bounded narration — one condensed line per ~2-minute poll (a 10-min leg
  ≈ 5 lines), never a transcript flood.

## Acceptance Criteria

- AC-1: Given SKILL.md's step-2 different-family instruction, When a csr run
  executes it, Then the wrapper is launched as a background task with stderr
  discarded (`2>/dev/null` — heartbeats already tee to the progress file), the
  orchestrator polls ~every 2 minutes rendering ONE condensed status line per poll
  from the sidecar, and on completion parses the result JSON from the task output
  file; a synchronous fallback is documented for harnesses without background
  execution. — seam: SKILL.md step-2 protocol text (the orchestrator's decision
  point; runtime behavior is the next real run's dogfood, honestly deferred)
- AC-2: Given the shipped state, When `csr_progress_gates.py` runs, Then the
  narration-contract check Blocks on any missing piece (step-2 background
  execution, stderr discard, status-render instruction, ADR #62 cross-ref in the
  workspace ADR log). — seam: `csr_progress_gates.py` check `narration-contract`
  (static presence — it cannot verify the orchestrator actually narrates; that is
  outer-ring + live-dogfood territory, stated)

## Non-Functional Requirements

- NFR-1: NO wrapper code change (hetero_doc_review.py untouched this task).
- NFR-2: stdlib/ruff/format discipline unchanged; gates stay green.
- NFR-3: narration cadence bounded (~1 line / ~2 min per running leg).

## Scope (explicit exclusions)

- No harness-level changes (CC display behavior, feature requests — out of scope).
- No change to the same-family leg dispatch (harness-native async agents already
  notify; the narration rule is written leg-generically but only the wrapper leg
  changes invocation form).
- No session-level cron/monitor tooling (rejected at first principles — violates
  zero-interaction).

## Acceptance-Criteria -> Test Mapping

Declared at RED (ADR #58 carve-out). Collector = the gate script; names are check
labels.

- AC-2 -> narration-contract
- AC-1 -> narration-contract (static half; runtime half deferred to the next real
  run — the live dogfood coverage note)
