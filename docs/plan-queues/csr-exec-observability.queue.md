---
queue_version: v1
frozen_at: 2026-09-15
plan_ref: docs/intent-blueprints/csr-exec-observability-v1.blueprint.md
authority_chain:
  - docs/intent-blueprints/csr-exec-observability-v1.blueprint.md
status: frozen
---

# Plan Queue — product-spec

FROZEN plan interpretation emitted by blueprint-crafting `freeze`. Read-only for the executor; revise only via the Revision Channel (`status` -> `revising` -> edit + queue_version bump -> `status: frozen`). See parallel-development `references/plan-driven-mode.md`.

## Summary (checkpoint view)

8 item(s). DoD source: docs/intent-blueprints/csr-exec-observability-v1.blueprint.md.

## Items

```json
[
  {
    "item_id": "P1",
    "seq": 1,
    "depends_on": [],
    "dod_ref": "AC-2",
    "title": "Wrapper stream-log hook",
    "scope": "hetero_doc_review.py: _STREAM_LOG_PATH/_STREAM_LOG_WARNED globals, _stream_log_append helper, spawn-start marker + per-block distillation in _run_streamed.stdout_reader (inert while None, counters untouched), global set in main() per-provider loop",
    "source_location": "AC-2 + NFR-1/2/3",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P2",
    "seq": 2,
    "depends_on": [],
    "dod_ref": "AC-4",
    "title": "Multi-run status renderer",
    "scope": "PRE-STEP before any renderer edit: capture the current single-run render output as a literal frozen golden fixture (the byte-regression oracle for check 12 — never regenerated post-change). Then csr_progress.py: _collect_run_dirs (islink-excluded, mtime-desc), render_multi_status (one block per active run, ended collapsed, zero-active fallback), dispatch pinned in _resolve_status_path/cmd_status — a dir with its own progress.jsonl renders single-run byte-identical; dispatch RESOLVES symlinks (status runs/LATEST stays single-run; symlink exclusion is scan-only, never at dispatch); any other dir is a runs dir scanned for */progress.jsonl; neither -> today's no-file message",
    "source_location": "AC-4 + D5",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P3",
    "seq": 3,
    "depends_on": [
      "P1"
    ],
    "dod_ref": "AC-1",
    "title": "SKILL.md contract edits",
    "scope": "Same-family bullet -> explicit FOREGROUND spawn, with the same-family-spawn / same-family-complete append instructions preserved verbatim (AC-1 clause); different-family bullet first-narration flips to own run-dir + both tail commands and cites (ADR #69) (four check-9 literals retained); Frame states run-dir; sidecar prose leg-generic clause narrowed; no new vocabulary bullets",
    "source_location": "AC-1 + AC-3 + NFR-4",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P4",
    "seq": 4,
    "depends_on": [
      "P1"
    ],
    "dod_ref": "AC-6",
    "title": "Divergence entry",
    "scope": "hetero_doc_review.divergence.md: dated csr-only ADR #69 section (csr-first-not-ported + pd-port-candidacy), distillation contract documented, signature table untouched",
    "source_location": "AC-6 + NFR-1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P5",
    "seq": 5,
    "depends_on": [
      "P1",
      "P2",
      "P3"
    ],
    "dod_ref": "AC-6",
    "title": "ADR #69",
    "scope": "Append ## 69 to skills/parallel-development/references/design-decisions.md: Context/Decision (3 parts)/Why/Rejected (a-g)/Sibling/Tests incl. the #62 reconciliation and rejected-(d) scoping",
    "source_location": "AC-6 + Origin reconciliation paragraph",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P6",
    "seq": 6,
    "depends_on": [
      "P1",
      "P2",
      "P3",
      "P5"
    ],
    "dod_ref": "AC-2",
    "title": "Gate updates",
    "scope": "csr_progress_gates.py: check 9 assertion set pinned post-batch per AC-1's canonical set — four existing literals + stream.jsonl + ADR #69 in the different-family bullet + ## 62. AND ## 69. in the ADR log (both stay) + same-family assertions (same-family bullet contains FOREGROUND, lacks run_in_background; sidecar poll clause names different-family leg); red until P5 lands, hence depends_on P5; check 5 no-false-promise sub-assertion; new check 11 stream-log-distillation (fake stream, caps, best-effort); new check 12 multi-run-render (scan-level LATEST exclusion, symlinked single-run dispatch case, zero-active, dispatch edge, byte regression against P2's pre-captured frozen golden); docstrings ten->twelve",
    "source_location": "AC-2 + AC-4 + AC-5 + AC->Test mapping",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P7",
    "seq": 7,
    "depends_on": [
      "P2",
      "P3"
    ],
    "dod_ref": "AC-6",
    "title": "Facade docs",
    "scope": "install.md sidecar paragraph + README csr bullet + USER_GUIDE csr paragraph: cadence flip to different-family, stream-log sentence, all-runs view one-liner (advisory severity)",
    "source_location": "AC-6",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "P8",
    "seq": 8,
    "depends_on": [
      "P5"
    ],
    "dod_ref": "AC-6",
    "title": "Stale ADR pointer fix",
    "scope": "docs/web-claim-verifier-proposal.md:49 next-free-ADR pointer #67 -> #70, AFTER ADR #69 lands",
    "source_location": "AC-6",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  }
]
```
