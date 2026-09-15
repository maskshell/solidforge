# Retrospective evaluation results — solidforge evidence corpus

> Implements `docs/retrospective-eval-design.md` (csr-converged 2026-09-15, 6 rounds). All numbers below are recomputable: `docs/papers/evidence-corpus/analysis/{metrics,analyze}.py` over the untracked corpus (46 units after the 2026-09-15 incremental harvest). Consumer projects appear only as pseudonyms (P1-P4; map in the untracked corpus README). Coding-pass verdicts are LLM-assisted with the human spot-check PENDING (design deliverable 3's human step).
>
> Process-axis results only — nothing here verdicts the loop's effectiveness versus alternatives (no control baseline exists), and outcome-axis conclusions stay human.

## Corpus and units

- 46 units (10 solidforge run dirs + consumer record sets; 3 reference-layer ingests: two recent csr runs + one bonus match, all flagged in metrics-output.json).
- Ingest flags: 22 run-record stubs (all `process_converged: true`), 3 aggregate parse-failures (excluded, disclosed), 1 run.json-sole-aggregate, 3 reference ingests, 2 aggregate-absent substitutes.
- Classifier assertion: ZERO failures across every corpus filename form — the 6-round-hardened matcher holds mechanically.

## RQ1 — multi-leg necessity (leg yield, defect-severity findings only)

| Bucket | Count | Share of attributable |
| --- | --- | --- |
| same-only | 192 | 53.5% |
| hetero-only | 167 | 46.5% |
| both (id-level) | 0 | 0% |
| unattributable | 308 | — |

- **Headline**: among the 359 findings with per-finding leg attribution, the two legs contribute near-symmetrically — each leg alone would lose roughly half of what the pair finds. (Both=0 is an id-level artifact — cross-leg ids never match; kind+location pair adjudication is pending and can only MOVE findings from only-buckets to both, never remove them.)
- Honest bounds: attribution coverage is 359/667 defect findings (54%); the unattributable mass sits in units without leg-separated files (consumer layer, and embedded-array records). Small-N disclosure per design: per-finding attribution exists in 8+ units.

## RQ2 — fix-introduced defect frequency

- Coding pass: 319 pre-filtered candidates (multi-round units, defect severity, fix/round-vocabulary pre-filter) → 23 raw positives; after the consistency re-run the headline is **23 fix-introduced findings (7.2% of candidates; 23/667 = 3.4% of ALL multi-round defect findings)** — the re-run's strict unit+id agreement is 96.9% (62/64) with ZERO genuine pass-1 disputes (an initial 93.8% computation had manufactured 2 spurious 'disputes' via bare-id cross-unit collision — root cause and correction recorded in the record).
- Pre-filter selection bias disclosed: the 319 are enriched for fix-mentioning text; 3.4% (23/667) is the conservative denominator bound, 7.2% (23/319) the enriched one. Truth lies between; both reported.
- Distribution by unit: seam-anchor (bc proposal review) 9, web-claim-verifier 9, prompt-content-spec 2, external-reference-candidates 1, retrospective-eval-design 2 (sums to 23, matching the record) — the pattern is PERVASIVE across runs and engines, not an artifact of recent runs.
- **Leg split of positives: same 9 / hetero 2 / null 12** — the null mass (id-join limits) makes the design's per-leg-skew expectation UNTESTABLE at this coverage; disclosed, not claimed.
- Spot-check: DONE — orchestrator-performed (NOT independent human — disclosed deviation; same-family independence is weaker than the design's human step), record-full-text quote verification, 5/5 positives across all 5 units + 3 negatives drawn; 1 record-lookup miss (unverifiable under docs/coding-pass-verification-protocol.md v1.2 rule 1); 2 effective, zero disagreements. Consistency re-run: second fresh seat, 64-item subsample, 96.9% strict-match agreement; zero genuine pass-1 disputes (2 apparent disputes were bare-id collision artifacts, corrected), 2 pass-2-only finds NOT added (one-directional rule). All details in `evidence-corpus/analysis/rq2-coding-result.json`.

## RQ3 — class-discovery dynamics

- At the design's kind granularity (6 buckets), 51/55 classes (92%) span >1 round. **Honest reading**: with only 6 coarse kinds, spanning is structurally common in multi-round runs — this CONFIRMS persistence of classes but is WEAK evidence for the fine-grained drip premise (backlog C9's "one instance per round" shape). Finer grouping (kind × section-cluster) is the named follow-up.

## RQ4 — loop economics (multi-round units only)

- 16 multi-round units: 11 substantive-converged (69%), 2 stalemate (13%), 3 other (cap-hit/malformed-class, 19%).
- Blocker decay across rounds is visible in the two recently-televised runs (4→3→2→1→0→0 and 7→...→converged) but heterogeneous across the corpus — per-unit series in metrics-output.json.
- Stub layer (22 run-records): 100% process_converged — the single-loop engines' recorded runs all converged on process axis.

## Confound coverage (annotation layer, index v2)

- Environment provenance recovered for a minority of units (sidecar/leg-file/record-internal); the majority remain `unknown` — consistent with the C1 gap measurement (79% of records lack env fields). Every cross-run comparison above is era-unstratified; the coverage % ships in index-v2.json and bounds any era-sensitive claim.

## Honest limits (in addition to the design's)

- The both-bucket (RQ1) and per-leg skew (RQ2) are both bottlenecked by id-level attribution; both need the pair-adjudication pass — reported as pending, not resolved.
- RQ3's kind granularity is coarse by design; its 92% must not be cited as drip-proof.
- The coding pass is one LLM seat; its consistency re-run (96.9% strict-match agreement, bare-id artifact corrected) is reported alongside. Kappa under class imbalance remains a named open item (verification docs/coding-pass-verification-protocol.md rule 4); the design's human spot-check step remains PENDING (orchestrator-tier deviation disclosed; never superseded).
- Corpus completeness: the harvest is a read-only snapshot; runs deleted before harvest are absent (survivorship), and the 2026-09-15 incremental addition is itself an admission that freshness matters.

## Deliverable status

| # | Deliverable | Status |
| --- | --- | --- |
| 1 | Annotation layer (index v2) | DONE — `evidence-corpus/analysis/index-v2.json` |
| 2 | metrics.py + normalization table | DONE (table inline in metrics.py constants; script lint-clean, assertions green) |
| 3 | RQ2 coding pass | DONE — LLM pass + orchestrator-tier spot-check + 96.9% consistency re-run (tier deviation disclosed; human step pending (orchestrator-tier deviation disclosed)) |
| 4 | Results doc | THIS DOCUMENT (draft — spot-check may adjust RQ2) |
| 5 | Paper integration draft | DRAFTED — `docs/papers/retrospective-section-draft.md` (pending author incorporation into the canonical paper) |
| 6 | Dedup arithmetic | DONE — `evidence-corpus/analysis/dedup-arithmetic.json` (raw vs unique per unit) |
