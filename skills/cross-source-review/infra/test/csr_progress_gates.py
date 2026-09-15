#!/usr/bin/env python3
"""csr_progress_gates.py — run-progress sidecar gate (BLOCKER; rule 4).

Mirrors the workspace's per-gate self-containment convention (rule 7 — duplicate
the helper, do NOT import a shared lib): offline checks for the ADR #61
run-progress observability contract (sidecar + renderer + wrapper tee). NO real
model call (rule 4) — the wrapper half runs via --dry-run / a faked stream child:

  1. registry-vocabulary-sync — csr_progress.EVENT_REGISTRY keys equal the
     SKILL.md event-vocabulary bullets EXACTLY (both directions; rule 5 drift
     is a Blocker, not advisory — the registry IS an enumeration).
  2. append-valid — `csr_progress.py append` lands one JSONL line with
     ts + type + coerced fields (cap=5 stays an int).
  3. append-invalid — unknown type / missing required field / unknown field /
     non-enum run-end outcome each exit non-zero (loud misuse, rule 3).
  4. status-render — a full two-round fixture renders header / round-of-cap /
     phase+age / leg + reconcile totals / terminal state; a torn last line and
     a RUNNING (no run-end) file never crash.
  5. wrapper-flag-surface — wrapper --dry-run --progress-file appends
     hetero-leg-start + hetero-leg-end JSONL lines while stdout stays the
     single result JSON; NO *.stream.jsonl is created (a dry run never reaches
     _run_streamed — no false promise of an execution log, ADR #69).
  6. wrapper-heartbeat-tee — a faked streamed child's stderr heartbeats ALSO
     land in the progress file (module-global _PROGRESS_PATH seam).
  7. wrapper-best-effort — an unwritable progress path NEVER raises
     (observability failure cannot kill the review, ADR #61).
  8. enumeration-sync — divergence log records --progress-file;
     disconnect_check REQUIRED_FILES + SKILL.md/install.md self-check lists
     carry the two new files (rule 5).
  9. narration-contract — SKILL.md's step-2 different-family bullet launches the
     wrapper as a BACKGROUND task with stderr captured to wrapper.stderr + a
     ~2-minute poll narration loop whose FIRST line per leg hands the human the
     session's OWN run-dir + progress.jsonl and stream.jsonl tail commands,
     keeping the runs/LATEST single-active-run one-liner (ADR #62 zero-
     interaction + the ADR #69 re-scoped pointer); the workspace ADR log
     carries #62 AND #69; the step-2 SAME-FAMILY bullet spawns FOREGROUND
     (contains FOREGROUND, lacks run_in_background, keeps both sidecar
     appends); the sidecar poll clause names the different-family leg.
 10. latest-pointer — csr_progress.py's run-start append atomically keeps
     runs/LATEST (relative symlink) pointed at the newest run dir; other event
     types never touch it (behavioral).
 11. stream-log-distillation — a faked streamed child's assistant blocks land
     as distilled stream-log lines (text / tool + input_head<=300 / one
     spawn-start with a bool schema flag); partials + result events never do;
     an unwritable stream-log path NEVER raises (ADR #69 best-effort).
 12. multi-run-render — `status <runs-dir>` renders one labeled block per
     ACTIVE run (no run-end), collapses ended runs, EXCLUDES the LATEST
     symlink from the scan (no double render) while still RESOLVING it at
     dispatch (symlinked single-run case); zero-active renders the most-recent
     block; dir-vs-file dispatch is identical and the single-run render
     matches the PRE-change frozen golden (age-normalized — the phase age is
     wall-clock-relative; everything else byte-compared, ADR #69).
 13. stream-render — `csr_progress.py stream <run-dir|.stream.jsonl>` renders
     the distilled execution log in HUMAN form (spawn divider, prose text,
     ▸ tool lines; no raw JSON leakage), auto-picks the NEWEST stream log for
     a run dir, and tolerates a torn tail under concurrent writes; snapshot
     shaping --tail N + --newest-first keeps the newest events in the visible
     head for CC-tool-result consumption (follow-incompatible, exit 2)
     (ADR #69 read side).
 14. trace-append — `csr_progress.py trace-append --file --entries` persists
     a same-family leg's self-reported execution_trace as stream-log JSONL:
     strict vocabulary (kind text|tool; unknown field/shape exits non-zero),
     server-side caps by truncation (text<=2000, input_head<=300), ts stamped,
     and the written file round-trips through the SAME stream renderer —
     both legs' execution records share one format + one reader (ADR #69).
     ALSO pins the two SKILL.md call sites: the same-family bullet names
     round<k>-same-family.stream.jsonl, and the web-claim-verifier spawn
     condition names verify-<claim_id>.stream.jsonl (both via trace-append).

Usage:
    python3 infra/test/csr_progress_gates.py
"""

import importlib.util
import io
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile

GATE = "csr-progress-gates"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # skills/cross-source-review
SCRIPTS = os.path.join(ROOT, "infra", "scripts")
CSR_PROGRESS = os.path.join(SCRIPTS, "csr_progress.py")
HETERO = os.path.join(SCRIPTS, "hetero_doc_review.py")
SKILL = os.path.join(ROOT, "SKILL.md")

# Faked streamed child (mirrors hetero_doc_guards' _FAKE_STREAM_OK shape):
# spans >1 heartbeat tick at the patched 0.3s interval, carries a resolvable model.
_FAKE_STREAM_OK = r"""
import json, sys, time
print(json.dumps({"type": "system", "subtype": "init"}), flush=True)
print('{"type":"stream_event","delta":"tok"}', flush=True)
time.sleep(1.2)
msg = {"type": "assistant", "message": {"model": "fake-model-x", "content": []}}
print(json.dumps(msg), flush=True)
"""

