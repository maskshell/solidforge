#!/usr/bin/env python3
"""analyze.py — RQ1(stratified)/RQ3/RQ4 + RQ2 pre-pass over the corpus.

Reuses metrics.py's unit building (single source for the design rules).
Writes analysis-output.json beside this script. Deterministic throughout;
the both-pair and RQ2 outputs are PRE-ADJUDICATION candidates for the
LLM coding pass + human spot-check (design deliverables 3).
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import (  # noqa: E402
    DEFECT_SEVS,
    HERE,
    build_units,
    collect_leg_files,
    leg_id_sets,
    select_aggregate,
)

FIX_INTRO_MARKERS = (
    "fix-introduced",
    "entered with the",
    "introduced by the",
    "the fix text",
    "required the",
    "fix itself",
    "same round",
    "own fix",
    "residue",
)


def round_of(path_basename):
    m = re.match(r"^(?:r|round)(\d+)", path_basename, re.I)
    return int(m.group(1)) if m else None


def analyze():
    units = build_units()
    rq1 = Counter()
    rq1_defect = Counter()
    rq2_pre = []
    rq3 = []  # per unit: {class: [rounds with new instances]}
    rq4 = {"multi_round": [], "stub_process_converged": Counter(), "flags": Counter()}
    degraded_rounds = []

    for u in units:
        src = select_aggregate(u)
        collect_leg_files(u)
        legs = leg_id_sets(u)
        for f in u.findings:
            in_h = f["id"] in legs["hetero"]
            in_s = f["id"] in legs["same"]
            bucket = (
                "both"
                if in_h and in_s
                else "hetero-only"
                if in_h
                else "same-only"
                if in_s
                else "unattributable"
            )
            rq1[bucket] += 1
            if f["sev"] in DEFECT_SEVS:
                rq1_defect[bucket] += 1
            if f["sev"] in DEFECT_SEVS and any(
                m in (f.get("evidence") or "").lower() for m in FIX_INTRO_MARKERS
            ):
                rq2_pre.append(
                    {
                        "unit": u.uid,
                        "id": f["id"],
                        "sev": f["sev"],
                        "evidence": f["evidence"][:200],
                        "leg": bucket if bucket != "unattributable" else None,
                    }
                )

        # RQ3/RQ4 need the aggregate's rounds
        data = u.aggregate[1] if u.aggregate else None
        if isinstance(data, dict) and isinstance(data.get("rounds"), list):
            rounds = data["rounds"]
            per_class = defaultdict(list)
            blockers_per_round = []
            for i, r in enumerate(rounds, 1):
                ids_here = set()
                flatten_ids_round(r, ids_here)
                blockers_per_round.append(r.get("blockers", 0))
                if r.get("hetero_degraded"):
                    degraded_rounds.append({"unit": u.uid, "round": i})
                for f in u.findings:
                    if f["id"] in ids_here and f.get("kind"):
                        per_class[f["kind"]].append(i)
            rq4["multi_round"].append(
                {
                    "unit": u.uid,
                    "rounds": len(rounds),
                    "blockers": blockers_per_round,
                    "substantive_converged": data.get("substantive_converged"),
                    "stalemate": data.get("stalemate"),
                }
            )
            rq3.append(
                {
                    "unit": u.uid,
                    "classes": {
                        k: {"rounds": v, "spanned": (max(v) - min(v) + 1) if v else 0}
                        for k, v in per_class.items()
                    },
                }
            )
        elif isinstance(data, dict) and "process_converged" in data:
            rq4["stub_process_converged"][str(data.get("process_converged"))] += 1
        rq4["flags"][src or "none"] += 1

    out = {
        "rq1_all": dict(rq1),
        "rq1_defect_severity_only": dict(rq1_defect),
        "rq2_prepass_candidates": rq2_pre,
        "rq3_drip": rq3,
        "rq4_economics": rq4,
        "degraded_rounds": degraded_rounds,
    }
    with open(os.path.join(HERE, "analysis-output.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    # console digest
    print("RQ1 defect-only:", dict(rq1_defect))
    print("RQ2 pre-pass candidates:", len(rq2_pre))
    mr = rq4["multi_round"]
    conv = sum(1 for r in mr if r["substantive_converged"] is True)
    stal = sum(1 for r in mr if r["stalemate"] is True)
    print(f"RQ4 multi-round units: {len(mr)} | converged {conv} | stalemate {stal}")
    print("stub process_converged:", dict(rq4["stub_process_converged"]))
    spans = [c["spanned"] for r in rq3 for c in r["classes"].values() if len(c["rounds"]) >= 1]
    if spans:
        multi = sum(1 for s in spans if s > 1)
        print(
            f"RQ3 classes: {len(spans)} | spanned>1 round: {multi} ({multi * 100 // len(spans)}%)"
        )
    print("degraded rounds:", len(degraded_rounds))


def flatten_ids_round(obj, acc):
    if isinstance(obj, dict):
        if "defect_id" in obj:
            acc.add(str(obj["defect_id"]))
        else:
            for v in obj.values():
                flatten_ids_round(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            flatten_ids_round(v, acc)


if __name__ == "__main__":
    analyze()
