#!/usr/bin/env python3
"""hetero_doc_guards.py — different-family substrate guard gate (BLOCKER; rule 4).

Mirrors the workspace's per-gate self-containment convention (rule 7 — duplicate
the helper, do NOT import a shared lib): offline checks for the ADR #52
bounded-turns + streamed-observability extension on hetero_doc_review.py. NO
real model call (rule 4) — the "claude" child is faked by sys.executable -c
scripts:

  1. argv guards — _claude_argv carries --max-turns; the DEFAULT spawn is
     stream-json + --verbose + --include-partial-messages; --observe-hooks adds
     --include-hook-events; stream=False restores the legacy json output.
  2. streamed telemetry — a faked JSONL stream yields the resolved model (first
     assistant event's message.model), the turn count (partial deltas excluded),
     the byte count, and a stderr heartbeat while it runs.
  3. byte-cap breaker — a runaway faked stream trips hetero-stream-bytes-cap
     (malformation, NOT a degrade) well before the wall-clock cap.
  4. wall-clock kill — a hung faked child trips hetero-subprocess-timeout at
     the cap with telemetry attached.
  5. CLI conflict — --no-stream + --observe-hooks fails fast (exit 2).
  6. result telemetry — the result envelope carries provider_runs[] (the
     post-hoc "which model actually ran" record).

Usage:
    python3 infra/test/hetero_doc_guards.py
"""

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys

GATE = "hetero-doc-guards"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # skills/cross-source-review
HETERO = os.path.join(ROOT, "infra", "scripts", "hetero_doc_review.py")

# Faked claude children (argv[0] is sys.executable; the code rides `-c`).
_FAKE_STREAM_OK = r"""
import json, sys, time
print(json.dumps({"type": "system", "subtype": "init"}), flush=True)
print('{"type":"stream_event","delta":"tok"}', flush=True)
print('{"type":"stream_event","delta":"tok"}', flush=True)
time.sleep(1.2)  # span >1 heartbeat tick at the patched 0.3s interval
msg = {"type": "assistant", "message": {"model": "fake-model-x", "content": []}}
print(json.dumps(msg), flush=True)
print(json.dumps(msg), flush=True)
"""

_FAKE_STREAM_RUNAWAY = r"""
import time
blob = '{"type":"stream_event","delta":"' + ("x" * 2000) + '"}'
while True:
    print(blob, flush=True)
    time.sleep(0.05)
"""

_FAKE_HUNG = r"""
import time
time.sleep(60)
"""