# Faked streamed child for check 11 (ADR #69 stream-log distillation): two
# assistant events — one text+tool_use, one text-only — around a partial and a
# result event that must NEVER reach the stream log. The parent passes
# --json-schema as a trailing argv token so the spawn-start marker's schema
# flag is exercised on its True branch.
_FAKE_STREAM_LOG = r"""
import json
print(json.dumps({"type": "system", "subtype": "init"}), flush=True)
print('{"type":"stream_event","delta":"tok"}', flush=True)
blocks = [
    {"type": "text", "text": "Reviewing the artifact."},
    {"type": "tool_use", "name": "Read",
     "input": {"file_path": "SKILL.md", "offset": 1, "limit": 50}},
]
print(json.dumps({"type": "assistant",
                  "message": {"model": "fake-model-x", "content": blocks}}),
      flush=True)
print(json.dumps({"type": "assistant",
                  "message": {"model": "fake-model-x",
                              "content": [{"type": "text",
                                           "text": "Second pass."},
                                          {"type": "text",
                                           "text": "L" * 3000}]}}),
      flush=True)
print(json.dumps({"type": "result", "subtype": "success"}), flush=True)
"""

# The PRE-change frozen golden for check 12's byte regression (captured from
# the pre-ADR-#69 renderer 2026-09-16, blueprint P2 PRE-STEP — never
# regenerated; a post-change regeneration would compare the code to itself).
# _AGE_NORM normalizes the ONLY wall-clock-relative field (the phase-age
# suffix); every other byte is compared.
_AGE_NORM = r"— \d+s ago"
_GOLDEN_EVENTS = [
    {
        "ts": "2026-09-16T00:00:00",
        "type": "run-start",
        "artifact": "docs/golden-probe.md",
        "tier": "short",
        "cap": 2,
    },
    {"ts": "2026-09-16T00:00:01", "type": "same-family-spawn", "round": 1},
    {
        "ts": "2026-09-16T00:01:00",
        "type": "same-family-complete",
        "round": 1,
        "findings": 3,
    },
    {
        "ts": "2026-09-16T00:01:30",
        "type": "hetero-leg-start",
        "round": 1,
        "provider": "deepseek",
    },
    {
        "ts": "2026-09-16T00:02:00",
        "type": "hetero-heartbeat",
        "provider": "deepseek",
        "elapsed_s": 30.0,
        "stream_bytes": 1000,
        "events": 10,
        "assistant_events": 2,
        "model": "deepseek-flash",
        "idle_s": 0.1,
        "killed": None,
    },
    {
        "ts": "2026-09-16T00:02:30",
        "type": "hetero-leg-end",
        "round": 1,
        "provider": "deepseek",
        "outcome": "ok",
        "findings": 2,
        "model": "deepseek-flash",
        "elapsed_s": 60.0,
        "degraded": False,
    },
    {
        "ts": "2026-09-16T00:03:00",
        "type": "reconcile",
        "round": 1,
        "fixed": 4,
        "rejected": 1,
        "escalated": 0,
    },
    {"ts": "2026-09-16T00:03:01", "type": "round-end", "round": 1, "new_blockers": 1},
]
_GOLDEN_RENDER = """csr run: docs/golden-probe.md (tier short, cap 2)
round: 1 of 2
phase: round-end — 2154s ago
same-family: 1 legs, 3 findings
hetero: 1 legs (ok 1, degraded 0, malformed 0)
reconcile: fixed 4, rejected 1, escalated 0
new-blockers: r1=1
state: RUNNING
unparsed: 0
"""


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _finding(detail, suggestion, file_=None):
    return {
        "severity": "blocker",
        "rule": "progress-guards",
        "file": file_ or "infra/scripts/csr_progress.py",
        "line": 0,
        "detail": detail,
        "suggestion": suggestion,
    }


def _check(name, ok, detail, suggestion, findings, coverage, file_=None):
    if ok:
        coverage.append(f"{name}: PASS")
    else:
        findings.append(_finding(f"{name}: {detail}", suggestion, file_=file_))
        coverage.append(f"{name}: FAIL")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _append(prog, tmpdir, etype, fields):
    """Run csr_progress.py append; return CompletedProcess."""
    argv = [sys.executable, prog, "append", "--file", tmpdir, "--type", etype]
    for k, v in fields.items():
        argv += ["--field", f"{k}={v}"]
    return subprocess.run(argv, capture_output=True, text=True)


def _skill_vocabulary(skill_text):
    """The `- `type`` bullets under the Run-progress sidecar section of SKILL.md."""
    sec = re.search(
        r"###\s+Run-progress sidecar.*?(?=\n###\s|\n##\s)", skill_text, re.DOTALL
    )
    if not sec:
        return None
    return set(re.findall(r"^- `([a-z-]+)`", sec.group(0), re.MULTILINE))


