# Record-Layer Auditability — Third-Party Assessment Re-Review + Fix Plan

> Status: **Plan (no code change yet).** An external project (fedaot-kb) applied this workspace's `cross-source-review` (csr) and `primary-source-verification` (psv) skills to `docs/plans/borrow-from-pi-llm-wiki.md`, and a third party audited the resulting records. This document (a) embeds that assessment verbatim, (b) re-checks every claim it makes against the actual artifacts and code, with a confirmed / partially-confirmed / refuted verdict per point, and (c) names the fix set. Verdict scale in the adjudication table: **confirmed** / **partially confirmed** / **refuted** / **misdirected** (claim targets the wrong store or object — treated as refuted on its own terms) / qualified confirmations (e.g. "confirmed, not a violation"). This document ITSELF then goes through the pipeline it criticizes: csr → psv → bc → pd (workspace rule 13 chain). Records land as sidecar files in this directory.
>
> Scope: the record layer of `skills/cross-source-review` + `skills/primary-source-verification` (+ one environment gap). NOT a review of fedaot-kb's content or of `parallel-development`'s core (its run-record is touched only as evidence). One fix item (D) lands in the external fedaot-kb repo and is executed AFTER this pipeline, separately.
> Companion rubrics: [CLAUDE.md](../CLAUDE.md) workspace rules (esp. 1, 3, 4, 10) + [cross-source-review SKILL.md](../skills/cross-source-review/SKILL.md) + [primary-source-verification SKILL.md](../skills/primary-source-verification/SKILL.md).

## Context — how the assessment reached this workspace

