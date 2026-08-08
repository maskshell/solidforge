---
queue_version: v1
frozen_at: 2026-08-08
plan_ref: docs/record-auditability-fix-plan.md
authority_chain:
  - docs/record-auditability-fix-plan.md
  - skills/cross-source-review/SKILL.md
  - skills/primary-source-verification/SKILL.md
status: frozen
---

# Plan Queue — iteration-plan

FROZEN plan interpretation emitted by blueprint-crafting `freeze`. Read-only for the executor; revise only via the Revision Channel (`status` -> `revising` -> edit + queue_version bump -> `status: frozen`). See parallel-development `references/plan-driven-mode.md`.

## Summary (checkpoint view)

10 item(s). DoD source: docs/record-auditability-fix-plan.md.

## Items

```json
[
  {
    "item_id": "A1",
    "seq": 1,
    "depends_on": [],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / A1",
    "title": "csr record schema: round gains required findings + dispositions",
    "scope": "convergence-record.schema.json round $defs gains required findings (doc-findings shape) + required dispositions (defect_id/action fixed|rejected|escalated/note)",
    "source_location": "record-auditability-fix-plan.md fix A",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "A2",
    "seq": 2,
    "depends_on": [
      "A1"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / A2",
    "title": "converge.py pass-through: findings + dispositions into the record",
    "scope": "converge.py emits per-round findings + dispositions from run.json; run.json input shape gains required per-round dispositions array; jsonschema validation covers both",
    "source_location": "record-auditability-fix-plan.md fix A landing",
    "parallel_group": "wave2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "A3",
    "seq": 3,
    "depends_on": [
      "A1"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / A3",
    "title": "csr SKILL.md step-2 + step-4 wording",
    "scope": "step 2: record accept/reject/escalate + rationale per defect_id at reconcile time (escalate target = human, stated explicitly); step 4: per-round findings + dispositions replaces findings trend",
    "source_location": "record-auditability-fix-plan.md fix A landing",
    "parallel_group": "wave2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "A4",
    "seq": 4,
    "depends_on": [
      "A1",
      "A2"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / A4",
    "title": "csr test fixtures: embedded findings + dispositions",
    "scope": "convergence_policy_check.py + findings_shape_check.py fixtures include records with findings + dispositions; round-trip asserts record-with-findings validates",
    "source_location": "record-auditability-fix-plan.md fix A landing",
    "parallel_group": "wave3",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "A5",
    "seq": 5,
    "depends_on": [
      "A1",
      "A2",
      "A3"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / A5",
    "title": "csr ADR log + doc-audit",
    "scope": "create skills/cross-source-review/docs/design-decisions.md (sibling convention) with the 3 pre-ADRs + escalate-target note; doc-audit grep for stale round-shape enumerations",
    "source_location": "record-auditability-fix-plan.md pre-ADR section + rule 5",
    "parallel_group": "wave4",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "B1",
    "seq": 6,
    "depends_on": [],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / B1",
    "title": "psv SKILL.md: packet persistence + extractor guidance",
    "scope": "step 4: per-claim doc-findings packet persisted as a file beside the coverage-record; extractor guidance: prefer durable in-repo sources; volatile sources flagged",
    "source_location": "record-auditability-fix-plan.md fix B",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "B2",
    "seq": 7,
    "depends_on": [],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / B2",
    "title": "psv coverage-record schema: volatile-authority registry",
    "scope": "coverage-record.schema.json gains volatile-authority registry (claim_ref -> volatile source; covers verified claims too); coverage_policy_check.py validates",
    "source_location": "record-auditability-fix-plan.md fix B",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "B3",
    "seq": 8,
    "depends_on": [
      "B1",
      "B2"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / B3",
    "title": "psv test fixtures: packet + registry",
    "scope": "psv test fixtures include a packet-with-registry record; coverage_policy_check + fetched_quote_gate stay green",
    "source_location": "record-auditability-fix-plan.md fix B landing",
    "parallel_group": "wave2",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "C1",
    "seq": 9,
    "depends_on": [],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / C1",
    "title": "jsonschema into dev deps",
    "scope": "pyproject.toml [project.optional-dependencies] dev + [dependency-groups] dev gain jsonschema; uv sync succeeds; converge.py under repo venv validates without SKIP note",
    "source_location": "record-auditability-fix-plan.md fix C",
    "parallel_group": "wave1",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  },
  {
    "item_id": "E1",
    "seq": 10,
    "depends_on": [
      "A1",
      "A2",
      "A3",
      "A4",
      "A5",
      "B1",
      "B2",
      "B3",
      "C1"
    ],
    "dod_ref": "record-auditability-iteration-plan.md §Per-iteration DoD / E1",
    "title": "full self-gate sweep",
    "scope": "csr + psv full test suites green under repo venv; no SKIP note; the audit's two record-layer defects demonstrably closed",
    "source_location": "record-auditability-fix-plan.md fix E + workspace rule 1",
    "parallel_group": "wave5",
    "blueprint_subset": [],
    "producer": "blueprint-crafting",
    "plan_model_version": "v1"
  }
]
```