def run():
    """Fourteen checks (incl. the RUNNING render variant). Returns (findings, coverage)."""
    coverage = [
        "csr-progress-gates (BLOCKER, rule 4 codifiable): the ADR #61 run-progress "
        "observability contract — registry sync, append shape, status render, "
        "wrapper tee + best-effort, enumeration sync."
    ]
    findings = []
    mod = _load_module(CSR_PROGRESS, "csr_progress")
    skill_text = _read(SKILL)

    # --- check 1: registry <-> SKILL.md vocabulary sync ------------------
    reg_keys = set(mod.EVENT_REGISTRY.keys())
    skill_keys = _skill_vocabulary(skill_text)
    ok1 = skill_keys is not None and reg_keys == skill_keys
    _check(
        "registry-vocabulary-sync",
        ok1,
        f"registry={sorted(reg_keys)} skill={sorted(skill_keys or [])}",
        "the event vocabulary is single-sourced: keep EVENT_REGISTRY keys and the "
        "SKILL.md Run-progress sidecar bullets in lockstep (rule 5)",
        findings,
        coverage,
    )

    with tempfile.TemporaryDirectory() as td:
        prog_file = os.path.join(td, "runs", "demo", "progress.jsonl")

        # --- check 2: append-valid --------------------------------------
        p2 = _append(
            CSR_PROGRESS,
            prog_file,
            "run-start",
            {"artifact": "docs/x.md", "tier": "long", "cap": "5"},
        )
        line = None
        try:
            with open(prog_file, encoding="utf-8") as fh:
                line = json.loads(fh.readline())
        except (OSError, json.JSONDecodeError):
            pass
        ok2 = (
            p2.returncode == 0
            and line is not None
            and line.get("type") == "run-start"
            and isinstance(line.get("ts"), str)
            and line.get("cap") == 5
            and isinstance(line.get("cap"), int)
        )
        p2b = _append(
            CSR_PROGRESS,
            os.path.join(td, "numstr.jsonl"),
            "run-start",
            {"artifact": "123", "tier": "long", "cap": "5"},
        )
        line_b = None
        try:
            with open(os.path.join(td, "numstr.jsonl"), encoding="utf-8") as fh:
                line_b = json.loads(fh.readline())
        except (OSError, json.JSONDecodeError):
            pass
        ok2b = (
            p2b.returncode == 0
            and line_b is not None
            and line_b.get("artifact") == "123"
            and isinstance(line_b.get("artifact"), str)
        )
        _check(
            "append-valid",
            ok2 and ok2b,
            f"rc={p2.returncode} line={line} numstr={line_b}",
            "append must land one JSONL line with ts + type + coerced fields; "
            "spec-driven coercion keeps numeric-LOOKING strings as strings (AC-1)",
            findings,
            coverage,
        )

        # --- check 3: append-invalid (3 sub-cases) ----------------------
        p3a = _append(CSR_PROGRESS, prog_file, "no-such-event", {"round": "1"})
        p3b = _append(CSR_PROGRESS, prog_file, "reconcile", {"round": "1"})
        p3c = _append(
            CSR_PROGRESS, prog_file, "round-end", {"round": "1", "bogus": "x"}
        )
        p3d = _append(CSR_PROGRESS, prog_file, "run-end", {"outcome": "convergedd"})
        ok3 = (
            p3a.returncode != 0
            and p3b.returncode != 0
            and p3c.returncode != 0
            and p3d.returncode != 0
        )
        _check(
            "append-invalid",
            ok3,
            f"unknown={p3a.returncode} missing={p3b.returncode} "
            f"extra-field={p3c.returncode} bad-outcome={p3d.returncode}",
            "unknown type / missing required field / unknown field / non-enum "
            "run-end outcome must each exit non-zero — the registry is a strict "
            "vocabulary (rule 3)",
            findings,
            coverage,
        )

        # --- check 4: status-render (fixture + torn line + RUNNING) -----
        seq = [
            ("run-start", {"artifact": "docs/x.md", "tier": "long", "cap": "5"}),
            ("same-family-spawn", {"round": "1"}),
            ("same-family-complete", {"round": "1", "findings": "3"}),
            ("hetero-leg-start", {"round": "1", "provider": "deepseek"}),
            (
                "hetero-heartbeat",
                {"provider": "deepseek", "elapsed_s": "12.5"},
            ),
            (
                "hetero-leg-end",
                {
                    "round": "1",
                    "provider": "deepseek",
                    "outcome": "ok",
                    "findings": "2",
                },
            ),
            (
                "reconcile",
                {"round": "1", "fixed": "4", "rejected": "1", "escalated": "1"},
            ),
            ("round-end", {"round": "1", "new_blockers": "1"}),
            ("same-family-spawn", {"round": "2"}),
            ("same-family-complete", {"round": "2", "findings": "0"}),
            ("hetero-leg-start", {"round": "2", "provider": "deepseek"}),
            (
                "hetero-leg-end",
                {
                    "round": "2",
                    "provider": "deepseek",
                    "outcome": "ok",
                    "findings": "0",
                },
            ),
            (
                "reconcile",
                {"round": "2", "fixed": "0", "rejected": "0", "escalated": "0"},
            ),
            ("round-end", {"round": "2", "new_blockers": "0"}),
            ("run-end", {"outcome": "converged"}),
        ]
        for etype, fields in seq:
            _append(CSR_PROGRESS, prog_file, etype, fields)
        with open(prog_file, "a", encoding="utf-8") as fh:
            fh.write('{"type":"hetero-heartbe')  # torn tail (concurrent tail -f)
        p4 = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", prog_file],
            capture_output=True,
            text=True,
        )
        out = p4.stdout
        ok4 = (
            p4.returncode == 0
            and "docs/x.md" in out
            and "2 of 5" in out
            and "CONVERGED" in out
            and "unparsed: 1" in out
            and "same-family" in out
            and "reconcile" in out
        )
        _check(
            "status-render",
            ok4,
            f"rc={p4.returncode} out={out[:400]!r}",
            "status must render header / round-of-cap / terminal state from the "
            "fixture and count (not crash on) the torn last line (AC-2)",
            findings,
            coverage,
        )
        # RUNNING variant: strip the run-end + torn lines into a fresh file.
        running_file = os.path.join(td, "running.jsonl")
        with open(prog_file, encoding="utf-8") as fh:
            good_lines = [
                ln
                for ln in fh.read().splitlines()
                if ln.strip()
                and not ln.startswith('{"type":"hetero-heartbe')
                and json.loads(ln).get("type") != "run-end"
            ]
        with open(running_file, "w", encoding="utf-8") as fh:
            fh.write("\n".join(good_lines) + "\n")
        p4b = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", running_file],
            capture_output=True,
            text=True,
        )
        ok4b = p4b.returncode == 0 and "RUNNING" in p4b.stdout
        _check(
            "status-render-running",
            ok4b,
            f"rc={p4b.returncode} out={p4b.stdout[:200]!r}",
            "a file with no run-end renders RUNNING (AC-2)",
            findings,
            coverage,
        )

        # --- check 5: wrapper --progress-file flag surface ---------------
        wrap_prog = os.path.join(td, "wrap.jsonl")
        p5 = subprocess.run(
            [
                sys.executable,
                HETERO,
                "--dry-run",
                "--artifact",
                "SKILL.md",
                "--profile",
                "deepseek",
                "--progress-file",
                wrap_prog,
            ],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        wrap_lines = []
        try:
            with open(wrap_prog, encoding="utf-8") as fh:
                wrap_lines = [json.loads(ln) for ln in fh if ln.strip()]
        except (OSError, json.JSONDecodeError):
            pass
        types = [e.get("type") for e in wrap_lines]
        stdout_json = None
        try:
            stdout_json = json.loads(p5.stdout)
        except json.JSONDecodeError:
            pass
        ok5 = (
            p5.returncode == 0
            and stdout_json is not None
            and "hetero-leg-start" in types
            and "hetero-leg-end" in types
            and any(
                e.get("type") == "hetero-leg-end" and e.get("outcome") == "ok"
                for e in wrap_lines
            )
            # ADR #69 no-false-promise: a dry run sets the stream-log path (the
            # provider loop derives it from --progress-file) but never reaches
            # _run_streamed — NO *.stream.jsonl may exist anywhere in td.
            and not any(f.endswith(".stream.jsonl") for f in os.listdir(td))
        )
        _check(
            "wrapper-flag-surface",
            ok5,
            f"rc={p5.returncode} types={types}",
            "wrapper --progress-file must append hetero-leg-start/-end while "
            "stdout stays the single result JSON (AC-3)",
            findings,
            coverage,
            file_="infra/scripts/hetero_doc_review.py",
        )

        # --- check 6: wrapper heartbeat tee ------------------------------
        hmod = _load_module(HETERO, "hetero_doc_review_tee")
        hmod.HEARTBEAT_INTERVAL_S = 0.3
        beat_file = os.path.join(td, "beats.jsonl")
        hmod._PROGRESS_PATH = beat_file
        err_buf = io.StringIO()
        with contextlib.redirect_stderr(err_buf):
            hmod._run_streamed(
                [sys.executable, "-c", _FAKE_STREAM_OK],
                30,
                10 * 1024 * 1024,
                "fake",
            )
        beats = []
        try:
            with open(beat_file, encoding="utf-8") as fh:
                beats = [
                    json.loads(ln)
                    for ln in fh
                    if ln.strip() and json.loads(ln).get("type") == "hetero-heartbeat"
                ]
        except (OSError, json.JSONDecodeError):
            pass
        ok6 = (
            len(beats) >= 1
            and all(b.get("provider") == "fake" for b in beats)
            and all(isinstance(b.get("elapsed_s"), (int, float)) for b in beats)
            and all(isinstance(b.get("ts"), str) for b in beats)
        )
        _check(
            "wrapper-heartbeat-tee",
            ok6,
            f"beats={len(beats)}",
            "streamed heartbeats must ALSO land in the progress file (the stderr "
            "heartbeat extended to the sidecar, ADR #61; AC-3)",
            findings,
            coverage,
            file_="infra/scripts/hetero_doc_review.py",
        )

        # --- check 7: best-effort (unwritable path never raises) ---------
        blocker_file = os.path.join(td, "afile.txt")
        with open(blocker_file, "w", encoding="utf-8") as fh:
            fh.write("i am a file, not a dir")
        hmod._PROGRESS_PATH = os.path.join(blocker_file, "sub", "p.jsonl")
        raised = False
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                hmod._progress_append(
                    "hetero-leg-end", provider="deepseek", outcome="ok"
                )
                hmod._emit_heartbeat(
                    "deepseek",
                    {
                        "elapsed_s": 1.0,
                        "stream_bytes": 1,
                        "events": 1,
                        "assistant_events": 0,
                        "model": None,
                        "idle_s": 0.0,
                        "killed": None,
                    },
                )
        except Exception:
            raised = True
        _check(
            "wrapper-best-effort",
            not raised,
            "progress write to an unwritable path raised",
            "an observability failure must NEVER kill the review — catch OSError, "
            "warn once on stderr, continue (ADR #61; AC-3)",
            findings,
            coverage,
            file_="infra/scripts/hetero_doc_review.py",
        )

    # --- check 8: enumeration sync (rule 5) -------------------------------
    divergence = _read(os.path.join(SCRIPTS, "hetero_doc_review.divergence.md"))
    disconnect = _read(os.path.join(ROOT, "infra", "test", "disconnect_check.py"))
    install = _read(os.path.join(ROOT, "references", "install.md"))
    ok8 = (
        "--progress-file" in divergence
        and "infra/scripts/csr_progress.py" in disconnect
        and "infra/test/csr_progress_gates.py" in disconnect
        and "csr_progress_gates.py" in skill_text
        and "csr_progress.py" in install
        and "csr_progress.py" in skill_text
    )
    _check(
        "enumeration-sync",
        ok8,
        "divergence/--progress-file, disconnect REQUIRED_FILES x2, SKILL.md "
        "self-check + contract, install.md observability mention — some missing",
        "adding a capability ripples through EVERY enumeration (rule 5): "
        "divergence log, disconnect REQUIRED_FILES, SKILL.md self-check list, "
        "install.md observability section",
        findings,
        coverage,
    )

    # --- check 9: in-session narration contract (ADR #62) ----------------
    # Scoped to the step-2 DIFFERENT-FAMILY BULLET (not the whole file): the
    # narration contract is an instruction AT that decision point — presence
    # elsewhere would not make the protocol fire (placement-true check).
    adr_log = _read(
        os.path.join(
            os.path.dirname(ROOT),
            "parallel-development",
            "references",
            "design-decisions.md",
        )
    )
    bullet = re.search(
        r"- Run the \*\*different-family leg\*\*(.*?)(?=\n   - |\n3\. )",
        skill_text,
        re.DOTALL,
    )
    bullet_text = bullet.group(0) if bullet else ""
    sf_bullet = re.search(
        r"- Run the \*\*same-family leg\*\*(.*?)(?=\n   - |\n3\. )",
        skill_text,
        re.DOTALL,
    )
    sf_text = sf_bullet.group(0) if sf_bullet else ""
    sidecar_sec = re.search(
        r"###\s+Run-progress sidecar.*?(?=\n###\s|\n##\s)", skill_text, re.DOTALL
    )
    sidecar_text = sidecar_sec.group(0) if sidecar_sec else ""
    # ADR #69 canonical pinned set (blueprint AC-1; the SAME set is restated in
    # AC-3/P6 — this is the single enforcing site).
    ok9 = (
        bool(bullet)
        and "run_in_background" in bullet_text
        and "wrapper.stderr" in bullet_text
        and "csr_progress.py status" in bullet_text
        and "runs/LATEST" in bullet_text  # watch-pointer first-narration (2026-09-07)
        and "## 62." in (adr_log or "")
        and "stream.jsonl" in bullet_text
        and "ADR #69" in bullet_text
        and "## 69." in (adr_log or "")
        and bool(sf_bullet)
        and "FOREGROUND" in sf_text
        and "run_in_background" not in sf_text
        and "same-family-spawn" in sf_text
        and "same-family-complete" in sf_text
        and "different-family leg" in sidecar_text
    )
    _check(
        "narration-contract",
        ok9,
        "step-2 bullets / sidecar prose: background launch / wrapper.stderr "
        "capture / status narration / session-own run-dir + stream.jsonl + "
        "ADR #69 pointer / runs/LATEST one-liner / same-family FOREGROUND "
        "(no run_in_background, appends kept) / ADR #62+#69 log cross-refs — "
        "some missing",
        "the zero-interaction reporting contract lives in the step-2 bullets "
        "(ADR #62 for the different-family leg; ADR #69 adds the foreground "
        "same-family spawn, the execution-stream pointer, and the re-scoped "
        "run-dir pointer); static presence only — whether the orchestrator "
        "actually narrates / spawns foreground is outer-ring + live-dogfood "
        "territory",
        findings,
        coverage,
        file_="SKILL.md",
    )

    # --- check 10: runs/LATEST stable pointer (observability affordance) ----
    # The run-start append atomically points <runs-dir>/LATEST at the run dir
    # (relative symlink); non-run-start appends never touch it; failures are
    # best-effort (never abort the append).
    with tempfile.TemporaryDirectory() as td:
        runs_dir = os.path.join(td, "runs")
        run_a = os.path.join(runs_dir, "20260907-aaa-slug")
        run_b = os.path.join(runs_dir, "20260907-bbb-slug")
        os.makedirs(run_a, exist_ok=True)
        os.makedirs(run_b, exist_ok=True)
        pa = _append(
            CSR_PROGRESS,
            os.path.join(run_a, "progress.jsonl"),
            "run-start",
            {"artifact": "x.md", "tier": "short", "cap": "2"},
        )
        latest = os.path.join(runs_dir, "LATEST")
        ok10a = (
            pa.returncode == 0
            and os.path.islink(latest)
            and os.path.realpath(latest) == os.path.realpath(run_a)
        )
        # a same-family-spawn (non-run-start) append must NOT repoint
        _append(
            CSR_PROGRESS,
            os.path.join(run_b, "progress.jsonl"),
            "same-family-spawn",
            {"round": "1"},
        )
        ok10b = os.path.realpath(latest) == os.path.realpath(run_a)
        # a LATER run-start repoints atomically
        _append(
            CSR_PROGRESS,
            os.path.join(run_b, "progress.jsonl"),
            "run-start",
            {"artifact": "y.md", "tier": "short", "cap": "2"},
        )
        ok10c = os.path.realpath(latest) == os.path.realpath(run_b)
        ok10 = ok10a and ok10b and ok10c
        _check(
            "latest-pointer",
            ok10,
            f"runs/LATEST behavior: created-on-run-start={ok10a} "
            f"untouched-by-other-events={ok10b} repointed-by-later-run-start={ok10c}",
            "csr_progress.py append --type run-start keeps runs/LATEST (relative "
            "symlink, atomic replace) pointed at the newest run — the stable "
            "human-facing watch path (SKILL.md sidecar section + step-2 first "
            "narration); best-effort: a failed pointer never aborts the append",
            findings,
            coverage,
            file_="infra/scripts/csr_progress.py",
        )

    # --- check 11: execution stream log distillation (ADR #69) -----------
    with tempfile.TemporaryDirectory() as td:
        slog = os.path.join(td, "round1-fake.stream.jsonl")
        hmod = _load_module(HETERO, "hetero_wrapper_11")
        hmod.HEARTBEAT_INTERVAL_S = 0.3
        hmod._PROGRESS_PATH = os.path.join(td, "progress.jsonl")
        hmod._STREAM_LOG_PATH = slog
        _, rc11, tele11, _ = hmod._run_streamed(
            [sys.executable, "-c", _FAKE_STREAM_LOG, "--json-schema"],
            30,
            10 * 1024 * 1024,
            "fake",
        )
        slines = []
        try:
            with open(slog, encoding="utf-8") as fh:
                slines = [json.loads(ln) for ln in fh if ln.strip()]
        except (OSError, json.JSONDecodeError):
            pass
        kinds11 = [ln.get("kind") for ln in slines]
        tool11 = [ln for ln in slines if ln.get("kind") == "tool"]
        spawn11 = [ln for ln in slines if ln.get("kind") == "spawn-start"]
        ok11 = (
            rc11 == 0
            and kinds11.count("text") == 3
            and len(tool11) == 1
            and tool11[0].get("tool") == "Read"
            and isinstance(tool11[0].get("input_head"), str)
            and len(tool11[0]["input_head"]) <= 300
            and len(spawn11) == 1
            and spawn11[0].get("schema") is True
            and tele11["assistant_events"] == 2
            and tele11["events"] == 5
            and not any("stream_event" in json.dumps(ln) for ln in slines)
            and not any(ln.get("kind") == "result" for ln in slines)
            # text-cap branch (outer-ring A3): the 3000-char block must land
            # truncated to <= 2000.
            and all(
                len(ln.get("text", "")) <= 2000
                for ln in slines
                if ln.get("kind") == "text"
            )
        )
        # schema-false branch (outer-ring A3): a spawn WITHOUT --json-schema
        # in argv self-identifies the structured-output retry shape.
        slog2 = os.path.join(td, "round1-fake-retry.stream.jsonl")
        hmod._STREAM_LOG_PATH = slog2
        hmod._STREAM_LOG_WARNED = False
        hmod._run_streamed(
            [sys.executable, "-c", _FAKE_STREAM_LOG], 30, 10 * 1024 * 1024, "fake"
        )
        spawn2 = []
        try:
            with open(slog2, encoding="utf-8") as fh:
                spawn2 = [
                    json.loads(ln)
                    for ln in fh
                    if ln.strip() and json.loads(ln).get("kind") == "spawn-start"
                ]
        except (OSError, json.JSONDecodeError):
            pass
        ok11 = ok11 and len(spawn2) == 1 and spawn2[0].get("schema") is False
        # best-effort sub-case: an unwritable stream-log path NEVER raises
        # (mirror of check 7's blocker-file trick for the progress path).
        blocker11 = os.path.join(td, "blocker")
        with open(blocker11, "w", encoding="utf-8") as fh:
            fh.write("x")
        hmod._STREAM_LOG_PATH = os.path.join(blocker11, "sub", "s.jsonl")
        hmod._STREAM_LOG_WARNED = False
        try:
            hmod._run_streamed(
                [sys.executable, "-c", _FAKE_STREAM_LOG, "--json-schema"],
                30,
                10 * 1024 * 1024,
                "fake",
            )
            best_effort11 = True
        except Exception:  # noqa: BLE001 — the contract is "never raises"
            best_effort11 = False
        _check(
            "stream-log-distillation",
            ok11 and best_effort11,
            f"stream log lines={kinds11} tele={tele11} best_effort={best_effort11}",
            "the wrapper distills assistant blocks to "
            "<run-dir>/round<k>-<provider>.stream.jsonl (text / tool+input_head "
            "<=300 / one spawn-start with a bool schema flag); partials and the "
            "result event never land; an unwritable path degrades, never raises "
            "(ADR #69)",
            findings,
            coverage,
            file_="infra/scripts/hetero_doc_review.py",
        )

    # --- check 12: multi-run status render (ADR #69) ---------------------
    with tempfile.TemporaryDirectory() as td:
        runs_dir = os.path.join(td, "runs")
        run_a = os.path.join(runs_dir, "20260907-aaa-slug")  # ended
        run_b = os.path.join(runs_dir, "20260907-bbb-slug")  # active
        for d in (run_a, run_b):
            os.makedirs(d, exist_ok=True)
        _append(
            CSR_PROGRESS,
            os.path.join(run_a, "progress.jsonl"),
            "run-start",
            {"artifact": "a.md", "tier": "short", "cap": "2"},
        )
        _append(
            CSR_PROGRESS,
            os.path.join(run_a, "progress.jsonl"),
            "run-end",
            {"outcome": "converged"},
        )
        _append(
            CSR_PROGRESS,
            os.path.join(run_b, "progress.jsonl"),
            "run-start",
            {"artifact": "b.md", "tier": "short", "cap": "2"},
        )
        # run_b's run-start append has ALREADY pointed runs/LATEST at run_b
        # (the real mechanism — cmd_append's run-start hook), so the symlink
        # exists for the scan-exclusion and dispatch-resolution cases below.
        # (a) all-runs view: one ACTIVE block, ended collapsed, no LATEST
        # double-render (the scan excludes symlinks).
        p12 = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", runs_dir],
            capture_output=True,
            text=True,
        )
        ok12a = (
            p12.returncode == 0
            and "20260907-bbb-slug (ACTIVE" in p12.stdout
            and "b.md" in p12.stdout
            and p12.stdout.count("csr run:") == 1
            and "1 ended" in p12.stdout
            and "a.md" not in p12.stdout
        )
        # (b) symlinked single-run dispatch: `status runs/LATEST` resolves the
        # symlink (isdir-follows-symlink) — NOT the scan path — and renders
        # the pointed-at run single-run.
        p12b = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", os.path.join(runs_dir, "LATEST")],
            capture_output=True,
            text=True,
        )
        ok12b = p12b.returncode == 0 and p12b.stdout.startswith("csr run: b.md")
        # (c) dir-vs-file dispatch identity (age-normalized — the phase age is
        # wall-clock-relative; everything else byte-compared).
        p12c = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", run_b],
            capture_output=True,
            text=True,
        )
        p12d = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "status",
                os.path.join(run_b, "progress.jsonl"),
            ],
            capture_output=True,
            text=True,
        )
        norm = lambda s: re.sub(_AGE_NORM, "— Ns ago", s)  # noqa: E731
        ok12c = norm(p12c.stdout) == norm(p12d.stdout)
        # (d) zero-active fallback: end run_b; the view names "no active runs"
        # and renders the most-recent run's full block.
        _append(
            CSR_PROGRESS,
            os.path.join(run_b, "progress.jsonl"),
            "run-end",
            {"outcome": "converged"},
        )
        p12e = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", runs_dir],
            capture_output=True,
            text=True,
        )
        ok12d = (
            "no active runs" in p12e.stdout
            and "most recent" in p12e.stdout
            and p12e.stdout.count("csr run:") == 1
        )
        # (e) PRE-change golden regression (age-normalized): the single-run
        # render is byte-stable against the frozen pre-ADR-#69 capture.
        gold_prog = os.path.join(td, "gold", "progress.jsonl")
        os.makedirs(os.path.dirname(gold_prog), exist_ok=True)
        with open(gold_prog, "w", encoding="utf-8") as fh:
            for evt in _GOLDEN_EVENTS:
                fh.write(json.dumps(evt, ensure_ascii=False) + "\n")
        p12f = subprocess.run(
            [sys.executable, CSR_PROGRESS, "status", os.path.dirname(gold_prog)],
            capture_output=True,
            text=True,
        )
        ok12e = norm(p12f.stdout) == norm(_GOLDEN_RENDER)
        _check(
            "multi-run-render",
            ok12a and ok12b and ok12c and ok12d and ok12e,
            f"active-block={ok12a} symlink-dispatch={ok12b} "
            f"dir-vs-file={ok12c} zero-active={ok12d} golden={ok12e}",
            "csr_progress.py status <runs-dir> renders one labeled block per "
            "active run (scan excludes LATEST; dispatch resolves it); zero "
            "active renders the most recent; single-run output matches the "
            "pre-change frozen golden (ADR #69)",
            findings,
            coverage,
            file_="infra/scripts/csr_progress.py",
        )

    # --- check 13: stream render (ADR #69 read side) ---------------------
    with tempfile.TemporaryDirectory() as td:
        rd = os.path.join(td, "run")
        empty_rd = os.path.join(td, "empty-run")
        os.makedirs(rd)
        os.makedirs(empty_rd)
        slog = os.path.join(rd, "round1-fake.stream.jsonl")
        with open(slog, "w", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "ts": "2026-09-16T01:21:30",
                        "kind": "spawn-start",
                        "schema": True,
                    }
                )
                + "\n"
            )
            fh.write(
                json.dumps(
                    {
                        "ts": "2026-09-16T01:21:36",
                        "kind": "text",
                        "text": "Reviewing the artifact.",
                    }
                )
                + "\n"
            )
            fh.write(
                json.dumps(
                    {
                        "ts": "2026-09-16T01:21:37",
                        "kind": "tool",
                        "tool": "Read",
                        "input_head": '{"file_path": "SKILL.md"}',
                    }
                )
                + "\n"
            )
            fh.write('{"ts": "2026-09-16T01:21:40", "kind": "te')  # torn tail
        # an OLDER stream log in the same dir must lose the auto-pick
        old_log = os.path.join(rd, "round0-fake.stream.jsonl")
        with open(old_log, "w", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "ts": "2026-09-16T00:00:00",
                        "kind": "spawn-start",
                        "schema": True,
                    }
                )
                + "\n"
            )
        os.utime(old_log, (0, 0))
        p13 = subprocess.run(
            [sys.executable, CSR_PROGRESS, "stream", rd],
            capture_output=True,
            text=True,
        )
        p13b = subprocess.run(
            [sys.executable, CSR_PROGRESS, "stream", slog],
            capture_output=True,
            text=True,
        )
        p13c = subprocess.run(
            [sys.executable, CSR_PROGRESS, "stream", empty_rd],
            capture_output=True,
            text=True,
        )
        # snapshot shaping: --tail 2 --newest-first keeps the newest 2 events
        # with the NEWEST on top (CC-tool-result consumption: the preview head
        # carries fresh lines; the fold only ever swallows old ones).
        p13d = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "stream",
                rd,
                "--tail",
                "2",
                "--newest-first",
            ],
            capture_output=True,
            text=True,
        )
        d_lines = [ln for ln in p13d.stdout.splitlines() if ln.strip()]
        # snapshot shaping is follow-incompatible (exit 2, loud misuse)
        p13e = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "stream",
                rd,
                "--tail",
                "2",
                "--watch",
                "5",
            ],
            capture_output=True,
            text=True,
        )
        ok13 = (
            p13.returncode == 0
            and "── spawn 01:21:30 (structured) ──" in p13.stdout
            and "01:21:36  Reviewing the artifact." in p13.stdout
            and "▸ Read" in p13.stdout
            and '"kind"' not in p13.stdout  # no raw JSON leakage
            and "00:00:00" not in p13.stdout  # auto-pick took the NEWEST log
            and p13b.stdout == p13.stdout  # file form == dir auto-pick form
            and p13c.returncode == 0
            and "no *.stream.jsonl" in p13c.stdout
            and p13d.returncode == 0
            and len(d_lines) == 2
            and d_lines[0].startswith("01:21:37")  # newest (tool) on top
            and d_lines[1].startswith("01:21:36")  # older (text) below
            and p13e.returncode == 2  # snapshot + follow = loud misuse
        )
        _check(
            "stream-render",
            ok13,
            f"rc={p13.returncode} out={p13.stdout[:120]!r} empty={p13c.stdout[:60]!r}",
            "csr_progress.py stream renders the distilled execution log in "
            "human form (spawn divider / prose / ▸ tool lines, no raw JSON), "
            "auto-picks the newest *.stream.jsonl for a run dir, and skips a "
            "torn tail without crashing (ADR #69 read side)",
            findings,
            coverage,
            file_="infra/scripts/csr_progress.py",
        )

    # --- check 14: trace-append (ADR #69 same-family read side) -----------
    with tempfile.TemporaryDirectory() as td:
        tfile = os.path.join(td, "round1-same-family.stream.jsonl")
        entries = json.dumps(
            [
                {"kind": "text", "text": "verifying §F6 against MEMORY.md"},
                {
                    "kind": "tool",
                    "tool": "Read",
                    "input_head": '{"file_path": "MEMORY.md"}',
                },
                {"kind": "text", "text": "L" * 3000},
            ]
        )
        p14 = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "trace-append",
                "--file",
                tfile,
                "--entries",
                entries,
            ],
            capture_output=True,
            text=True,
        )
        # renderer round-trip: the written file renders like any stream log
        p14r = subprocess.run(
            [sys.executable, CSR_PROGRESS, "stream", tfile],
            capture_output=True,
            text=True,
        )
        # misuse: unknown kind / unknown field / non-array
        p14b = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "trace-append",
                "--file",
                tfile,
                "--entries",
                json.dumps([{"kind": "thought"}]),
            ],
            capture_output=True,
            text=True,
        )
        p14c = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "trace-append",
                "--file",
                tfile,
                "--entries",
                json.dumps([{"kind": "text", "text": "ok", "why": "x"}]),
            ],
            capture_output=True,
            text=True,
        )
        p14d = subprocess.run(
            [
                sys.executable,
                CSR_PROGRESS,
                "trace-append",
                "--file",
                tfile,
                "--entries",
                "not-json",
            ],
            capture_output=True,
            text=True,
        )
        lines14 = []
        try:
            with open(tfile, encoding="utf-8") as fh:
                lines14 = [json.loads(ln) for ln in fh if ln.strip()]
        except (OSError, json.JSONDecodeError):
            pass
        ok14 = (
            p14.returncode == 0
            and len(lines14) == 3
            and all("ts" in ln for ln in lines14)
            and lines14[0]["kind"] == "text"
            and "§F6" in lines14[0]["text"]
            and lines14[1]["tool"] == "Read"
            and len(lines14[1]["input_head"]) <= 300
            and len(lines14[2]["text"]) <= 2000  # 3000-char line truncated
            and p14r.returncode == 0
            and "▸ Read" in p14r.stdout  # same renderer consumes it
            and p14b.returncode == 2
            and p14c.returncode == 2
            and p14d.returncode == 2
            # both SKILL.md call sites instruct trace-append persistence
            and "round<k>-same-family.stream.jsonl" in skill_text
            and "trace-append" in skill_text
            and "verify-<claim_id>.stream.jsonl" in skill_text
        )
        _check(
            "trace-append",
            ok14,
            f"rc={p14.returncode} lines={len(lines14)} "
            f"misuse={[p14b.returncode, p14c.returncode, p14d.returncode]}",
            "csr_progress.py trace-append persists the same-family "
            "execution_trace as stream-log JSONL (strict vocabulary, "
            "server-side caps by truncation, ts stamped) that the SAME stream "
            "renderer consumes (ADR #69)",
            findings,
            coverage,
            file_="infra/scripts/csr_progress.py",
        )

    return findings, coverage


def emit(findings, coverage):
    """Codifiable contract: blocker on violation -> exit non-zero (rule 4)."""
    passed = not any(f.get("severity") == "blocker" for f in findings)
    print(
        json.dumps(
            {
                "gate": GATE,
                "passed": passed,
                "coverage": coverage,
                "findings": findings,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    sys.exit(0 if passed else 1)


def main():
    findings, coverage = run()
    emit(findings, coverage)


if __name__ == "__main__":
    main()