def _load_module():
    spec = importlib.util.spec_from_file_location("hetero_doc_review", HETERO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _finding(detail, suggestion):
    return {
        "severity": "blocker",
        "rule": "substrate-guards",
        "file": "infra/scripts/hetero_doc_review.py",
        "line": 0,
        "detail": detail,
        "suggestion": suggestion,
    }


def _check(name, ok, detail, suggestion, findings, coverage):
    if ok:
        coverage.append(f"{name}: PASS")
    else:
        findings.append(_finding(f"{name}: {detail}", suggestion))
        coverage.append(f"{name}: FAIL")


def _flag_value(argv, flag):
    return argv[argv.index(flag) + 1] if flag in argv else None


def run():
    """Six checks. Returns (findings, coverage)."""
    coverage = [
        "hetero-doc-guards (BLOCKER, rule 4 codifiable): the ADR #52 substrate "
        "guards — argv surface, streamed telemetry + heartbeat, byte-cap "
        "breaker, wall-clock kill, CLI conflict, provider_runs telemetry."
    ]
    findings = []
    mod = _load_module()

    # --- check 1: argv guards -------------------------------------------
    argv_stream = mod._claude_argv(
        "p.json",
        "opus",
        "{}",
        "prompt",
        12.0,
        "Read Grep",
        False,
        max_turns=7,
        stream=True,
    )
    argv_hooks = mod._claude_argv(
        "p.json",
        "opus",
        "{}",
        "prompt",
        12.0,
        "Read Grep",
        True,
        max_turns=7,
        stream=True,
    )
    argv_json = mod._claude_argv(
        "p.json",
        "opus",
        "{}",
        "prompt",
        12.0,
        "Read Grep",
        False,
        max_turns=7,
        stream=False,
    )
    ok1 = (
        _flag_value(argv_stream, "--max-turns") == "7"
        and _flag_value(argv_stream, "--output-format") == "stream-json"
        and "--verbose" in argv_stream
        and "--include-partial-messages" in argv_stream
        and "--include-hook-events" not in argv_stream
        and "--include-hook-events" in argv_hooks
        and "--verbose" in argv_hooks
        and _flag_value(argv_json, "--output-format") == "json"
        and "--verbose" not in argv_json
        and "--include-partial-messages" not in argv_json
    )
    _check(
        "argv-guards",
        ok1,
        "stream argv missing --max-turns/--verbose/--include-partial-messages, "
        "hook-events routing wrong, or json fallback carries stream flags",
        "restore the ADR #52 flag surface in _claude_argv (manifest: CC v2.1.238)",
        findings,
        coverage,
    )

    # --- check 2: streamed telemetry + heartbeat ------------------------
    mod.HEARTBEAT_INTERVAL_S = 0.3
    err_buf = io.StringIO()
    with contextlib.redirect_stderr(err_buf):
        raw, rc2, tele, _tail = mod._run_streamed(
            [sys.executable, "-c", _FAKE_STREAM_OK],
            30,
            10 * 1024 * 1024,
            "fake",
        )
    beats = [ln for ln in err_buf.getvalue().splitlines() if "hetero-heartbeat" in ln]
    ok2 = (
        rc2 == 0
        and tele["model"] == "fake-model-x"
        and tele["assistant_events"] == 2
        and tele["events"] == 5
        and tele["stream_bytes"] > 0
        and tele["killed"] is None
        and len(beats) >= 2
        and '"model": "fake-model-x"' in err_buf.getvalue()
    )
    _check(
        "streamed-telemetry",
        ok2,
        f"tele={tele} beats={len(beats)} rc={rc2}",
        "the stream reader must capture resolved model / assistant events / bytes "
        "and emit "
        "stderr heartbeats (ADR #52)",
        findings,
        coverage,
    )

    # --- check 3: byte-cap breaker ---------------------------------------
    rc3 = mod._run_claude_once(
        [sys.executable, "-c", _FAKE_STREAM_RUNAWAY],
        25,
        False,
        None,
        guards={"provider": "fake", "max_stream_bytes": 4000},
    )
    ok3 = (
        rc3["ok"] is False
        and rc3["fingerprint"] == "hetero-stream-bytes-cap"
        and rc3["error_subtype"] is None
        and rc3["stream_bytes"] > 4000
        and rc3["elapsed_s"] is not None
        and rc3["elapsed_s"] < 20
    )
    _check(
        "bytes-cap-breaker",
        ok3,
        f"rc3={rc3.get('fingerprint')} bytes={rc3.get('stream_bytes')}",
        "a runaway stream must die at --max-stream-bytes with the "
        "hetero-stream-bytes-cap malformation, NOT burn the wall-clock cap",
        findings,
        coverage,
    )

    # --- check 4: wall-clock kill ----------------------------------------
    rc4 = mod._run_claude_once(
        [sys.executable, "-c", _FAKE_HUNG],
        1,
        False,
        None,
        guards={"provider": "fake", "max_stream_bytes": 10 * 1024 * 1024},
    )
    ok4 = (
        rc4["ok"] is False
        and rc4["fingerprint"] == "hetero-subprocess-timeout"
        and rc4.get("elapsed_s") is not None
        and rc4["elapsed_s"] < 10
    )
    _check(
        "wall-clock-kill",
        ok4,
        f"rc4={rc4.get('fingerprint')} elapsed={rc4.get('elapsed_s')}",
        "a hung child must die at the wall-clock cap with telemetry attached",
        findings,
        coverage,
    )

    # --- check 5: CLI conflict -------------------------------------------
    p5 = subprocess.run(
        [
            sys.executable,
            HETERO,
            "--dry-run",
            "--artifact",
            "SKILL.md",
            "--profile",
            "deepseek",
            "--no-stream",
            "--observe-hooks",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    _check(
        "cli-conflict",
        p5.returncode == 2,
        f"--no-stream + --observe-hooks exited {p5.returncode} (expected 2)",
        "the json fallback cannot serve hook events — fail fast (rule 3)",
        findings,
        coverage,
    )

    # --- check 6: provider_runs telemetry --------------------------------
    p6 = subprocess.run(
        [
            sys.executable,
            HETERO,
            "--dry-run",
            "--artifact",
            "SKILL.md",
            "--profile",
            "deepseek",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    runs = None
    try:
        runs = json.loads(p6.stdout).get("provider_runs")
    except json.JSONDecodeError:
        pass
    ok6 = (
        p6.returncode == 0
        and isinstance(runs, list)
        and len(runs) == 1
        and runs[0].get("name") == "deepseek"
        and {"name", "model", "assistant_events", "stream_bytes", "elapsed_s"}
        <= set(runs[0])
    )
    _check(
        "provider-runs-telemetry",
        ok6,
        f"runs={runs}",
        "the result envelope must carry provider_runs[] (ADR #52 post-hoc "
        "observability: resolved model / assistant events / bytes / elapsed)",
        findings,
        coverage,
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