- External project: fedaot-kb (local repo at `/Users/solosus/dev/ws-wiki/fedaot-kb`), a wiki knowledge-base platform that consumes this workspace's skills.
- Artifact under review there: `docs/plans/borrow-from-pi-llm-wiki.md` — a borrow-assessment proposal that went through csr (3 rounds) + psv (58 claims) + prior-art-search.
- Records the audit examined: `docs/plans/borrow-from-pi-llm-wiki.csr-record.json` + `.psv-record.json` (both in the fedaot-kb repo).
- The assessment was relayed by the workspace owner (this repo's user) from the external project's side. It is NOT a file on disk anywhere (provenance check 2026-08-08: grep for the appendix's distinctive phrases across both project repos + `~/.claude` — only this document matches); it is embedded verbatim in [Appendix A](#appendix-a--third-party-assessment-verbatim) so this document is self-contained and the claims below have a fetchable adjudication source.

## Verified fact profile (this session, grep/read-counted)

Distinguished from assertions: everything below was verified by reading the named artifact this session.

1. `skills/cross-source-review/infra/schemas/convergence-record.schema.json` round shape is counts-only: the count fields are `same_source_findings`, `hetero_findings`, `blockers`, plus the ordinal `round` and the boolean `hetero_degraded` (schema lines 60–72). No per-finding retention.
2. `infra/scripts/converge.py` RECEIVES full findings per round (`same_findings`/`hetero_findings` arrays, lines 231–232) but emits only counts into the record (lines 258–267). The finding detail is discarded at the record boundary.
3. csr SKILL.md step 4 (Emit) promises a "per-round findings trend" (SKILL.md line 53) — the record's only findings-reporting content, not a per-finding packet (contrast psv step 4's "plus a doc-findings packet"); the schema delivers exactly that: a trend, not the findings.
4. psv SKILL.md step 4 mandates "emit a `coverage-record` … plus a doc-findings packet" (SKILL.md line 57) — but the fedaot-kb repo contains only the counts-style `psv-record.json`. Grep for claim ids `C57`/`C28` across fedaot-kb `docs/` TEXT sources hits only the record file itself (a binary fetched PDF — the repo's `docs/references/docling-tech-report.pdf`, the only repo PDF with a raw-byte hit — carries the bare string in its raw bytes (`grep -a` match at offset 672115) but not in its rendered text (`pdftotext docs/references/docling-tech-report.pdf - | grep -c 'C57'` → 0); grep behavior is tool-dependent, verified 2026-08-08: this shell's default `grep` (ugrep 7.5.0, via profile) skips the binary (exit 1, no output) while GNU grep 3.12 (the PATH binary) and BSD `/usr/bin/grep` report the binary match; excluded as noise — the exclusion rests on the rendered-text fact, not on any grep exit code): the per-claim packet with fetched quotes was NOT persisted. Consequence: the psv record's assertion that the 5 narrowed claims (C28, C36, C42, C49, C54) "均附 fetched 引文" and its cited verifier corrections (C15, C45) rest on quotes that live only in the unpreserved packet — NOT re-checkable today; they are out of this document's adjudication surface. The psv run's fetched base (`/tmp/pi-llm-wiki` clone) currently exists and is re-fetchable (verified 2026-08-08: shallow clone with complete checkout — `.git/shallow` present — containing the psv adjudication sources `docs/architecture.md`, `docs/superpowers/specs/2026-08-02-okf-foundation-design.md`, `docs/superpowers/specs/2026-08-02-okf-v0.2-interoperability-design.md`, `AGENTS.md`, `prompts/`), but /tmp is volatile and may disappear; the run-time packet was not persisted anywhere — verified absent from both the clone and the fedaot-kb repo.
5. The audit's round numbers are all accurate against `borrow-from-pi-llm-wiki.csr-record.json`: round 1 = 6+5=11 findings / 2 blockers / rewrite; round 2 = 9+7=16 / 0 blockers / pass; round 3 = 6+4=10 / 0 blockers / pass.
6. The assessed claims' memory sources DO exist on disk: `~/.claude/projects/-Users-solosus-dev-ws-wiki-fedaot-kb/memory/{project-self-evolution-architecture,project-self-evolution-plan,project-memory-design-borrowables,project-pipeline-performance}.md` (the fourth file is C57's adjudication source — fix D line 89). `project-self-evolution-architecture.md` lines 17–23 enumerate exactly three knowledge-entry paths (A `submit_knowledge()`, B `research_topic()`, C manual ingest). These files live inside the `~/.claude` git work tree (toplevel `/Users/solosus/.claude`) under a blanket `.gitignore` `*` — tracked by no repo, hence unversioned (row 2a). The audit's "磁盘不存在" (does not exist on disk) is FALSE.
7. Graphiti was never the adjudication surface for these claims. The psv record's own coverage notes name the sources, verbatim: "裁决源全部本地可 fetch（/tmp/pi-llm-wiki 克隆仓库 + fedaot-kb 仓库 + memory 文件），无 paywall；fetch 过程两处被 verifier 独立复核纠正（C15 命令真实存在、C45 grep 描述不精确）" and "C57 以 memory 为裁决面（agent memory 非权威信源，仅裁决 claim↔text 保真度）" (psv-record.json coverage lines 27, 29). The audit's Graphiti search was directed at the wrong store.
8. The audit's remediation target for the borrow doc is partially valid. `docs/retrieval-memory-evaluation.md` (fedaot-kb) corroborates L5 (all three EverOS items: §2.5 announces the three borrowables, §3.1–3.3 enumerate them — content-hash incremental compile, predictable-classification, evolver-reflection persistence) — verified by reading it. That same file does NOT carry L3's "已有 3 路径" enumeration framing: its own 路径 mentions name the knowledge-entry paths (手工写页 / research_topic / staging) only in compile-gate-bypass context (retrieval-memory-evaluation.md lines 23, 60), and it cross-references `docs/wiki-common/knowledge-trust-tiering.md` (line 129) — the 信任分级 half of L3 has durable anchors there. The A/B/C path enumeration does have a durable anchor elsewhere: `docs/staging-usage.md` line 3 ("所有外部知识（手动录入、Agent 提交、研究报告）均先进入 Staging…") maps C 手动 ingest = 手动录入, A submit_knowledge = Agent 提交, B research_topic = 研究报告 — the memory file's enumeration is the same three paths in different wording.
9. `pyproject.toml` dev deps lack `jsonschema`; `converge.py` docstring (lines 24–26) tells the operator to run under `uv run --with jsonschema ...` — the standard environment takes the degraded path by default.
10. `skills/parallel-development/infra/schemas/run-record.schema.json` is also counts-only (`findings_count`, line 105–109). csr's counts-only record mirrors pd's run-record by declared field alignment (schema description), but csr has NO code dependency on pd — it can embed findings without waiting for pd.
11. The audit itself acknowledges the jsonschema degradation was disclosed ("有披露，好"). Disclosed degradation is exactly what workspace rule 3 prescribes (never silent green; degrade to a documented no-op). The audit's characterization "已披露的灰色而非绿色" is accurate and does NOT constitute a rule violation.

