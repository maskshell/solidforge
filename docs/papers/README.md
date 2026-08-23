# The paper: vendored snapshot

This directory carries a **verbatim snapshot** of the paper *Specification Gaming as an
Orthogonal Failure Axis in Autonomous Coding Loops* so the repo is self-contained and
citable even before the paper lands on arXiv.

Why THIS repo vendors it: the paper is load-bearing for solidforge twice over — (1) the
orthogonal-axis frame (same-family vs different-family verification) behind
[USER_GUIDE](../../USER_GUIDE.md)'s degradation/defense model, and (2) the ORIGIN of the
`primary-source-verification` skill: the paper's own cross-source-review pass let
citation misattributions slip that only independent primary-source spot-checks caught —
the exact gap that skill closes (`skills/primary-source-verification/docs/proposal.md`).
The provenance trails below RAN on this workspace's own skills (csr / psv dogfood).

## Artifacts

| File | Role |
| --- | --- |
| `spec-gaming-orthogonal-axis.md` | Text authority (canonical snapshot, copied verbatim; `last_updated` in its frontmatter) — diffable, reviewable, searchable |
| `spec-gaming-orthogonal-axis.pdf` | The citation artifact — built from the text via LaTeX, after the last text edit |
| `spec-gaming-orthogonal-axis.tex` | LaTeX source of the PDF (GENERATED from the text; rebuildable — the .md is the authority) |
| `spec-gaming-orthogonal-axis.pub-readiness.md` | Publication-readiness review + proposed fixes (context, not part of the paper) |

### Provenance trails (the paper dogfooded on itself)

| File | Role |
| --- | --- |
| `spec-gaming-orthogonal-axis.convergence.json` | The paper's csr convergence record (3-round reconvergence of 2026-07-31, of the 4-round 2026-07-08 pass; schema-validatable) |
| `spec-gaming-orthogonal-axis.loopx-reconvergence.json` | The LoopX-amendment reconvergence delta (§7 peer paragraph + §4.4 control-plane note) |
| `loopx-research.md` + `loopx-research.psv/coverage-record.json` | The LoopX evidence trail the reconvergence record cites (psv coverage record) |

(The readiness review's own csr/psv record set — `spec-gaming-orthogonal-axis.pub-readiness.csr/` — remains in the canonical knowledge base; not vendored.)

## Canonical source & drift rule

The **canonical source** remains the author's knowledge base:
`~/dev/ws-wiki/fedaot-kb/docs/papers/spec-gaming-orthogonal-axis.md` (its convergence /
verification trails live beside it there).

This snapshot is updated **only by an explicit sync step** — never silently.

```bash
bash docs/papers/sync-paper.sh    # re-copies the artifact set from the canonical KB and reports freshness
```
