#!/usr/bin/env python3
"""metrics.py — deterministic metrics over the solidforge evidence corpus.

Implements docs/retrospective-eval-design.md (csr-converged 2026-09-15, 6 rounds).
Every structural rule here traces to a design decision that survived adversarial
review; where the corpus surprises us, the script FAILS LOUD (assert) rather than
silently dropping or double-counting — the failure modes rounds 1-6 closed.

Outputs (written beside this script):
  index-v2.json          — annotation layer (deliverable 1)
  dedup-arithmetic.json  — per-run unique counts (deliverable 6)
  metrics-output.json    — RQ1/RQ3/RQ4 + RQ2 pre-pass (deliverable 2)

Usage: python3 metrics.py [--corpus <root>]   (default: the parent of analysis/)
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = (
    os.path.abspath(sys.argv[sys.argv.index("--corpus") + 1])
    if "--corpus" in sys.argv
    else os.path.dirname(HERE)
)
RAW_RUNS = os.path.join(CORPUS, "raw", "solidforge-runs")
RAW_CONS = os.path.join(CORPUS, "raw", "consumer-projects")
REPO_DOCS = os.path.abspath(
    os.path.join(CORPUS, "..", "..", "..", "docs")
)  # committed reference layer

# ── DESIGN §Unit rules: aggregate kinds ──────────────────────────────────────
AGG_PATTERNS = ("record.json", "convergence-record", "csr-record", "run-record", "run.json")
NEVER_INPUT_SUBSTR = ("dispositions", "prior-context", "prior-findings")
NEVER_INPUT_EXACT = {"same-leg-full-findings.json"}
STUB_KEYS = {
    "artifact_type",
    "caveats",
    "coverage",
    "inner_ring",
    "outer_ring",
    "process_converged",
    "rightness",
}


def jload(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def walk_jsons(root):
    out = []
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".json"):
                out.append(os.path.join(dp, fn))
    return sorted(out)


# ── DESIGN §RQ1: classifier (precedence-pinned) ──────────────────────────────
def classify_leg(basename):
    """Return 'hetero' | 'same' | None (not a leg input).
    NEVER-INPUTS evaluated FIRST; token forms next; token-less hyphen suffix last.
    Multi-form token match (hetero AND same in one basename) → AssertionError."""
    low = basename.lower()
    if any(s in low for s in NEVER_INPUT_SUBSTR) or basename in NEVER_INPUT_EXACT:
        return None
    has_h, has_s = "hetero" in low, "same" in low
    if has_h and has_s:
        raise AssertionError(f"multi-form token match: {basename}")
    if has_h:
        return "hetero"
    if has_s:
        return "same"
    if re.search(r"(^|[-_])findings\.json$", low) and "-" in low:  # hyphen token-less form only
        return "same"
    return None  # dot-form stem pairs, bare findings.json, aggregates → not leg inputs


def has_round_key(basename):
    return bool(re.match(r"^(r\d+|round\d+)[-_.]", basename, re.I))


# ── DESIGN §Vocabulary normalization ─────────────────────────────────────────
def norm_severity(sev):
    if sev is None:
        return "absent"
    s = str(sev).lower()
    if s in ("coverage_note", "coverage"):
        return "coverage"  # ≡ rule
    if s in ("note",) or "note-class" in s:
        return "advisory"  # note-class advisories
    if s in ("blocker", "warning"):
        return s
    return f"raw:{s}"


DEFECT_SEVS = {"blocker", "warning"}


# ── Unit construction ─────────────────────────────────────────────────────────
class Unit:
    def __init__(self, uid, layer, directory):
        self.uid, self.layer, self.directory = uid, layer, directory
        self.files = []  # all json files in the unit's scope
        self.aggregate = None  # (path, data) authoritative finding source
        self.agg_kind = None
        self.flags = []  # disclosed ingest decisions
        self.findings = []  # normalized finding dicts
        self.leg_files = {"hetero": [], "same": []}


def is_aggregate(basename):
    return any(p in basename.lower() for p in AGG_PATTERNS)


def build_units():
    units = []
    # Layer 1: run-dir layer — one directory = one unit
    for d in sorted(os.listdir(RAW_RUNS)):
        pdir = os.path.join(RAW_RUNS, d)
        if not os.path.isdir(pdir):
            continue
        u = Unit(f"sf:{d}", "solidforge-runs", pdir)
        u.files = walk_jsons(pdir)
        units.append(u)
    # Layer 2: consumer layer — stem pairs / standalone records
    cons_jsons = walk_jsons(RAW_CONS)
    by_stem = defaultdict(lambda: {"findings": None, "record": None, "others": []})
    for p in cons_jsons:
        bn = os.path.basename(p)
        stem = re.sub(r"\.(findings|run-record)\.json$", "", bn)
        if re.search(r"\.findings\.json$", bn):
            by_stem[(os.path.dirname(p), stem)]["findings"] = p
        elif re.search(r"\.run-record\.json$", bn):
            by_stem[(os.path.dirname(p), stem)]["record"] = p
        else:
            by_stem[(os.path.dirname(p), stem)]["others"].append(p)
    for (dirstem, stem), slot in sorted(by_stem.items()):
        uid = f"cons:{os.path.relpath(dirstem, RAW_CONS)}/{stem}"
        u = Unit(uid, "consumer-projects", dirstem)
        if slot["findings"] and slot["record"]:
            u.files = [slot["findings"], slot["record"]] + slot["others"]
        elif slot["findings"] or slot["record"]:
            u.files = [x for x in (slot["findings"], slot["record"]) if x] + slot["others"]
        else:
            u.files = slot["others"]  # standalone aggregate(s) — one-record unit each
        units.append(u)
    return units


# ── Aggregate selection per unit ──────────────────────────────────────────────
def flatten_findings(obj, acc, source):
    """Recursively collect finding-shaped dicts (defect_id + severity/pass)."""
    if isinstance(obj, dict):
        if "defect_id" in obj and ("severity" in obj or "pass" in obj):
            acc.append(
                {
                    "id": str(obj.get("defect_id")),
                    "sev": norm_severity(obj.get("severity", obj.get("pass"))),
                    "kind": obj.get("kind"),
                    "evidence": str(obj.get("evidence", ""))[:400],
                    "source": source,
                }
            )
            return
        for v in obj.values():
            flatten_findings(v, acc, source)
    elif isinstance(obj, list):
        for v in obj:
            flatten_findings(v, acc, source)


def select_aggregate(u):
    aggs = [p for p in u.files if is_aggregate(os.path.basename(p))]
    primary = [p for p in aggs if os.path.basename(p) != "run.json"]
    chosen = None
    if primary:
        # prefer record/convergence/csr-record kinds over generic run-record when coexisting
        ranked = sorted(
            primary,
            key=lambda p: (
                0
                if (
                    "convergence-record" in os.path.basename(p)
                    or os.path.basename(p) == "record.json"
                )
                else 1
            ),
        )
        chosen = ranked[0]
        if len(primary) > 1:
            u.flags.append(f"coexisting-aggregates:{[os.path.basename(p) for p in primary]}")
    elif any(os.path.basename(p) == "run.json" for p in u.files):
        chosen = [p for p in u.files if os.path.basename(p) == "run.json"][0]
        u.flags.append("run.json-sole-aggregate")
    if chosen:
        try:
            data = jload(chosen)
        except Exception as e:
            u.flags.append(f"aggregate-parse-failure:{e.__class__.__name__}")
            return None
        u.aggregate, u.agg_kind = (chosen, data), os.path.basename(chosen)
        flatten_findings(data, u.findings, "aggregate")
        if not u.findings:
            keys = set(data.keys()) if isinstance(data, dict) else set()
            if keys and keys <= STUB_KEYS:
                u.flags.append("run-record-stub")
        return "aggregate"
    # no aggregate: stub fallback (paired dot-form findings) or named substitute (leg files)
    paired = [
        p
        for p in u.files
        if re.search(r"\.findings\.json$", os.path.basename(p))
        or os.path.basename(p) == "findings.json"
    ]
    legs = [p for p in u.files if classify_leg(os.path.basename(p))]
    # reference layer FIRST among the fallbacks (design §reference layer): a committed
    # docs/*.csr-record.json matching this run supersedes substitute ingestion
    ref = find_reference(u)
    if ref is not None:
        name, data = ref
        u.aggregate = (os.path.join(REPO_DOCS, name), data)
        u.agg_kind = name
        flatten_findings(data, u.findings, f"reference:{name}")
        u.flags.append(f"reference-ingest:{name}")
        return "reference"
    if paired and any(is_runrecord_stub_file(p) for p in u.files):
        chosen = paired[0]
        u.flags.append(f"stub-paired-fallback:{os.path.basename(chosen)}")
        data = jload(chosen)
        u.aggregate, u.agg_kind = (chosen, data), os.path.basename(chosen)
        flatten_findings(data, u.findings, "stub-paired")
        return "stub-paired"
    if legs:
        u.flags.append("aggregate-absent-substitute:leg-files")
        for p in legs:
            try:
                data = jload(p)
            except Exception:
                continue
            flatten_findings(data, u.findings, f"leg-substitute:{os.path.basename(p)}")
        return "substitute"
    u.flags.append("no-finding-source")
    return None


def find_reference(u):
    """Committed docs/*.csr-record.json matched to this run by findings-id overlap
    (>=50% of the unit's candidate ids). Returns (name, data) or None."""
    if not os.path.isdir(REPO_DOCS):
        return None
    unit_ids = set()
    for p in u.files:
        bn = os.path.basename(p)
        if classify_leg(bn) or re.search(r"\.findings\.json$", bn) or bn == "findings.json":
            try:
                unit_ids |= ids_in(jload(p))
            except Exception:
                continue
    if not unit_ids:
        return None
    best, best_cov = None, 0.0
    for name in sorted(os.listdir(REPO_DOCS)):
        if not name.endswith(".csr-record.json"):
            continue
        try:
            data = jload(os.path.join(REPO_DOCS, name))
        except Exception:
            continue
        cov = len(unit_ids & ids_in(data)) / len(unit_ids)
        if cov > best_cov:
            best, best_cov = (name, data), cov
    return best if best_cov >= 0.5 else None


def is_runrecord_stub_file(path):
    bn = os.path.basename(path)
    if "run-record" not in bn:
        return False
    try:
        keys = set(jload(path).keys())
    except Exception:
        return False
    return keys <= STUB_KEYS


# ── Leg attribution inputs (RQ1) ──────────────────────────────────────────────
def collect_leg_files(u):
    for p in u.files:
        bn = os.path.basename(p)
        leg = classify_leg(bn)
        if leg and has_round_key(bn):
            u.leg_files[leg].append(p)
        elif leg and not has_round_key(bn):
            u.flags.append(f"leg-file-no-round-key:{bn}")  # round-less leg file — cross-check only


def leg_id_sets(u):
    """defect_id sets per leg from leg files + run.json per-round arrays."""
    out = {"hetero": set(), "same": set()}
    for leg, paths in u.leg_files.items():
        for p in paths:
            try:
                data = jload(p)
            except Exception:
                continue
            out[leg] |= ids_in(data)
    # run.json arrays channel
    for p in u.files:
        if os.path.basename(p) == "run.json":
            try:
                data = jload(p)
            except Exception:
                continue
            for r in data.get("rounds", []) if isinstance(data, dict) else []:
                for f in r.get("hetero_findings") or []:
                    if isinstance(f, dict) and f.get("defect_id"):
                        out["hetero"].add(str(f["defect_id"]))
                for f in r.get("same_findings") or []:
                    if isinstance(f, dict) and f.get("defect_id"):
                        out["same"].add(str(f["defect_id"]))
    return out


def ids_in(obj, acc=None):
    if acc is None:
        acc = set()
    if isinstance(obj, dict):
        if "defect_id" in obj:
            acc.add(str(obj["defect_id"]))
        else:
            for v in obj.values():
                ids_in(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            ids_in(v, acc)
    return acc


# ── Annotation layer (deliverable 1) ──────────────────────────────────────────
def annotate(u):
    prov, model, label = None, None, "unknown"
    sidecar = os.path.join(u.directory, "progress.jsonl")
    if os.path.exists(sidecar):
        with open(sidecar, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        for line in lines:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("provider") and not prov:
                prov = d.get("provider")
            if d.get("model") and model is None:
                model = d.get("model")
        if prov:
            label = "sidecar"
    if not prov:
        for p in u.leg_files.get("hetero", []) + [
            p for p in u.files if "hetero" in os.path.basename(p).lower()
        ]:
            try:
                data = jload(p)
            except Exception:
                continue
            prs = (
                data.get("provider_runs") or data.get("providers")
                if isinstance(data, dict)
                else None
            )
            if prs:
                prov = prov or (
                    prs[0].get("name")
                    if isinstance(prs, list) and isinstance(prs[0], dict)
                    else None
                )
                model = model or (
                    prs[0].get("model")
                    if isinstance(prs, list) and isinstance(prs[0], dict)
                    else None
                )
            if prov:
                label = "leg-file"
                break
    date = None
    if isinstance(u.aggregate and u.aggregate[1], dict):
        for k in ("started_at", "ended_at", "date", "fetched_at"):
            v = u.aggregate[1].get(k)
            if isinstance(v, str):
                date = v[:10]
                break
    era = "unknown"
    if date:
        era = "pre-ADR52" if date < "2026-08-21" else "post-ADR52"
        if label == "unknown":
            label = "record-internal"
    return {"provider": prov, "model": model, "era": era, "date": date, "provenance": label}


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    units = build_units()
    report = {"units": [], "asserts": []}
    index_v2 = {"generated": "2026-09-15", "units": []}
    dedup = []
    for u in units:
        src = select_aggregate(u)
        collect_leg_files(u)
        # classifier assertion: every round-keyed json with a leg token classifies
        for p in u.files:
            bn = os.path.basename(p)
            if has_round_key(bn) and not any(s in bn.lower() for s in NEVER_INPUT_SUBSTR):
                leg = classify_leg(bn)
                if leg is None and re.search(r"(hetero|same)", bn.lower()):
                    report["asserts"].append(f"UNCLASSIFIED leg-shaped file: {u.uid}/{bn}")
        # dedup arithmetic: unique ids vs raw finding count
        raw_n = len(u.findings)
        uniq = len({f["id"] for f in u.findings})
        dedup.append({"unit": u.uid, "raw_findings": raw_n, "unique_ids": uniq, "source": src})
        env = annotate(u)
        # RQ1 attribution
        legs = leg_id_sets(u)
        attrib = Counter()
        for f in u.findings:
            in_h, in_s = f["id"] in legs["hetero"], f["id"] in legs["same"]
            if in_h and in_s:
                attrib["both"] += 1
            elif in_h:
                attrib["hetero-only"] += 1
            elif in_s:
                attrib["same-only"] += 1
            else:
                attrib["unattributable"] += 1
        u_rec = {
            "uid": u.uid,
            "layer": u.layer,
            "source": src,
            "flags": u.flags,
            "findings_raw": raw_n,
            "findings_unique": uniq,
            "env": env,
            "leg_attribution": dict(attrib),
        }
        report["units"].append(u_rec)
        index_v2["units"].append({"uid": u.uid, **env})
    for name, payload in (
        ("index-v2.json", index_v2),
        ("dedup-arithmetic.json", dedup),
        ("metrics-output.json", report),
    ):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
    # console summary
    tot = Counter()
    for r in report["units"]:
        for k, v in r["leg_attribution"].items():
            tot[k] += v
    print(f"units: {len(units)} | asserts: {len(report['asserts'])}")
    for a in report["asserts"][:10]:
        print("  !!", a)
    print("leg attribution (all units):", dict(tot))
    print("flags:", Counter(f for r in report["units"] for f in r["flags"]).most_common(12))


if __name__ == "__main__":
    main()