## Adjudication of the assessment

| # | Audit claim | Verdict | Evidence |
| --- | --- | --- | --- |
| 1a | CSR record has counts only, no finding-level disposition | **CONFIRMED** | Facts 1–3; `converge.py` discards findings at the record boundary |
| 1b | 16 round-2 / 10 round-3 non-blocker findings untraceable; `substantive_converged` rests on reviewer severity | **CONFIRMED** | Fact 5; blocker-ness is the reviewer's `severity` call (doc-findings.schema.json) and the record retains no basis to re-judge it |
| 1c | Same defect applies to psv (per-claim packets not persisted) — **doc's own inference, not the audit's claim** (Appendix A names only the csr counts defect + the psv authority_ref suggestion) | **CONFIRMED** | Fact 4 — the audit did not name psv's packet gap; the same standard applies |
| 2a | Memory sources: "git 从未跟踪（0 文件）" | **CONFIRMED** | memory dir is inside the `~/.claude` git work tree but blanket-ignored (`.gitignore` line 2 is a bare `*`), hence untracked and unversioned; it is outside both project repos. Coverage note: the audit's "0 文件" is ambiguous between a tracked-count and an existence reading; CONFIRMED holds under the tracking reading, and row 2b adjudicates the existence reading separately |
| 2b | Memory sources: "磁盘不存在" | **REFUTED** | Fact 6 — all four files exist (the three L3/L5 files + C57's source `project-pipeline-performance.md`); content matches the claims (3 paths; EverOS items) |
| 2c | "Graphiti … 检索不到对应 episode" | **MISDIRECTED** | Fact 7 — Graphiti was never the oracle for these claims |
| 2d | Core volatility point: sources repo-external, unversioned, deletable → auditor cannot re-fetch | **CONFIRMED** | row 2a's scope note (memory dir inside the `~/.claude` work tree, blanket-ignored → untracked, unversioned); this is the durable, actionable core |
| 2e | Repoint doc memory references to `docs/retrieval-memory-evaluation.md` | **PARTIAL** | Fact 8 — census is FOUR lines (22, 43, 89, 142); the borrow doc cites NO `retrieval-memory-evaluation.md` itself (verified: the string appears nowhere in it — the repoint is a replacement, not a re-citation). Line 43's EverOS item (`project-memory-design-borrowables` list) → repoint to `docs/retrieval-memory-evaluation.md`: valid; line 22's EverOS ref (`project-memory-design-borrowables` 借鉴) → same repoint: valid, but line 22's `project-self-evolution-*` refs → invalid for that target (L3 sources — repoint to `docs/staging-usage.md`); line 89 → invalid (`project-pipeline-performance`, C57's source); line 142 (named by the audit) → valid for its EverOS/borrowables refs, invalid for self-evolution-*; per-line mapping in Fix D |
| 3 | jsonschema degradation: disclosed gray, not green | **CONFIRMED, not a violation** | Fact 11 — rule-3 compliant; env fix is trivial (Fact 9) |
| 2f | L3's "3 路径" count "完全落在挥发源上，无法复验" | **REFUTED on re-verifiability; CONFIRMED on the borrow doc's citation volatility** | Fact 8 — the A/B/C enumeration is durably anchored at `docs/staging-usage.md` line 3 (re-verifiable today); the borrow doc's citation of `memory/project-self-evolution-*` remains volatile until fix D repoints it |

## Fix set

Each item: mechanism → landing → acceptance. This set is the bc input for the implementation plan.

### A — csr convergence-record embeds per-round findings (required) + dispositions

