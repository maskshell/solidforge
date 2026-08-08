# cross-source-review — Design Decisions (ADR log)

Non-obvious decisions (workspace rule 6). Context / Decision / Why / Rejected. The sibling skills keep this log at `docs/design-decisions.md` (psv, prior-art-search) or `references/design-decisions.md` (parallel-development); this file follows the psv convention.

## ADR #1 — Convergence-record embeds per-round findings + dispositions (required)

- Context: the third-party record-layer audit (fedaot-kb, 2026-08-08) found the convergence-record counts-only: round 2 carried 16 findings / 0 blockers / pass with no way to see what the 16 findings were or why they were waived. `substantive_converged` rested on the reviewer's severity classification alone.
- Decision: the record's round object carries required `findings` (the reconciled doc-findings shapes) and required `dispositions` (one per finding: `fixed` / `rejected` / `escalated`, each with the orchestrator's rationale). `converge.py` passes them through and enforces the 1:1 coverage invariant (a partial dispositions array is a contract violation — never silent).
- Why: the record must be self-contained for audit — a reader can list every finding per round, its severity, and what was done about it. The orchestrator already makes accept/reject decisions at reconcile time (SKILL.md step 2); the change records them instead of discarding them.
- Rejected: (a) separate per-round findings files — orphanable, reproduce the volatility sin under audit; (b) optional `findings`/`dispositions` for back-compat — optionality would silently re-create the counts-only hole.

## ADR #2 — Volatile authority sources: flag, not forbid

- Context: the audit also found adjudication sources that are repo-external, unversioned, and deletable (`~/.claude/projects/` memory files, `/tmp` clones): claims verified against them are not re-fetchable by a repo reader. The audit's recommendation was to forbid such sources ("psv 类管线的 authority_ref 应禁用不可重取的源").
- Decision: psv flags volatile authorities instead of forbidding them — the coverage-record carries a volatile-authority registry (claim_ref → volatile source) covering ALL claims, verified included; the extractor prefers a durable in-repo source when one exists (the doc should carry the durable citation).
- Why: project-state claims often have a volatile source as their ONLY adjudication surface; forbidding would kill their verification outright. Flagging keeps the verdict honest and the record transparent; the discipline the audit wants is enforced one level up — the DOC should carry durable citations when one exists.
- Rejected: (a) the audit's forbid-everything rule — kills verification of legitimate project-state claims; (b) silent pass with no disclosure — violates workspace rule 3.

## ADR #3 — Record schema evolution: breaking change, no migration

- Context: making `findings` + `dispositions` required breaks validation of old counts-only records (e.g. the fedaot-kb record that triggered the audit).
- Decision: accept the breaking change. Old records are historical snapshots; no migration. The SKILL.md + install.md note the schema version change.
- Why: a required field is the only shape that cannot silently re-create the audit's hole; migration machinery for a record format that has existed for weeks is over-engineering.
- Rejected: migrating old records / keeping the fields optional for back-compat — historical records are immutable evidence, and optionality re-opens the counts-only hole.

## ADR #4 — Escalate target under-defined in the reconciliation table (known gap, made explicit)

- Context: SKILL.md step 2's reconciliation table row "different-family-only→escalate" names no target; the skill's only named escalation target is the human (cap-hit / stalemate lines). The dogfood log records the under-definition.
- Decision: the `escalated` disposition value states the target explicitly (the human) in the SKILL.md step-2 wording, and this ADR records the gap so a future edit can make the table row itself name the target.
- Why: an escalated finding's disposition must be traceable to where it went; silently leaving the target implicit re-creates the untraceability class of defect this log exists to prevent.
- Rejected: leaving the row as-is and letting the disposition omit the target — the record would say "escalated" without saying where.
