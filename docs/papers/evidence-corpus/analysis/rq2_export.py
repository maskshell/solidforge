#!/usr/bin/env python3
"""rq2_export.py — the committed exporter for the RQ2 coding-pass pools.

Implements the pool construction the protocol header describes:
  1. POOL: multi-round units (>=2 rounds) × defect-severity findings,
     exclusions per docs/retrospective-eval-design.md §Vocabulary normalization.
  2. PRE-FILTER: regex over evidence+disposition —
     fix|reword|introduc|residu|stale|own |same round|earlier|prior round
     (case-insensitive) — pool → candidates.

Outputs: rq2-coding-input.json (the pool) and rq2-candidates.json (the
candidates), both beside this script. Round-trip assertion: re-running
this script over the unchanged corpus reproduces both artifacts'
(unit, id) key sequences; content fields are not compared.

Usage: python3 rq2_export.py [--check]   (--check: verify against the
existing artifacts and exit non-zero on drift, writing nothing)
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import (  # noqa: E402
    DEFECT_SEVS,
    build_units,
    collect_leg_files,
    leg_id_sets,
    select_aggregate,
)

HERE = os.path.dirname(os.path.abspath(__file__))
PREFILTER = re.compile(
    r"fix|reword|introduc|residu|stale|own |same round|earlier|prior round", re.I
)


def walk_disp(obj, acc):
    if isinstance(obj, dict):
        if "defect_id" in obj and "note" in obj:
            acc.append((str(obj["defect_id"]), str(obj["note"])))
        else:
            for v in obj.values():
                walk_disp(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            walk_disp(v, acc)


def build_pools():
    pool, cands = [], []
    for u in build_units():
        select_aggregate(u)
        collect_leg_files(u)
        data = u.aggregate[1] if u.aggregate else None
        if not (
            isinstance(data, dict)
            and isinstance(data.get("rounds"), list)
            and len(data["rounds"]) >= 2
        ):
            continue
        legs = leg_id_sets(u)
        disps = []
        walk_disp(data, disps)
        disp_map = dict(disps)
        for f in u.findings:
            if f["sev"] not in DEFECT_SEVS:
                continue
            ev, dp = f["evidence"], disp_map.get(f["id"], "")
            if PREFILTER.search(ev) or PREFILTER.search(dp):
                cands.append(
                    {
                        "unit": u.uid,
                        "id": f["id"],
                        "sev": f["sev"],
                        "kind": f.get("kind"),
                        "evidence": ev[:280],
                        "disposition": dp[:280],
                    }
                )
        for f in u.findings:
            if f["sev"] not in DEFECT_SEVS:
                continue
            leg = (
                "both"
                if f["id"] in legs["hetero"] and f["id"] in legs["same"]
                else "hetero"
                if f["id"] in legs["hetero"]
                else "same"
                if f["id"] in legs["same"]
                else None
            )
            pool.append(
                {
                    "unit": u.uid,
                    "id": f["id"],
                    "sev": f["sev"],
                    "kind": f.get("kind"),
                    "leg": leg,
                    "evidence": f["evidence"],
                }
            )
    return pool, cands


def main():
    check = "--check" in sys.argv
    pool, cands = build_pools()
    pct = len(cands) * 100 // len(pool)
    print(f"pool: {len(pool)} | candidates: {len(cands)} | yield: {pct}%")
    if check:
        for name, fresh in (("rq2-coding-input.json", pool), ("rq2-candidates.json", cands)):
            path = os.path.join(HERE, name)
            with open(path, encoding="utf-8") as fh:
                old = json.load(fh)
            key = "findings" if isinstance(old, dict) and "findings" in old else None
            old_items = old[key] if key else old
            fresh_keys = [(x["unit"], x["id"]) for x in fresh]
            old_keys = [(x["unit"], x["id"]) for x in old_items]
            status = "OK" if fresh_keys == old_keys else "DRIFT"
            print(f"  {name}: {len(old_items)} on disk vs {len(fresh)} fresh -> {status}")
            if status == "DRIFT":
                sys.exit(1)
        return
    with open(os.path.join(HERE, "rq2-coding-input.json"), "w", encoding="utf-8") as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "rq2-candidates.json"), "w", encoding="utf-8") as fh:
        json.dump(cands, fh, ensure_ascii=False, indent=1)
    print("artifacts written")


if __name__ == "__main__":
    main()