- Mechanism: each round in the record carries the reconciled findings array (same-family + hetero, de-duplicated) AND a per-finding disposition list. Finding shape — the doc-findings fields (the schema's `$defs/finding` field set, already validated by `converge.py` when jsonschema is present), one per line:
  - `defect_id`
  - `severity`
  - `kind`
  - `location`
  - `evidence`
  - `suggestion`
  Disposition values (one per line, each with the orchestrator's reconcile rationale):
  - `fixed` — accepted, artifact revised
  - `rejected` — declined, with rationale (incl. coverage disclosures: not defects, carried in the record's coverage notes)
  - `escalated` — the reconciliation table's different-family-only→escalate row (SKILL.md step 2; the row itself names no target — the skill's only named escalation target is the human, cap-hit lines 14/51), neither fixed nor rejected
  The orchestrator already makes accept/reject decisions at reconcile time (SKILL.md step 2: "revise the artifact per accepted findings, or reject a finding with rationale") — today that decision is discarded.
- Landing:
  - `convergence-record.schema.json` — round gains required `findings` + required `dispositions`
  - `converge.py` — pass-through (it holds the findings in memory; emit them) + run.json input shape (per-round `dispositions` array: defect_id → fixed/rejected/escalated + rationale — the engine's new required input)
  - SKILL.md step 2 — record accept/reject/escalate + rationale per defect_id at reconcile time (the PRODUCING step for dispositions)
  - SKILL.md step 4 — "findings trend" → "per-round findings + dispositions"
  - `infra/test/convergence_policy_check.py` + `findings_shape_check.py` fixtures
- Acceptance: a reader of the record can list every finding per round, its severity, and what was done about it; `pass` with N findings becomes legible (pass = no NEW blocker; advisory findings remain advisory by workspace rule 4).

### B — psv per-claim packet persisted; volatile-authority rule (flag, not forbid)

- Mechanism (two parts):
  - Persistence: the per-claim doc-findings packet (refuted / narrowed / unverifiable findings with claim_ref / verdict / source_ref / fetched quote) becomes a file beside the coverage-record, per the SKILL.md's already-mandated "plus a doc-findings packet" — the packet shape stays as SKILL.md defines it (verified claims stay counted-not-listed).
  - Volatile-authority rule: an authority source is classified durable (repo-local, versioned) vs volatile (e.g. `~/.claude/projects/` memory, `/tmp` clones). A claim adjudicated against a volatile source keeps its verdict but carries a `volatile_authority` flag; the coverage record carries a volatile-authority registry — claim_ref → volatile source — covering ALL claims, verified ones included (their sources are counted-not-listed in the packet, so the registry is their only re-fetchability signal). The extractor guidance prefers a durable in-repo source when one exists (the fedaot-kb remediation, fix D, is the first instance).
- Landing: psv SKILL.md (emit step + extractor guidance), `coverage-record.schema.json` (volatile-authority registry), claim packet shape.
- Acceptance: every non-verified finding's source is re-fetchable; every volatile source is flagged in the registry; verified-claim sources are re-fetchable wherever the claim's authority was volatile.

### C — jsonschema into dev deps

- Mechanism: add `jsonschema` to `pyproject.toml` `[project.optional-dependencies] dev` + `[dependency-groups] dev`. The graceful-skip machinery in `converge.py` stays as the bare-python fallback (rule 1), but the standard environment stops taking the degraded path.
- Coverage note: the audited degradation occurred in fedaot-kb's run — its environment (own `.venv` / `pyproject.toml`, jsonschema absent there too) is external and is NOT remediated by this fix set; fix C prevents the same gap in this workspace's environment. The fedaot-kb env gap is tracked as a follow-up to fix D's handoff.
- Landing: `pyproject.toml`.
- Acceptance: `converge.py` under the repo venv validates findings-schema + record without the SKIP note.

### D — fedaot-kb doc remediation (EXTERNAL repo, after this pipeline)

- Mechanism: repoint ALL memory-file references in `docs/plans/borrow-from-pi-llm-wiki.md` (census by `grep -n 'memory .*project-'` = lines 22, 43, 89, 142). Reference repointing ONLY — any claim-wording changes belong to fedaot-kb's own review process; this plan does not modify fedaot-kb content. Line 43 carries BOTH the EverOS three-item list (P1 — the borrow doc's primary proposal slot, trajectory→skill distillation, defined at borrow-from-pi-llm-wiki.md line 43 — the L5 anchor → `docs/retrieval-memory-evaluation.md`, corroboration verified) AND the load-bearing 3-paths assertion (L3 → `docs/staging-usage.md`, the durable in-repo anchor verified in Fact 8); the EverOS part of line 22 → `docs/retrieval-memory-evaluation.md`; line 89 (`project-pipeline-performance` — C57's adjudication source) → a durable in-repo ETL source (the parallelization code under `src/etl/`); lines 22/142 are citation lines only and are repointed to the same durable sources their content maps to.
- Landing: fedaot-kb repo — executed separately, NOT by this pipeline's pd.
- Acceptance: every memory reference in the doc resolves to a tracked artifact.

### E — self-gates green before commit

- Mechanism: csr + psv + pd test suites pass after A/B/C (workspace rule 1: a skill's own self-gates are the definition of done).
- Landing: `skills/cross-source-review/infra/test/*`, `skills/primary-source-verification/infra/test/*`.
- Acceptance: full test set green; no `coverage` note that could be eliminated by the env fix.

## Pre-ADR design decisions (recorded before bc; ADRs land in `skills/cross-source-review/docs/design-decisions.md` — sibling-skill convention, e.g. psv's `docs/design-decisions.md`; the file will be created when the ADRs land)

- **Embed-vs-external findings (fix A)**: embed the findings in the record. Rejected: separate per-round files — they are orphanable and reproduce the exact volatility sin under audit. Cost: a long-doc record grows by the findings' size (~KB), acceptable for auditability.
- **Flag-vs-forbid volatile authorities (fix B)**: flag, do not forbid. Rejected: the auditor's "禁用不可重取的源" — project-state claims (L3/L5 shape) often have memory as their ONLY source; forbidding kills their verification outright. Flag keeps the verdict honest and the record transparent. The discipline the auditor wants is enforced one level up: the DOC should carry durable citations when one exists (fix D).
- **Schema back-compat (fix A)**: `findings` and `dispositions` become required — a record with findings but no dispositions would re-create the untraceability hole on the "what was done about it" half, exactly the optionality the findings requirement rejects. Old records (the fedaot-kb one) predate the change and are historical; no migration. Rejected: migrating old records / keeping either field optional for back-compat — old records are historical snapshots, and optionality would silently re-create the counts-only hole.

## Scope boundary

- In: A, B, C, E (this repo). D (external repo) is sequenced after the pipeline.
- Not touched: `parallel-development` core, `blueprint-crafting`, `prior-art-search`, fedaot-kb knowledge content (Fix D's citation-string repointing is executed by fedaot-kb's own process — this pipeline modifies no fedaot-kb file).
- The pre-existing uncommitted changes to `skills/*/infra/scripts/profiles/{deepseek,qwen3}.json` (proxy config) are unrelated to this plan and left untouched.

## Pipeline self-description (this document's own journey)

This document goes through the pipeline it criticizes. Records land as sidecars here:

- csr → `docs/record-auditability-fix-plan.csr-record.json` (same-family + different-family; hetero leg needs `.env.solidforge` DEEPSEEK token — present in this repo).
- psv → `docs/record-auditability-fix-plan.psv-record.json` + per-claim packet (adjudication sources: this document + the artifacts in the verified-fact profile + the embedded Appendix A).
- bc → iteration-plan for fixes A/B/C/E (consumed by pd).
- pd → implementation + self-gates green.
- Fix D lands in fedaot-kb afterward, separately.

## Appendix A — third-party assessment (verbatim)

> 外部项目在应用本项目某些skill后，第三方对结果做的评定：
>
> 记录层的两个可审计性缺陷
>
> CSR 记录只有计数，无 finding 级处置。round 1 是 6+5=11 findings / 2 blockers / rewrite；round 2 变成 9+7=16 findings / 0 blockers / pass——findings 变多却翻判，只有"blockers 清零"能解释，但 16 条非阻断 finding 是什么、为何放行，记录不可回溯。round 3 仍有 6+4=10 条 findings 而 verdict 为 pass。"substantive_converged: true" 因此只能建立在信任审稿人严重度分类之上。另 findings-schema validation skipped: jsonschema absent——门降级了（有披露，好），按本项目"门不得沉默报绿"的宪法精神，这属于已披露的灰色而非绿色。
>
> 裁决源挥发性。L3（"self-evolution 已有 3 路径"）、L5、C57 的裁决面是 memory/project-*.md：git 从未跟踪（0 文件）、磁盘不存在、Graphiti fedaot-kb group 经 search_nodes/get_episodes 均检索不到对应 episode——今天的审计者已无法重取该 oracle。L5 侥幸由持久文档 docs/retrieval-memory-evaluation.md §3/§4 corroborate（三项状态全部吻合）；L3 的"3 路径"计数则完全落在挥发源上，无法复验。建议把 doc 第 22、142 行的 memory 引用改指 docs/retrieval-memory-evaluation.md（落盘版已存在），psv 类管线的 authority_ref 应禁用不可重取的源。
