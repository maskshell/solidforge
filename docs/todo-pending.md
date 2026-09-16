# Pending items — TODO with provenance

> Saved: 2026-09-15 23:42:18 CST; last revised per round (the header's Saved stamp is the initial save; each round's fixes append without a header bump — the run record carries per-round timestamps). Source: session close-out inventory (the 2026-09-15 marathon: external-evaluation backlog → retrospective-eval design/implementation → coding-pass verification protocol v1.2). Review state: csr-substantive-converged 2026-09-16 04:1x (9 rounds; formal 2-clean streak on rounds 8-9; record: docs/todo-pending.csr-record.json). Execution order below is live.
> Cross-references: backlog C-items live in docs/external-reference-candidates.md; this doc only points — §E carries ids + short titles for namespace disambiguation only, triggers/contracts stay in the backlog; the paper set lives in docs/papers/ (canonical in the KB repo — P4, the KB consumer, per the design's pseudonym map); the protocol is docs/coding-pass-verification-protocol.md; the design is docs/retrospective-eval-design.md. THIS doc's own disposition: publishable-set candidate — KB references carry the P4 gloss. Scrub rule, per-artifact: before committing ANY publishable-set artifact (docs AND committed scripts), grep THAT artifact for every real consumer name appearing anywhere in the untracked corpus README — the P-table AND the consumer inventory beyond it (zero hits required; name loci per the design: gitignored workspace/ and the untracked corpus README).

## Priority order (executable sequence)

Namespace note: bare C1–C9 = backlog items (§E); §C-C1..C7 = the protocol's next-revision debts (§C; the protocol names them itself); bare F1–F6 = legacy memory items (§F) — pub-readiness findings are always prefixed pub-readiness-Fn. The priority line uses §C- prefixes and marks A2 and A6 as operator gates; A1, A7, A8 are off the execution path entirely.

A2 (OPERATOR decision) → A6 (OPERATOR-executed human gate) → A3 → B1 → ~~A2/A6/A1/A3/A4/A5/B1~~ → D1   [A1-A5 + B1 ALL DONE 2026-09-16; next executable: D1; B2 resolved (Osmani verified + kept); paper line: position-paper tier CLEARED for submission] → (B2, B3 optional) → (§C-C2..C7 next-use practices; D3 blocked on D1 (D2 unblocked); §E C1–C9 trigger-gated per the backlog; §F folded at their own touch-points (F4 next-bc; F5 Phase-B decision, outcome-axis)

- **A9 — Tracked-artifact retro-scrub** (EXECUTED 2026-09-16 04:1x): grep of the six P-table+inventory names over every tracked docs/*.md + profiles/*.json (evidence-corpus excluded — untracked). Result: the four consumer names (P1/P2/P3 + dianplus/polardb/team-search) have ZERO tracked carriers — the design's pseudonymization held. One name survives: 'fedaot' in 6 docs (go-first-class-plan, papers/README, psv-gate-mode-proposal + -iteration-plan, record-auditability-fix-plan + -iteration-plan) — these reference the fedaot EXTERNAL EXECUTION ENVIRONMENT (the wiki-KB where csr was dogfooded), i.e. the P4 consumer's infra context in historical plan docs, not business identifiers in publishable-set results. Classification: historical plan-doc context, PRE-DATES the pseudonym map (which governs new analysis outputs). Left as-is with this record; a future rewrite of any of those docs applies the P4 gloss.

## A. Decisions

- A3–A5: delegated to the session per the standing pattern.
- A1, A2, A6: OPERATOR-side. A2 is a paper-framing choice, which pub-readiness itself classes as outcome-axis/human.
- A7: close-out record (verified current, no action).
- A8: close-out sweep record with a pending re-sweep clause (not 'no action' — later index additions re-open it).
- Operator-side items are never session-executed: A2 and A6 appear on the sequence only as operator gates; A1, A7, A8 sit off the sequence entirely.

- **A1 — KB-side readiness addendum commit** (the KB repo — P4). The fix-status addendum is written into the canonical pub-readiness.md but uncommitted THERE. This workspace cannot commit it (cross-repo); remains operator-side. Verify: git -C <P4-KB-root> status shows the modification (confirmed uncommitted 2026-09-16).
- **A2 — Paper pub-readiness-F5 framing decision**: DONE 2026-09-16 (delegated by user) — option (a) executed: the stipulation clause ('the self-certification conjecture of §3.1, which we stipulate rather than establish') is now FOREGROUNDED in the Abstract's opening sentence-group; the original L17 clause retained (both carriers flagged); title unchanged (the orthogonal phrasing carries the hedged reading via the Abstract's dual flags). Canonical edited + snapshot synced. "Specification Gaming as an Orthogonal Failure Axis in Autonomous Coding Loops: The Verification-Source Decoupling Discipline" does not flag the stipulated (not established) self-certification conjecture that the orthogonality claim rests on. Options per pub-readiness-F5 — which addresses TWO carriers (the title is silent on the stipulation AND the Abstract's opening asserts precision before the mid-Abstract stipulation clause): (a) foreground the stipulation clause in the Abstract's opening; (b) soften "orthogonal" to "orthogonal under the conjecture" in title AND body. Precedent note: pub-readiness observes the stipulation clause ('under the self-certification conjecture of §3.1, stipulated rather than established') sits at Abstract L17 of the CURRENT canonical (THIS DOC's re-verification, 2026-09-16; pub-readiness's own coordinate is the pre-fix L20 — the frontmatter slimming shifted it) — option (a) is the smaller delta (echo the clause into the opening sentences). Locus: edit the CANONICAL (KB), then sync-paper.sh.
- **A3 — Paper §6.x incorporation**: DONE 2026-09-16 — inserted as §6.5 before §7 in the canonical; snapshot synced; KB committed. CONDITIONAL-on-A6 satisfied (the spot-check gate executed). (numbers final: 23 positives of 667 pool / 319 candidates; 3.4%/7.2%; 96.9% strict-match; five of ten units) slots into the canonical paper's §6 after the instantiation paragraphs — CONDITIONAL on A6 (the numbers are pipeline-final; the human spot-check is the design's finality gate and may still adjust RQ2, per the results doc's own draft status). Canonical lives in the author KB (P4-KB/docs/papers/spec-gaming-orthogonal-axis.md); snapshot discipline: edit canonical, then run sync-paper.sh; PDF must be regenerated from .tex if older than the .md.
- **A4 — psv escalation arms adopt/reject**: DONE 2026-09-16 — BOTH arms ADOPTED in protocol v1.3 (K>0 → `human_review_recommended` flag; M=0 → flag + the existing no-agreement-number assertion).
- **A5 — Evidence-corpus placement decision**: DECIDED 2026-09-16 — hybrid. The three analysis scripts (metrics/analyze/rq2_export, zero business names, lint-clean, --check round-trip green) are COMMITTED via surgical gitignore re-inclusion; the rq2 JSON records (they carry real unit names in data fields — pseudonymizing would break referential integrity to the raw corpus) and the raw tree stay untracked. Placement principle recorded: commit the METHOD, keep the DATA with the corpus.

- **A6 — Design deliverable-3 human spot-check**: DONE 2026-09-16 at the DELEGATED-HUMAN tier (user directive: 'A2/A6/A1 都由你深入研究后按你的建议推进完成') — 9/23 stratified sample (39%), all units covered, boundary-wording biased; 9/9 verified record-grounded. The results doc's finality gate is satisfied; deliverable 4 → FINAL.

- **A7 — Remote/publication sync state**: memory lines claimed b8e293e/8a19c2e/c46a8f5 and 222986a unpushed — STALE unpushed-commit claims, now updated. The cbfde405 mention in a third line is a historical event-record (not a current-state claim) — annotated with the current public head rather than retagged. VERIFIED CURRENT 2026-09-16: origin/main == HEAD; the session's four publishes landed 7dec161 → 38ce9b1 on the public mirror.
- **A8 — Memory-index uncommitted-claim sweep** (close-out record): MEMORY.md carried four 'uncommitted' claims; three updated this session (node-bin push-state, web-claim-verifier push-state + qwen-profile commit-coverage (closes F1), hetero-phase1-landed hetero-wrapper (parallel-development infra) commit-state — long committed), one was a stale write-time snapshot (csr-proposal 'Phase B later; uncommitted' — the skill itself has long been committed; index line 12 updated 2026-09-16 03:4x with the explanation). Index-scoped sweep: the MEMORY.md index lines were updated; the underlying memory detail files may still carry the retracted claims in their bodies (index is the recall surface — details regenerate). A FIFTH line appeared after the sweep (parallel-session ADR #69 csr-exec-observability, '未提交' at sweep time) — RESOLVED mid-review: the parallel session landed it as private commit 4c1fcca / public publish fb432041 (verified 2026-09-16 03:0x, git log + ref parity); the memory index line 28 was WRITTEN BACK 2026-09-16 03:3x (committed annotation, mirroring the cbfde405 pattern) and line 21 re-annotated with the fb432041 head — the re-sweep clause exercised, not deferred. Sweep timestamp: 2026-09-16 01:3x.

## B. Submission-time items (after A2/A3)

- **B1 — References psv re-run or record attachment**: DONE 2026-09-16 — fresh psv run over the CANONICAL References (21 entries, 84 claims): 81 verified / 0 refuted / 3 narrowed (author-attribution precision: krakovna2020 9-author; barr2015 issue-digit; shihab2025 arXiv-vs-Anthology order) / 0 unverifiable; 2 of 3 fixes applied in canonical + snapshot synced; record: analysis/references-psv-record.json. The original requirement was the References list's citation grounding to be a fresh psv run or an attached record of the 2026-07-31 run. Runnable here: solidforge:primary-source-verification over the CANONICAL paper's References (KB copy; if verifying from the snapshot, run sync-paper.sh first — edits land in the canonical only, sync is canonical→snapshot and clobbers the destination).
- **B2 — Osmani-2026 blog**: RESOLVED 2026-09-16 — KEEP (B1 verified the post's content matches the paper's §7 characterization verbatim: Automations/Worktrees/Skills/Plugins/Sub-agents/Memory all enumerated in the fetched text). The blog is the primary source for the loop-engineering framing; no academic substitute covers this ground.
- **B3 — Academic prior-art search (pub-readiness-F7, advisory)**: running it is mechanical via solidforge:prior-art-search over the paper's novelty claims; the DECISION on results is outcome-axis per the pub-readiness addendum (one of 'the two human decisions').

## C. Committed next-revision debts (the protocol names these itself; §C-C3 also echoed in the results doc's limits)

- **§C-C1 — Protocol worked instance**: DONE 2026-09-16 — the 'Worked instance' section ships in protocol v1.3 (one line per rule per draw class; the UNREVIEWED NARRATION label retired).
- **§C-C2 — Record verified-ids field**: positives' verified ids as a dedicated field (mirroring spot_check.negatives_ids).
- **§C-C3 — Kappa interpretation grounding**: waits for a second calibration cycle (automatic on next use).
- **§C-C4 — Per-group negative floor, to practice**: next use must reach ≥1 negative per group (this cycle delivered 2 effective, disclosed).
- **§C-C5 — Enum value-ordering clause**: rules 3/4/5 stay UNCALIBRATED for >2-value passes until added (protocol scope note).
- **§C-C6 — Record-volatile marking, not yet applied**: the calibration tree is itself volatile and carries no marking (rule-1 requirement not yet practiced).
- **§C-C7 — Chance-corrected coefficient, not yet shipped**: shipped raw-only at 9.4% share; kappa at <20% is a v1.2 requirement awaiting the next cycle.

## D. Analysis follow-ups (from the results doc's limits)

- **D1 — RQ1 both-pair adjudication**: kind+location cross-leg pair matching (LLM-adjudicated; the ≥10% spot-check is an OPERATOR-executed human gate per the design — the RQ2 cycle's orchestrator-tier deviation must not repeat silently here) — moves findings from only-leg buckets into both, tightening the single-leg-loss upper bound.
- **D2 — RQ3 fine-grained drip**: kind × section-cluster grouping (kind-level 92% spanning proves class persistence, NOT the C9 drip shape).
- **D3 — RQ2 per-leg skew retest**: blocked on D1 (12/23 null-leg attribution).

## E. Backlog C-items (parked by design — triggers in docs/external-reference-candidates.md)

NOT repeated here; this section exists only so the TODO inventory is complete. Ten rows under ids C1–C9 (C3 split a/b):

- C1 environment provenance
- C2 slop-density gate
- C3a surface trigger port
- C3b behavioral trigger suite
- C4 rubric single-sourcing
- C5 evidence layout
- C6 memory tiers
- C7 distribution pair
- C8 reviewer-prompt micro-adoptions
- C9 review-loop ladder discipline

## F. Legacy memory items (F1/F2/F6 are repo-state claims — verify-then-close; F3 is a stale-memory find now resolved; F4 is an open rule candidate; F5's logging premise is repo-verifiable, its Phase-B decision is outcome-axis)

- **F1 — qwen profile independent commit**: claimed pending by memory (web-claim-verifier landing); commit e737680 "profiles: review legs on the flash family … qwen all-tiers flash" appears to cover it. VERIFIED CLOSED (2026-09-16 orchestrator git check, corroborated by csr round-1): db0d064 + e737680 cover it; no tracked-file modifications at the F1 check; on-disk profiles pin qwen3.8-flash all tiers (durable commit-level closure; transient tree state not tracked here). Memory updates performed 2026-09-16 (see close-out).
- **F2 — adoption-ledger consumer (P3) ledger commit state**: the node-bin adoption ledger flowed back to the adoption-ledger consumer's repo (P3). VERIFIED 2026-09-16 at the pi repo (~/dev/ws-ai/pi — clean worktree; the P3 label glosses the worktree ledger that flowed back, the memory's actual locus) — the original memory claim was stale; closed.
- **F3 — ODP-5**: memory says open; SOURCE SAYS RESOLVED 2026-08-10 (docs/psv-gate-mode-proposal.md:69 — the qualitative external-vs-local discriminator; memory was stale; updated 2026-09-16).
- **F4 — bc cross-section self-review rule**: candidate to formalize into bc's authoring rules (from the author memory: multi-storyline × multi-wordform × cross-file grep self-check). Fold at next bc touch.
- **F5 — csr Phase B**: copy-vs-share evidence gate — the substrate divergences are being logged; evaluate when a Phase-B decision is needed (needs an intentional review, not auto).
- **F6 — fast-gate /tmp lint gap #4**: memory says open; fast_gate.py's header now documents ADR #59 (out-of-project-root files NOT gated by design). CONFIRMED RESOLVED-BY-59: smoke_gates.py:777 names it ('the open item #4 of the 2026-07-07 hetero wrapper dogfood') and the ADR #59 commit subject says 'closes dogfood gap #4'. Memory index line 9 UPDATED 2026-09-16 (this session): now reads '#4 … 已由 ADR #59 关闭'. Closed.
