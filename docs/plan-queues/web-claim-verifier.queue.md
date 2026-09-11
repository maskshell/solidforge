---
queue_version: v1
frozen_at: 2026-09-11
plan_ref: docs/web-claim-verifier-proposal.md
authority_chain:
  - docs/web-claim-verifier-proposal.md (csr cap-hit at the human-decreed ceiling of 17; core claims coverage-verified; record docs/web-claim-verifier-proposal.csr-record.json)
  - agents/claim-verifier.agent.md (the exemplar)
status: frozen
---

# Plan Queue — web-claim-verifier agent

FROZEN plan interpretation. Read-only for the Coder; revise only via the Revision Channel.

## Summary (checkpoint view)

3 items at the plan's native grain: T1 authors the agent (§4 bullet-by-bullet), T2a wires csr's
reconcile spawn condition, T2b does the five enumerations. T3 (ADR + gates) rides with T2b's
completion. DoD source: §6 acceptance. Execution shape (per the node-bin precedent): inline +
manual commit.

## Items

```json
[
  {
    "seq": 0,
    "item_id": "T1",
    "title": "author agents/web-claim-verifier.agent.md",
    "scope": "per §4 BULLET BY BULLET: frontmatter (name: web-claim-verifier; tools WebSearch/WebFetch/Read/Grep/Glob; disallowedTools Edit/Write/NotebookEdit); mode selection; claim-mode output (claim_id, verdict labels, finding sub-object iff != verified, note REQUIRED-for-verified); question-mode output (findings[] with grounding + confidence + partial_reason); the two-rule oracle discipline (exemplar quotes verbatim); source_tier enum + boundary + preprint mapping; volatile gate; bounded search; boundaries",
    "source_location": "proposal §4 + §6-T1",
    "depends_on": [],
    "dod_ref": "proposal §6 acceptance (bullet-by-bullet review of the .agent.md)",
    "parallel_group": "wave-1"
  },
  {
    "seq": 1,
    "item_id": "T2a",
    "title": "csr SKILL.md reconcile spawn integration",
    "scope": "EXTEND both reconcile moments (SKILL.md:47/:49): the fetchable-claim trigger (EVIDENCE or rejected-rationale cites an identifiable source), per-round cap (≤2 per reconcile moment, highest-severity first, un-spawned → coverage notes), the spawn prompt template (claim text + defect_id + URL/named-source), evidence-drop into <run-dir>/evidence/, escalated-no-fetch",
    "source_location": "proposal §5 csr bullet + §6-T2a",
    "depends_on": ["T1"],
    "dod_ref": "proposal §6 acceptance + csr's own self-gates",
    "parallel_group": "wave-2"
  },
  {
    "seq": 2,
    "item_id": "T2b",
    "title": "enumerations + ADR + gates",
    "scope": "plugin.json '22 cascaded subagents' -> 23; EXPECTED_AGENTS 17 -> 23 (five pre-existing + web-claim-verifier + the two '17 plugin-bundled' prose sites); psv SKILL.md building-block mention; .graphiti.json two-axis fix ('their 13' -> 'the plugin's 23 cascaded subagents (plugin-scoped as solidforge:<name>)'); ADR #67 in pd's design-decisions.md; gates: pd rule-1 battery + csr self-gates + psv self-gates",
    "source_location": "proposal §5 (all non-csr bullets) + §6-T2b/T3",
    "depends_on": ["T1"],
    "dod_ref": "proposal §6 acceptance (all three skills' self-gates green)",
    "parallel_group": "wave-2"
  }
]
```
