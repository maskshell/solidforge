---
queue_version: v1
frozen_at: 2026-08-09
plan_ref: docs/psv-gate-mode-iteration-plan.md
authority_chain:
  - docs/psv-gate-mode-proposal.md
  - skills/primary-source-verification/SKILL.md
  - skills/primary-source-verification/docs/proposal.md
  - skills/primary-source-verification/docs/design-decisions.md
status: frozen
---

# Plan Queue — iteration-plan

FROZEN plan interpretation emitted by blueprint-crafting `freeze`. Read-only for the executor; revise only via the Revision Channel (`status` -> `revising` -> edit + queue_version bump -> `status: frozen`). See parallel-development `references/plan-driven-mode.md`.

## Summary (checkpoint view)

7 item(s). DoD source: docs/psv-gate-mode-proposal.md.

## Items

```json
[
  {
    "item_id": "E1",
    "seq": 1,
    "depends_on": [],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E1",
    "title": "CLAUDE.md rule 13 insertion-point wording",
    "scope": "lines 112+122: psv additive; gate-first when rule-13 conditions hold; authoritative full-M after csr",
    "source_location": "psv-gate-mode-proposal.md §Enumerations",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E2",
    "seq": 2,
    "depends_on": [],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E2",
    "title": "USER_GUIDE.md Two-axis + diagram",
    "scope": "lines 24, 27-31, 33, 47, 49, 54 — gate mode named",
    "source_location": "psv-gate-mode-proposal.md §Enumerations",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E3",
    "seq": 3,
    "depends_on": [],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E3",
    "title": "psv SKILL.md gate-mode note",
    "scope": "description + line 73: subset gate, batch GO/NO-GO, gate record non-authoritative, bounded re-gate",
    "source_location": "psv-gate-mode-proposal.md §Enumerations",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E4",
    "seq": 4,
    "depends_on": [],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E4",
    "title": "csr SKILL.md psv-positioning note",
    "scope": "coordination section: ADD gate-mode note (no psv text exists there today)",
    "source_location": "psv-gate-mode-proposal.md §Enumerations",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E5",
    "seq": 5,
    "depends_on": [],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E5",
    "title": "psv proposal.md Q5 amendment",
    "scope": "'after or beside csr' → 'and before csr as the gate when rule-13 conditions hold'",
    "source_location": "psv-gate-mode-proposal.md §Enumerations (N09)",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E6",
    "seq": 6,
    "depends_on": [
      "E3"
    ],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E6",
    "title": "psv design-decisions.md ADR entry",
    "scope": "gate-mode decisions ADR (GO contract, gate-M=0, batch threshold, bounded re-gate); ADR #1/#3/#5 untouched",
    "source_location": "psv-gate-mode-proposal.md §Enumerations (N09)",
    "parallel_group": "wave2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E7",
    "seq": 7,
    "depends_on": [
      "E1",
      "E2",
      "E3",
      "E4",
      "E5",
      "E6"
    ],
    "dod_ref": "psv-gate-mode-iteration-plan.md §DoD/E7",
    "title": "doc-audit sweep (rule 5)",
    "scope": "grep every pipeline-order statement; zero stale; proposal enumeration list maps 1:1",
    "source_location": "psv-gate-mode-proposal.md §Enumerations + rule 5",
    "parallel_group": "wave3",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  }
]
```
