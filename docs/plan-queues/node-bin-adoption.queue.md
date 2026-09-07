---
queue_version: v2
frozen_at: 2026-09-06
plan_ref: docs/sf-project-node-bin-adoption.md
authority_chain:
  - docs/sf-project-node-bin-adoption.md (SUBSTANTIVE-CONVERGED; csr record docs/sf-project-node-bin-adoption.csr-record.json)
  - solidforge-pi post-0.2.7 implementation (diffable source, evidence/pi-detect_toolchain.py)
status: frozen
---

# Plan Queue — SF_PROJECT_NODE_BIN adoption (pi 0.2.7 → CC)

FROZEN plan interpretation. Read-only for the Coder; revise only via the Revision Channel.
See plan-driven-mode.md.

## Summary (checkpoint view)

6 items at the plan's native T-grain. T1 is the foundation (canonical resolve_tool gains
the node opt-in branch + containment + the pi-signature `root=None` kwarg); T2 collapses
the SEVEN ad-hoc project-local resolution sites (incl. gating the npx --no-install arm)
into the canonical resolver; T3 routes arm.py tool_present through it; T4 ports the 10-check
pi test file + CC extensions; T5 documents both opt-in envs in 5 facade docs; T6 wires
$ARGUMENTS in the command + fixes the --lang go drift + extends plugin_layout. DoD source:
the plan's §5 acceptance (self-gates green + ported/extended tests green + planted-binary
probes per site). Outcome axis stays human.

## Items

```json
[
  {
    "seq": 0,
    "item_id": "T1",
    "title": "canonical resolve_tool: node branch + containment + root kwarg",
    "scope": "detect_toolchain.py resolve_tool adopts pi's signature resolve_tool(name, root=None) and the SF_PROJECT_NODE_BIN branch (realpath containment under <root>/node_modules/; PATH wins; escaping symlink refused even under opt-in); diffable against solidforge-pi post-0.2.7",
    "source_location": "sf-project-node-bin-adoption.md §5 T1 (A1)",
    "depends_on": [],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-1"
  },
  {
    "seq": 1,
    "item_id": "T2",
    "title": "collapse the seven ad-hoc sites + gate the npx arm",
    "scope": "fast_gate.py check_web (217-218) eslint; arch_contract_web.py depcruise_cmd (70-78, npx arm gated behind SF_PROJECT_NODE_BIN=1), eslint (167-171), _resolve_tsc (202-207); arch_contract_tests.py _resolve_vitest (575-587); spectral_adapter.py resolve_spectral (124-133); arch_contract_python.py private resolve_tool deleted (83-97), callers 156/192/307 import the canonical one; every site keeps its degrade path (coverage note, no silent green); spectral keeps no-npx semantics",
    "source_location": "sf-project-node-bin-adoption.md §5 T2 (A3)",
    "depends_on": ["T1"],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-2"
  },
  {
    "seq": 2,
    "item_id": "T3",
    "title": "arm.py tool_present routes through resolve_tool",
    "scope": "tool_present imports hooks/lib detect_toolchain, calls resolve_tool(name, root=project_dir); private unconditional venv scan dropped; report semantics change (opt-in-less project-local tools report absent) is intended",
    "source_location": "sf-project-node-bin-adoption.md §5 T3 (A2)",
    "depends_on": ["T1"],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-2"
  },
  {
    "seq": 3,
    "item_id": "T4",
    "title": "port detect_toolchain_test.py + CC extensions",
    "scope": "port pi's 10 checks (7 main + 3 arm_tool_present_truth); extend with CC-specific cases for the seven collapsed sites: in-tree .bin symlink resolve (containment sentinel), planted node_modules/.bin/eslint, .venv/bin/ruff, .venv/bin/lint-imports (arch_contract_python regression probe), depcruise/tsc/vitest/spectral site probes, gated npx arm probe",
    "source_location": "sf-project-node-bin-adoption.md §5 T4 (A4)",
    "depends_on": ["T1", "T2", "T3"],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-3"
  },
  {
    "seq": 4,
    "item_id": "T5",
    "title": "document both opt-in envs in facade docs",
    "scope": "README, README.zh-CN, USER_GUIDE, USER_GUIDE.zh-CN, references/install.md: SF_PROJECT_VENV_TOOLS + SF_PROJECT_NODE_BIN, PATH-wins + containment contract, report-semantics change, tsc/vitest pinned-version note. PLUS (v2, outer-ring T3 finding) the RUNTIME hint: arm.py absent_tool_hint names both opt-in envs so the post---with-tools absent state is self-explaining at the point of confusion",
    "source_location": "sf-project-node-bin-adoption.md §5 T5 (A7)",
    "depends_on": ["T1"],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-3"
  },
  {
    "seq": 5,
    "item_id": "T6",
    "title": "$ARGUMENTS wiring + --lang go drift + plugin_layout assertion",
    "scope": "commands/arm-tools.md: wire $ARGUMENTS explicitly near the top with a parse instruction; add go to both --lang enumerations (line 3 + line 20); extend infra/test/plugin_layout.py with the wiring assertion; record the 4 ADRs from §6 in design-decisions.md",
    "source_location": "sf-project-node-bin-adoption.md §5 T6 (A5+A6) + §6",
    "depends_on": [],
    "dod_ref": "sf-project-node-bin-adoption.md §5 acceptance",
    "parallel_group": "wave-3"
  }
]
```
