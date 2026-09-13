---
queue_version: v1
frozen_at: 2026-09-13
plan_ref: docs/prompt-content-spec.md
authority_chain:
  - docs/prompt-content-spec.md
  - CLAUDE.md
  - ~/.claude/CLAUDE.md
  - skills/parallel-development/references/design-decisions.md
status: frozen
---

# Plan Queue — product-spec

FROZEN plan interpretation emitted by blueprint-crafting `freeze`. Read-only for the executor; revise only via the Revision Channel (`status` -> `revising` -> edit + queue_version bump -> `status: frozen`). See parallel-development `references/plan-driven-mode.md`.

## Summary (checkpoint view)

9 item(s). DoD source: docs/prompt-content-spec.md.

## Items

```json
[
  {
    "item_id": "PCS-1",
    "seq": 1,
    "depends_on": [],
    "dod_ref": "docs/prompt-content-spec.md §3 Scope Boundary + §4 Consumer Sub-Typing",
    "title": "Tier boundary + consumer sub-typing + dispatch modes",
    "scope": "Define tier-1 in-scope artifact set (incl. commands/*.md), exclude tiers 2/3, split tier-1 into three consumer kinds, and classify agent dispatch modes (mapping 11 / workflow 7 / dual 1 / platform-flow 4)",
    "source_location": "docs/prompt-content-spec.md §3–§4",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-2",
    "seq": 2,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L1 Parse-Reliability Layer",
    "title": "L1 parse-reliability principles",
    "scope": "Restate rule-10 parse principles as MUST/SHOULD for all tier-1 artifacts including assembled prompts",
    "source_location": "docs/prompt-content-spec.md §5 L1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-3",
    "seq": 3,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L2 Routing-Surface Layer",
    "title": "L2 routing-surface contract",
    "scope": "Three-part description contract (trigger / NOT-for + route-to / produces) for description-routed skills and agents",
    "source_location": "docs/prompt-content-spec.md §5 L2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-4",
    "seq": 4,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L3 Behavioral-Contract Layer",
    "title": "L3 canonical behavioral clause set",
    "scope": "Five canonical clauses (oracle / negative-scope / schema-only-no-edit / no-stake / honest-disclosure) with grandfathering",
    "source_location": "docs/prompt-content-spec.md §5 L3",
    "open_decisions": [
      {
        "id": "ODP-3",
        "kind": "deferred",
        "resolution": "Unification lands incrementally per D4 touch-trigger; a dedicated sweep over the corrected inventory (7 strict carriers + 2 variant carriers + code-reviewer's zero-clause gap, snapshot spec §6) is a separate work item with its own convergence run"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-5",
    "seq": 5,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L4 Enforcement-Division Layer",
    "title": "L4 enforcement-division principle",
    "scope": "No prose re-statement of deterministically-gated constraints; declare enforcement locus instead",
    "source_location": "docs/prompt-content-spec.md §5 L4",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-6",
    "seq": 6,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L5 Placement Layer",
    "title": "L5 placement/loading-chain inheritance",
    "scope": "Restate rule-8 decision-point reachability; inherit deterministic disconnect_check enforcement",
    "source_location": "docs/prompt-content-spec.md §5 L5",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-7",
    "seq": 7,
    "depends_on": [
      "PCS-1"
    ],
    "dod_ref": "docs/prompt-content-spec.md §5 L6 Assembly-Discipline Layer",
    "title": "L6 assembly-discipline rules",
    "scope": "Deterministic assembly, assert-or-coverage-note, minimal state lines, quote delimiting, different-family-by-default, bounds stay in harness",
    "source_location": "docs/prompt-content-spec.md §5 L6",
    "open_decisions": [
      {
        "id": "ODP-2",
        "kind": "deferred",
        "resolution": "Candidate future gate (assert-on-prompt-text or coverage-note grep) recorded; blocked on ODP-1 sequencing and a wrapper change touching assembly"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-8",
    "seq": 8,
    "depends_on": [
      "PCS-2",
      "PCS-3",
      "PCS-4",
      "PCS-5",
      "PCS-6",
      "PCS-7"
    ],
    "dod_ref": "docs/prompt-content-spec.md §6 Codification-Status Audit",
    "title": "Codification-status audit baseline",
    "scope": "Per-layer carrier/status/enforcement table with grep-verified evidence and the generational agent-split finding",
    "source_location": "docs/prompt-content-spec.md §6",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "PCS-9",
    "seq": 9,
    "depends_on": [
      "PCS-8"
    ],
    "dod_ref": "docs/prompt-content-spec.md §7 Decisions + §8 Acceptance Criteria",
    "title": "Decisions D1–D6 + AC set with declared enforcement loci",
    "scope": "Six decisions with rationale/rejections; seven ACs each declaring deterministic/advisory/human enforcement",
    "source_location": "docs/prompt-content-spec.md §7–§8",
    "open_decisions": [
      {
        "id": "ODP-1",
        "kind": "deferred",
        "resolution": "D5 promotion of L4+L6 to CLAUDE.md rules deferred until >=1 completed dogfood cycle against this spec; this spec is the carrier meanwhile"
      }
    ],
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  }
]
```
