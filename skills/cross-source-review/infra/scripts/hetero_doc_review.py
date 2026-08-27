#!/usr/bin/env python3
"""hetero_doc_review.py — doc-domain different-family (different-family) adversarial review.

Spawns a non-interactive Claude Code subprocess on a DIFFERENT model family (e.g.
DeepSeek) as an additive adversarial second opinion on a DOC-SHAPED artifact. The
same-family reviewer (the CSR-I2 `doc-reviewer` agent) stays PRIMARY; different-family is the
cross-family leg that hunts what same-family review misses. The orchestrator
(interactive CC) stays on its primary provider unchanged.

This is a DOC-DOMAIN copy-pattern of `parallel-development`'s
`infra/scripts/hetero_review.py` (workspace rule 7 — copy-patterns-not-code; NOT an
import). The substrate (provider-template + token-injection, the FLAG-SURFACE
MANIFEST, fence-aware JSON parse, CC substrate-error DEGRADE handling, multi-provider
merge) is copied near-verbatim from the proven pd source. The divergences are
doc-domain adaptations only — see `hetero_doc_review.divergence.md` for the full list
and the Phase-A function-signature contract (proposal §5 / F3).

Authority chain: `docs/proposal.md` §3 (different-family substrate), §5 (Phase-A interface-compat
constraint), §8 (bootstrap already used this raw-substrate pattern), §9 Q2 (doc-findings
kind enum) / Q3 (convergence-record, no loop_state dependency); `docs/iteration-plan.md`
§CSR-I3 (deliverable + Done-when + Phase-A compat constraint).

Proposal Q3 is load-bearing here: the doc domain does NOT drive pd's `loop_state`
state machine. This wrapper runs ONE different-family review and PRINTS a clean result dict
`{verdict, degraded, degraded_providers, findings_count, findings, coverage,
malformation, providers, provider_runs}` (provider_runs = per-run substrate telemetry —
resolved model / assistant events / stream bytes / elapsed, ADR #52). The CSR-I4 convergence driver
(built separately) calls this wrapper once per round and assembles the convergence-record
itself.

==============================================================================
FLAG-SURFACE MANIFEST — verified against Claude Code v2.1.201 (2026-07); re-probed
against v2.1.207 (2026-07) after a substrate regression; re-probed against
v2.1.238 (2026-08) after three drifts (see NOTEs below).
If a CC upgrade breaks the wrapper, update this manifest + the flag list in
`_claude_argv()`. `--bare` (minimal mode: skip hooks/LSP/plugin) is the documented
FALLBACK if a CC upgrade breaks the hook/LSP surface — it is NOT the default (the
default keeps hooks so --observe-hooks can see the deterministic gates). `--no-stream`
(single end-of-run json envelope, no incremental telemetry) is the analogous FALLBACK
for the OUTPUT surface (ADR #52).
NOTE (v2.1.207 regression): CC's `--json-schema` validator now bundles ONLY Draft-07
in its draft registry; it rejects schemas declaring Draft 2019-09 / 2020-12 (the
`$schema` marker is treated as an unresolvable ref). The wrapper strips `$schema`
via `_strip_schema_marker_for_cc` before the `--json-schema` arg — the committed schema
stays Draft 2020-12 (the Python `jsonschema` consumer in converge.py uses an explicit
validator class, unaffected). Backward-compat: `$schema` is optional, so a validator
that accepted it (v2.1.201) accepts its absence (v2.1.207). Probe matrix in
`_strip_schema_marker_for_cc`'s docstring.
NOTE (v2.1.238 re-probe, 2026-08-21 — three drifts, ADR #52):
  1. `-p --output-format stream-json` now REQUIRES `--verbose` (a fast rc=1
     `Error: ... requires --verbose` without it) — the pre-2.1.238 stream argv
     (no --verbose) broke. Fixed: the stream mode always passes --verbose.
  2. Alias remap VERIFIED end-to-end through this wrapper's own materialization
     path: `--model opus` + profile `ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-v4-pro[1m]`
     → the API request carries model `deepseek-v4-pro` (the `[1m]` suffix is
     stripped client-side; measured from a stream-json assistant event's
     message.model). Model-name routing is NOT a failure locus. (pro was
     later demoted to flash as the review-leg default — ADR #53; the probe
     fact above stands as measured.)
  3. CC prices UNRECOGNIZED models (any non-Anthropic backend) at premium
     fallback rates — measured $0.24 for ONE tiny turn (num_turns=1). Budget-cap
     semantics amended: coarse breaker only, default 12.0 (ADR #42 amendment).
Flags used:
  claude -p
    --settings <temp-materialized.json>  per-process provider config — the wrapper
                                         materializes this from profiles/<name>.json +
                                         the runtime token (NOT a committed path)
    --model <alias>                    tier/model alias resolved via the profile env
    --output-format stream-json        DEFAULT (ADR #52) — incremental read: stderr
                                       heartbeat + stream-byte cap + the LIVE resolved
                                       model name (the 0-byte blind spot fix)
    --verbose                          required by -p + stream-json (CC v2.1.238)
    --include-partial-messages         token-delta events — liveness BEFORE a message
                                       completes (feeds the byte cap + heartbeat)
    [--include-hook-events]            gate observability (selected by --observe-hooks)
    [--output-format json]             the --no-stream FALLBACK — single end-of-run
                                       envelope, no incremental telemetry (ADR #52)
    --json-schema <schema-json>        the findings shape (doc-findings.schema.json)
    --permission-mode bypassPermissions
    --no-session-persistence           stateless per invocation (ADR #40 (h))
    --max-budget-usd <cap>             coarse runaway breaker (ADR #42 amendment)
    --max-turns <cap>                  hard agentic-turn cap — print mode has NO
                                       default turn limit (ADR #52); the hit
                                       DEGRADES (error_max_turns, ADR #41)
    [--allowedTools "Read Grep Glob Bash"]
    -p "<adversarial prompt>"
`--settings` receives a THROWAWAY temp file the wrapper builds (the committed
profiles/<name>.json is a TEMPLATE; CC does NOT expand ${VAR} in --settings env,
so the wrapper expands the token itself — verified CC v2.1.201). `--json-schema`
takes the schema JSON inline (read from file + passed as one arg).
`--include-hook-events` rides the DEFAULT stream-json mode (--observe-hooks adds
it; the final structured result + hook events are parsed from the stream).
==============================================================================

PROVIDER-TEMPLATE + TOKEN-INJECTION PATTERN:
  profiles/<provider>.json — committed TEMPLATES with ROUTING ONLY (BASE_URL +
                               model aliases). NO `ANTHROPIC_AUTH_TOKEN` field, NO
                               `${...}` token ceremony — drop in a template + set one
                               env var, that's it.
  token-var convention — `<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN` (deepseek ->
                               `DEEPSEEK_ANTHROPIC_AUTH_TOKEN`, qwen-token-plan-cn ->
                               `QWEN_TOKEN_PLAN_CN_ANTHROPIC_AUTH_TOKEN`). Override with the
                               template's optional `_token_env` for a non-convention name.
  --profile <name[,name2...]> or $HETERO_DOC_PROFILE — select provider(s); comma-list
                               = dual-/multi-different-family (each backend runs independently,
                               findings merged + tagged with `provider`).
  token source — shell env (`export DEEPSEEK_ANTHROPIC_AUTH_TOKEN=...`) or
                 <project>/.env (shell wins). The wrapper reads it, INJECTS it as
                 `ANTHROPIC_AUTH_TOKEN` into a chmod-600 temp settings file, passes
                 the file to claude, unlinks it. Other `${VAR}` refs (non-token
                 fields) in the template still expand.
  namespace isolation — the `_ANTHROPIC_AUTH_TOKEN` suffix is the SOLE token
                 source; the provider's native `<FILENAME>_API_KEY` is NEVER read
                 (it may serve another tool/SDK in the same env, so reading it
                 would risk a credential meant for a different use). See the
                 namespace-isolation ADR.

Findings schema (CSR-I1 / proposal Q2): `infra/schemas/doc-findings.schema.json`.
Its finding shape carries `defect_id` / `severity` / `kind` / `location` /
`evidence` / `suggestion`, where `kind` is the doc-domain enum
(`contradiction` / `authority-chain-break` / `scope-creep` / `structural-gap` /
`citation-error` / `coverage-gap`) and `severity` keeps bc's {blocker, warning,
coverage} — the `coverage` severity is the reviewer's honest disclosure "could not
verify X" (workspace rule 3), DISTINCT from the `coverage-gap` KIND (a defect in the
artifact). A different-family "could not verify X" disclosure maps to severity=coverage with the
evidence naming the unchecked area (rule 3/4 — never silent).

Substrate-error handling (ADR #41 — preserved EXACTLY from pd): a non-zero CC exit is
NOT automatically a malformation. CC puts recoverable substrate errors (budget cap,
turn cap, provider overwhelm) in STDOUT as a clean
`{"is_error":true,"subtype":...,"errors":[...]}` envelope (stderr stays empty).
`run_claude` parses it; subtypes in `DEGRADABLE_CC_SUBTYPES` DEGRADE — the different-family leg
contributes 0 findings + a coverage note + a `hetero-degraded-<subtype>` note, and the
verdict stays pass/rewrite from the OTHER providers (different-family is additive — ADR #40).
Non-degradable subtypes (invalid-args, auth) and unparseable output still malform →
rewrite (never mask a regression — rule 3). The default `--budget-usd 4.0` leaves
headroom.

USD caveat (ADR #42, amended 2026-08-21): for non-Anthropic backends
`--max-budget-usd` is a COARSE runaway breaker, NOT real cost — the
Anthropic-compatible API returns tokens only (no price), and CC v2.1.238 prices
UNRECOGNIZED models at premium fallback rates (measured: $0.24 for ONE tiny turn),
so the cap fires on CC's mismeasure long before real provider spend matters (real
accounting is the provider's own dashboard). Provider-independent bounds, in firing
order: `--max-turns` per subprocess (ADR #52 — the OLD citation of "CC's turn limit
(`error_max_turns`)" was a PHANTOM boundary: print mode has no default turn limit and
the wrapper never passed the flag) + the stream-byte cap (ADR #52) + the wall-clock
`--timeout` (ADR #43) + `step_cap_S` globally (pd-side driver only).

Timeout (ADR #43): the per-subprocess wall-clock cap is `--timeout` (default 600, or
$HETERO_DOC_TIMEOUT). A cold large-doc review on the pro tier can exceed 600s — raise the
timeout OR drop a tier (`--model haiku`), do NOT remap the profile alias (timeout ⊥ model
selection; cold-start is transient — DeepSeek auto-caches ~99% after the first call).

Observability + guards (ADR #52): the DEFAULT spawn is stream-json read
INCREMENTALLY (Popen) — a heartbeat line to STDERR every 30s (provider /
elapsed_s / stream_bytes / events / assistant_events / model / idle_s / killed), so a
streaming review is distinguishable from a hang WITHOUT socket forensics, and
`model` names the model the backend actually resolved (result field
`provider_runs[].model`). Wrapper-side breakers CC does not offer mid-run:
`--max-turns` (unbounded agentic loop) and `--max-stream-bytes` (runaway
response stream — an endless stream is visible via partial deltas BEFORE any
message completes). NO idle-kill: a legitimately long single response (cold
large-doc, ADR #43) can be line-silent for minutes — the heartbeat reports
idle_s for the OPERATOR to judge; killing on idle would false-abort cold starts.
`--no-stream` restores the legacy single-envelope json spawn (fallback if a CC
upgrade breaks the stream surface).

Self-contained (workspace rule 7): pure stdlib, no imports from pd or any shared lib.
The script stays independently deployable. Exits 0 on a clean run (verdict pass OR
rewrite-due-to-blocker — the wrapper succeeded); exit 1 on a malformation (the wrapper
could NOT produce a usable result); exit 2 on argument/IO errors.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

SCHEMAS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")
FINDINGS_SCHEMA = os.path.join(SCHEMAS_DIR, "doc-findings.schema.json")
PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")

# CC substrate errors that DEGRADE (recoverable — the different-family leg contributed nothing; the
# same-family primary stands, per ADR #40 additive). Unknown subtypes + auth/invalid-args
# errors are NOT here — they malform (surface the cause), never silently mask a regression
# (rule 3; the FLAG-SURFACE MANIFEST above is the precedent for treating CC drift as
# non-silent). ADR #41. Preserved EXACTLY from pd's hetero_review.py.
DEGRADABLE_CC_SUBTYPES = frozenset(
    {
        "error_max_budget_usd",
        "error_max_turns",
        "error_overwhelmed",
        "error_session_expired",
        "error_session_not_found",
    }
)

# The Morph-caveat signal (ADR #40): a heterogeneous backend exhausts CC's
# --json-schema structured-output retries (CC demands the exact schema shape; a
# non-Claude backend may not comply within the retry budget). This is NOT degradable
# (it is a backend-capability gap, not a transient cap) BUT it IS recoverable via the
# wrapper's own defensive parse — retry once WITHOUT --json-schema (the live-substrate
# path; the wrapper's _extract_json_object + _validate_findings_shape handle a fenced /
# preamble-prose JSON return). See run_claude's auto-fallback. Verified CC v2.1.207.
STRUCTURED_OUTPUT_RETRY_FP = "hetero-cc-error:error_max_structured_output_retries"

# --- Incremental-stream guards + observability (ADR #52) -----------------------
#
# The 2026-08-21 third-party incident (deepseek leg, same-task minimax control
# passed): a provider-side runaway stream burned the FULL wall-clock cap with 0
# bytes visible outside — CC's `-p` output is buffered until process exit AND
# subprocess.run buffers it again, so a 20-minute run was indistinguishable from
# a hang, and the model name actually resolved was unverifiable from outside.
# The DEFAULT spawn is therefore stream-json read INCREMENTALLY (Popen): a stderr
# heartbeat every HEARTBEAT_INTERVAL_S, the LIVE resolved model name (first
# assistant event's message.model), a byte-count runaway breaker, and an explicit
# --max-turns (print mode has NO default turn limit — `error_max_turns` fires
# only when the flag is passed; the docstring's old reliance on it was phantom).
HEARTBEAT_INTERVAL_S = 30.0

# stream-json partial-delta events (--include-partial-messages) carry no findings
# signal — skip their JSON parse by line prefix (hot path: one event per token
# delta; json.loads per delta would dominate parse time on a large review).
_PARTIAL_EVENT_PREFIX = '{"type":"stream_event"'


def _read_schema(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _strip_schema_marker_for_cc(schema_json):
    """Compat shim — strip the `$schema` draft marker before passing the schema to CC's
    `--json-schema` arg. CC's `--json-schema` validator registers ONLY Draft-07 in its
    bundled draft registry; it rejects schemas declaring Draft 2019-09 / 2020-12 with
    `--json-schema is not a valid JSON Schema: no schema with key or ref "<draft-uri>"`
    (the marker URI is treated as an unresolvable ref). Probe matrix (CC v2.1.207):
      Draft 2020-12 / 2019-09 / Draft-06 `$schema` -> REJECT
      Draft-07 `$schema` / no `$schema`            -> ACCEPT
    The committed schema stays Draft 2020-12 (correct; `$defs` is 2019-09+): the OTHER
    consumer, converge.py, uses an EXPLICIT `jsonschema.Draft202012Validator(schema)`
    class (not auto-detect from `$schema`), so stripping the marker does not affect it.
    Backward-compat: `$schema` is an OPTIONAL field; a validator that accepts a schema
    WITH it (CC v2.1.201 per the FLAG-SURFACE MANIFEST) accepts one WITHOUT. So the shim
    is safe across 2.1.201 / 2.1.207. The shim lives at the CC boundary (this wrapper),
    NOT in the committed schema — adapt-at-the-edge, do not mutilate the source.
    See CSR ADR (CC v2.1.207 --json-schema draft-registry regression)."""
    try:
        obj = json.loads(schema_json)
    except json.JSONDecodeError:
        return schema_json  # let CC surface the parse error verbatim
    if isinstance(obj, dict) and "$schema" in obj:
        obj = {k: v for k, v in obj.items() if k != "$schema"}
        return json.dumps(obj)
    return schema_json


def _load_prior(prior_arg):
    """Load prior-findings context: JSON string, `@file` path, or '' → None."""
    if not prior_arg:
        return None
    raw = prior_arg
    if prior_arg.startswith("@"):
        try:
            with open(prior_arg[1:], encoding="utf-8") as fh:
                raw = fh.read()
        except FileNotFoundError:
            print(
                f"warn: prior-findings file not found: {prior_arg[1:]}; ignoring",
                file=sys.stderr,
            )
            return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Not fatal — degrade to a doc-shaped hint in the prompt context.
        return [
            {
                "severity": "warning",
                "kind": "citation-error",
                "location": "prior-findings",
                "evidence": raw,
            }
        ]


# --- provider-template + token-injection (the profiles/<provider>.json pattern) --
#
# profiles/<provider>.json files are COMMITTED TEMPLATES with ROUTING ONLY (BASE_URL
# + model aliases) — NO secret, NO `${...}` token ceremony. The auth token is read
# at runtime from the env var DERIVED BY CONVENTION from the filename:
# `<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN` (deepseek -> DEEPSEEK_ANTHROPIC_AUTH_TOKEN,
# qwen-token-plan-cn -> QWEN_TOKEN_PLAN_CN_ANTHROPIC_AUTH_TOKEN). The wrapper injects it as ANTHROPIC_AUTH_TOKEN
# into a THROWAWAY temp settings file passed to `claude -p` (CC does NOT expand
# ${VAR} itself — verified CC v2.1.201). A template may override the var name via an
# optional `_token_env` field; other `${VAR}` refs (non-token fields) still expand.
# Selection: --profile <name[,name2...]> (multi = dual-/multi-different-family) or HETERO_DOC_PROFILE.


def _project_root_for_env():
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def _load_dotenv_file(path):
    """Load KEY=VALUE pairs from one file into os.environ (setdefault — shell wins).
    Best-effort: missing file / malformed line silently skipped."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _load_dotenv():
    """Load the INVOKING project's env files into os.environ (setdefault — shell always
    wins; between files the first-loaded wins for a shared key). Reads
    <cwd>/.env.solidforge (the host workspace's arm-env IF present — the solidforge arm
    convention; absent + silently skipped in external projects) THEN <cwd>/.env (generic).
    Either may carry the provider token. Best-effort: missing files silently skipped.
    Portable — CWD-based, so csr reads the env of wherever it is invoked. See
    references/install.md."""
    root = _project_root_for_env()
    _load_dotenv_file(os.path.join(root, ".env.solidforge"))
    _load_dotenv_file(os.path.join(root, ".env"))


_ENV_VAR_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


def _expand_env_values(obj):
    """Expand ${VAR} in every string value at ANY depth of `obj` from os.environ.
    Unset vars are left as-is (the token-presence check in _materialize_profile
    catches a missing _token_env value before the spawn). Recurses into nested
    dicts/lists — the profile shape is {env: {ANTHROPIC_AUTH_TOKEN: "${...}"}}."""

    def expand(node):
        if isinstance(node, str):
            return _ENV_VAR_RE.sub(
                lambda m: os.environ.get(m.group(1), m.group(0)), node
            )
        if isinstance(node, dict):
            return {k: expand(v) for k, v in node.items()}
        if isinstance(node, list):
            return [expand(x) for x in node]
        return node

    return expand(obj)


def _resolve_profile_path(name):
    p = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(p):
        sys.exit(
            f"error: unknown provider profile '{name}' (no {p}). "
            "Committed templates live in infra/scripts/profiles/."
        )
    return p


def _resolve_token_var(name, template):
    """The env var holding the provider's auth token.

    Override: the template's optional `_token_env` field. Default (convention):
    `<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN` — e.g. `deepseek` ->
    `DEEPSEEK_ANTHROPIC_AUTH_TOKEN`, `qwen-token-plan-cn` -> `QWEN_TOKEN_PLAN_CN_ANTHROPIC_AUTH_TOKEN`,
    `openai-compat` -> `OPENAI_COMPAT_ANTHROPIC_AUTH_TOKEN`. The convention lets a user
    drop in `profiles/<name>.json` with ROUTING ONLY (no `_token_env`, no `${...}`) and
    the wrapper resolves the token var from the filename — zero ceremony per provider.
    """
    if template.get("_token_env"):
        return template["_token_env"]
    sanitized = re.sub(r"[^A-Za-z0-9]", "_", name).upper()
    return f"{sanitized}_ANTHROPIC_AUTH_TOKEN"


def _materialize_profile(name):
    """Load profiles/<name>.json, resolve + read the token, expand any ${VAR} in the
    template, INJECT the token as ANTHROPIC_AUTH_TOKEN, write a throwaway chmod-600
    temp settings file. Returns the temp path (caller unlinks after the spawn).

    The template carries ONLY routing (BASE_URL + model aliases) — no `ANTHROPIC_AUTH_TOKEN`
    field, no `${...}` token ceremony. The wrapper injects the token from the
    convention var (or `_token_env` override); other `${VAR}` refs in the template
    (e.g. a custom header) still expand. The real token never touches the committed
    profile."""
    src = _resolve_profile_path(name)
    with open(src, encoding="utf-8") as fh:
        tmpl = json.load(fh)
    token_var = _resolve_token_var(name, tmpl)
    token = os.environ.get(token_var, "")
    if not token:
        sys.exit(
            f"error: provider '{name}' needs the env var ${token_var}. The wrapper reads it "
            "from $CLAUDE_PROJECT_DIR or <cwd>/.env.solidforge then <cwd>/.env (shell wins) — "
            "if you cd'd into the skill dir, re-run from the PROJECT ROOT (where .env.solidforge "
            "lives) via the ${CLAUDE_PLUGIN_ROOT} absolute path. Convention: "
            "<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN; override via the template's `_token_env`."
        )
    env_block = _expand_env_values(tmpl.get("env", {}))
    if not isinstance(env_block, dict):
        env_block = {}
    env_block["ANTHROPIC_AUTH_TOKEN"] = (
        token  # convention injection (overrides any stale value)
    )
    payload = {"env": env_block}
    if tmpl.get("model"):
        payload["model"] = tmpl["model"]
    fd, tmp_path = tempfile.mkstemp(suffix=f"-hetero-doc-{name}.json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    try:
        os.chmod(tmp_path, 0o600)
    except OSError:
        pass
    return tmp_path


def adversarial_prompt(artifact_ref, authority_ref, prior_findings=None, round_no=0):
    """Build the DOC-domain ADVERSARIAL prompt (proposal §3; Q2 kind enum).

    Replaces pd's CODE-shaped adversarial prompt with a DOC-shaped one. "Find what
    the primary reviewer missed or got wrong" — NOT "validate". Without this the loop
    degenerates into rubber-stamping. Hunts the Q2 6 doc defect kinds, is BARRED from
    outcome-axis (proposal §2), returns a doc-findings object. Keeps the prior-findings
    framing (fed via --prior-findings) so the different-family leg hunts the gap, not restatements.
    """
    prior_block = ""
    if prior_findings:
        prior_block = (
            "\n\nThe same-family primary reviewer already found:\n"
            f"{json.dumps(prior_findings, ensure_ascii=False, indent=2)}\n"
            "Your job is NOT to confirm these. Find what they MISSED or got WRONG — "
            "a defect kind or doc location they did not cover. Restating the same "
            "defect on the same location is NOT a new finding."
        )
    authority_clause = (
        f" against the authoritative reference `{authority_ref}`"
        if authority_ref
        else (
            " (the doc is self-contained — verify claims against the doc's own "
            "internal consistency)"
        )
    )
    return (
        f"You are an ADVERSARIAL doc reviewer on a different model family than the "
        f"primary reviewer — your value is catching what same-family review misses "
        f"(contradictions the author is blind to, citation drift, scope creep, "
        f"unstated load-bearing concepts). Review the doc at `{artifact_ref}`"
        f"{authority_clause}. Hunt for these defect kinds and NOTHING else:\n"
        f"- contradiction — two claims conflict, or a claim conflicts with a cited source\n"
        f"- authority-chain-break — a claim cites a source that does not say what the doc says\n"
        f"- scope-creep — the doc over-reaches its stated non-goals or conflates domains\n"
        f"- structural-gap — a load-bearing concept is undefined or a step is missing\n"
        f"- citation-error — a file/section/field citation is wrong or unverifiable\n"
        f"- coverage-gap — something that should be addressed for soundness is absent\n"
        f"\nYou are BARRED from OUTCOME-AXIS judgment: do NOT judge whether the doc is "
        f"'right', whether the requirement is correct, or whether the conclusion is "
        f"true — those are human-only. You converge PROCESS-AXIS quality only "
        f"(well-formed, consistent, citation-accurate, coverage-complete).{prior_block}\n\n"
        f"Return a doc-findings-shaped JSON object:\n"
        f'{{"outcome_axis_respected": true, "findings": [{{"defect_id": "<short id>", '
        f'"severity": "blocker"|"warning"|"coverage", "kind": "contradiction"|'
        f'"authority-chain-break"|"scope-creep"|"structural-gap"|"citation-error"|'
        f'"coverage-gap", "location": "<doc section/line/anchor>", "evidence": '
        f'"<concrete quote from the doc AND from the source you verified against>", '
        f'"suggestion": "<optional one-line fix direction>"}}]}}\n\n'
        f"A blocker requires concrete evidence (a quote from source). A guess is a "
        f"warning. An area you could not verify is a coverage-severity finding naming "
        f"it — NEVER silenced (rule 3/4). Note: the coverage SEVERITY (your honest "
        f"disclosure) is DISTINCT from the coverage-gap KIND (a defect in the artifact). "
        f"Round {round_no}."
    )


def _claude_argv(
    profile,
    model,
    schema_json,
    prompt,
    budget_usd,
    allowed_tools,
    observe_hooks,
    max_turns=60,
    stream=True,
):
    """Build the claude -p argv. See FLAG-SURFACE MANIFEST above (CC v2.1.238).

    `--max-turns` bounds the agentic loop (print mode has NO default turn limit —
    `error_max_turns` fires only when the flag is passed; a hit DEGRADES via
    DEGRADABLE_CC_SUBTYPES, ADR #41/#52). `stream=True` selects the DEFAULT
    stream-json mode: --verbose (required by -p + stream-json since CC v2.1.238)
    + --include-partial-messages (token deltas feed the byte cap + heartbeat,
    ADR #52). `stream=False` is the legacy `--output-format json` spawn
    (--no-stream fallback) — no incremental telemetry. The two trailing kwargs
    are ADDITIVE: pre-ADR-#52 positional callers stay source-compatible (the
    divergence.md contract row updates in lockstep with pd's copy)."""
    argv = [
        "claude",
        "-p",
        "--settings",
        profile,
        "--model",
        model,
        "--permission-mode",
        "bypassPermissions",
        "--no-session-persistence",
        "--max-budget-usd",
        str(budget_usd),
        "--max-turns",
        str(max_turns),
    ]
    if stream:
        # -p + stream-json REQUIRES --verbose since CC v2.1.238 (fast rc=1 without
        # it — manifest NOTE 1); --include-partial-messages streams token deltas so
        # the byte cap + heartbeat see liveness BEFORE a message completes.
        argv += [
            "--output-format",
            "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if observe_hooks:
            argv += ["--include-hook-events"]
    else:
        argv += ["--output-format", "json"]
    argv += ["--json-schema", schema_json]
    if allowed_tools:
        argv += ["--allowedTools", allowed_tools]
    argv += ["-p", prompt]
    return argv


# Run-progress sidecar (ADR #61): when --progress-file is given, this wrapper's
# leg boundaries + heartbeats ALSO land as JSONL in that file — the external
# observability contract, extending the ADR #52 stderr heartbeat (which lives
# inside the invoking session's captured tool call) to any outside observer.
# BEST-EFFORT by contract: an observability failure NEVER kills the review —
# OSError is caught, warned ONCE on stderr, and the run continues. The append
# helper is deliberately self-contained (rule 7 — the wrapper does NOT import
# csr_progress; each script stays independently deployable).
_PROGRESS_PATH = None
_PROGRESS_WARNED = False


def _progress_append(event_type, **fields):
    global _PROGRESS_WARNED
    if not _PROGRESS_PATH:
        return
    event = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "type": event_type,
        **fields,
    }
    try:
        parent = os.path.dirname(os.path.abspath(_PROGRESS_PATH))
        os.makedirs(parent, exist_ok=True)
        with open(_PROGRESS_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
            fh.flush()
    except OSError as exc:
        if not _PROGRESS_WARNED:
            print(
                f"warning: progress file unwritable ({exc}); continuing without it",
                file=sys.stderr,
            )
            _PROGRESS_WARNED = True


def _emit_heartbeat(provider, tele):
    """One progress line to STDERR (stdout stays the single result JSON). The
    heartbeat is the wrapper's liveness contract (ADR #52): an outer orchestrator
    (or a human at a terminal) distinguishes a streaming review from a hang
    WITHOUT socket-level forensics; `model` names the model the backend actually
    resolved (closes the 2026-08-21 incident's "cannot confirm the model name
    from outside" gap); `idle_s` reports line-silence for the OPERATOR to judge
    (deliberately NOT a kill condition — a cold-start single response can be
    legitimately line-silent for minutes, ADR #43)."""
    print(
        json.dumps(
            {
                "type": "hetero-heartbeat",
                "provider": provider,
                "elapsed_s": round(tele["elapsed_s"], 1),
                "stream_bytes": tele["stream_bytes"],
                "events": tele["events"],
                "assistant_events": tele["assistant_events"],
                "model": tele["model"],
                "idle_s": round(tele["idle_s"], 1),
                "killed": tele["killed"],
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
        flush=True,
    )
    # ADR #61 sidecar tee: the same heartbeat lands in the progress file too.
    _progress_append(
        "hetero-heartbeat",
        provider=provider,
        elapsed_s=round(tele["elapsed_s"], 1),
        stream_bytes=tele["stream_bytes"],
        events=tele["events"],
        assistant_events=tele["assistant_events"],
        model=tele["model"],
        idle_s=round(tele["idle_s"], 1),
        killed=tele["killed"],
    )


def _run_streamed(argv, timeout_s, max_stream_bytes, provider):
    """Stream-mode spawn (ADR #52): Popen + incremental stdout read, so the
    wrapper has LIVE telemetry (stderr heartbeat every HEARTBEAT_INTERVAL_S) and
    two wrapper-side breakers CC does not offer mid-run:

      - wall-clock `timeout_s` (unchanged semantics — kill + the existing
        `hetero-subprocess-timeout` fingerprint);
      - `max_stream_bytes` on accumulated stdout INCLUDING token-delta partial
        events (kill + `hetero-stream-bytes-cap`) — an endless single response
        is visible via partial deltas BEFORE any message completes, which
        message-level stream-json would miss entirely.

    Reader THREADS drain stdout + stderr concurrently (an undrained pipe can
    block the child). The first assistant event's message.model is captured as
    the RESOLVED model (externally verifiable post-hoc). Returns
    `(raw_stdout, returncode, tele, stderr_tail)`; `tele["killed"]` is
    None | "timeout" | "bytes-cap" — the caller classifies, this never raises
    on kill paths. CC's own stderr (previously discarded) is tailed so substrate
    diagnostics (e.g. `[claude-code:unrecognized_model]` telemetry) survive.
    """
    tele = {
        "model": None,
        "assistant_events": 0,
        "events": 0,
        "stream_bytes": 0,
        "elapsed_s": 0.0,
        "idle_s": 0.0,
        "killed": None,
    }
    out_chunks = []
    err_tail = collections.deque(maxlen=24)
    lock = threading.Lock()
    started = time.monotonic()
    state = {"last_line_at": started}

    proc = subprocess.Popen(
        argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    def stdout_reader():
        for line in proc.stdout or ():
            with lock:
                tele["stream_bytes"] += len(line.encode("utf-8", "replace"))
                tele["events"] += 1
                state["last_line_at"] = time.monotonic()
                if not line.startswith(_PARTIAL_EVENT_PREFIX):
                    evt = _try_json(line)
                    if isinstance(evt, dict) and evt.get("type") == "assistant":
                        tele["assistant_events"] += 1
                        if tele["model"] is None:
                            msg = evt.get("message")
                            if isinstance(msg, dict) and isinstance(
                                msg.get("model"), str
                            ):
                                tele["model"] = msg["model"]
                out_chunks.append(line)

    def stderr_reader():
        for line in proc.stderr or ():
            err_tail.append(line.rstrip("\n"))

    t_out = threading.Thread(target=stdout_reader, daemon=True)
    t_err = threading.Thread(target=stderr_reader, daemon=True)
    t_out.start()
    t_err.start()

    next_beat = started + HEARTBEAT_INTERVAL_S
    while True:
        if proc.poll() is not None:
            break
        now = time.monotonic()
        tele["elapsed_s"] = now - started
        with lock:
            tele["idle_s"] = now - state["last_line_at"]
        if tele["elapsed_s"] >= timeout_s:
            tele["killed"] = "timeout"
            proc.kill()
            break
        if max_stream_bytes and tele["stream_bytes"] > max_stream_bytes:
            tele["killed"] = "bytes-cap"
            proc.kill()
            break
        if now >= next_beat:
            _emit_heartbeat(provider, tele)
            next_beat = now + HEARTBEAT_INTERVAL_S
        time.sleep(0.5)

    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=15)
    t_out.join(timeout=15)
    t_err.join(timeout=15)
    tele["elapsed_s"] = time.monotonic() - started
    # Final heartbeat so the tail state (esp. the kill reason) lands on stderr.
    _emit_heartbeat(provider, tele)
    return (
        "".join(out_chunks),
        proc.returncode,
        tele,
        "\n".join(list(err_tail)[-8:]),
    )


def _parse_cc_substrate_error(raw):
    """Extract (subtype, errors) from a CC substrate-error envelope.

    CC exits rc!=0 with EMPTY stderr and puts the reason in stdout as
    `{"type":"result","subtype":"error_max_budget_usd","is_error":true,"errors":[...]}`.
    Handles BOTH output modes: `--output-format json` (a single object) AND
    `--output-format stream-json` (`--observe-hooks`; JSONL — walk for the result event).
    Returns (subtype, errors) for any CC error envelope (the caller decides degrade vs
    malform via DEGRADABLE_CC_SUBTYPES), else (None, []). Defensive: any parse failure →
    (None, []). ADR #41. Preserved EXACTLY from pd's hetero_review.py.
    """
    if not raw:
        return None, []
    obj = _try_json(raw)
    if not (isinstance(obj, dict) and obj.get("is_error")):
        # stream-json mode (--observe-hooks): stdout is JSONL — walk for a result event
        # carrying the CC error envelope. Reuses _try_json per line.
        obj = None
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            cand = _try_json(line)
            if isinstance(cand, dict) and cand.get("is_error"):
                obj = cand
                break
    if not (isinstance(obj, dict) and obj.get("is_error")):
        return None, []
    subtype = obj.get("subtype")
    if not isinstance(subtype, str) or not subtype:
        return None, []
    raw_errors = obj.get("errors", [])

    def render(e):
        return e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)

    if isinstance(raw_errors, list):
        errors = [render(e) for e in raw_errors if e is not None]
    elif raw_errors is not None:
        errors = [render(raw_errors)]
    else:
        errors = []
    return subtype, errors


def _stdout_indicates_success(raw):
    """True iff the CC stdout envelope is a SUCCESS (subtype 'success'), regardless of the
    process exit code or the is_error flag. CC's protocol: the result event's `subtype` is
    authoritative — 'success' means a usable result was produced. Handles both
    --output-format json (a single object) and stream-json (JSONL — walk for the result
    event). Defensive: any parse failure -> False.

    Rationale (CSR-I6 dogfood): a long-doc review hit a CC backend quirk — CC exited
    NON-ZERO with a contradictory envelope (subtype 'success' + is_error true). The
    returncode!=0 branch mis-treated it as a malformation (hetero-cc-error:success),
    discarding a usable result. Trusting the subtype over the exit code recovers it.
    ADR #41 (DEGRADE handling) is unchanged — this only adds a success short-circuit
    BEFORE the substrate-error parse, so a genuinely-degraded/error envelope still
    degrades/malforms as before."""
    if not raw:
        return False
    obj = _try_json(raw)
    if isinstance(obj, dict) and obj.get("subtype") == "success":
        return True
    for line in raw.splitlines():
        cand = _try_json(line.strip())
        if isinstance(cand, dict) and cand.get("subtype") == "success":
            return True
    return False


def _run_claude_once(
    argv,
    timeout_s,
    dry_run,
    dry_findings,
    dry_malform=False,
    dry_budget=False,
    guards=None,
):
    """Spawn the subprocess ONCE (or dry-run). Returns a dict:
    {findings, hook_count, ok, fingerprint, error_subtype, errors}.

    - findings: the parsed doc-findings-shaped return (None on malformation/degrade).
    - hook_count: hook events observed (0 unless --observe-hooks).
    - ok: True iff the subprocess exited 0 AND the return parsed cleanly.
    - fingerprint: a malformation fingerprint ("" when ok or when the error DEGRADED —
      degraded legs are not malformations).
    - error_subtype: a CC substrate-error subtype when rc!=0 but stdout carried a clean
      `is_error` envelope (None otherwise). The caller DEGRADES on DEGRADABLE_CC_SUBTYPES,
      malforms on the rest. ADR #41.
    - errors: the envelope's `errors` strings (for the coverage/degrade note).
    - model / assistant_events / stream_bytes / elapsed_s / cc_stderr_tail: stream-mode
      telemetry (ADR #52); the legacy json spawn carries only cc_stderr_tail.

    DEGRADE logic preserved EXACTLY from pd's hetero_review.py (ADR #41). The trailing
    `guards` kwarg is ADDITIVE (None = legacy json spawn via subprocess.run; a dict
    {provider, max_stream_bytes} = stream spawn via _run_streamed — heartbeat + byte
    cap + telemetry, ADR #52), so the Phase-A positional-signature contract holds.
    """
    base = {"findings": None, "hook_count": 0, "error_subtype": None, "errors": []}
    if dry_run:
        if dry_malform:
            # Offline malformation path (CSR-I5 offline gate; dogfood blocker).
            return {**base, "ok": False, "fingerprint": "dry-run-malform"}
        if dry_budget:
            # Offline budget-exhaustion (degrade test; rule 4 — no real call). ok=False +
            # fingerprint="" + error_subtype set ⇒ main classifies DEGRADED.
            return {
                **base,
                "ok": False,
                "fingerprint": "",
                "error_subtype": "error_max_budget_usd",
                "errors": ["Reached maximum budget ($0.05)"],
            }
        # Offline path for the CSR-I5 wiring test (rule 4: no real model call in the gate).
        return {**base, "findings": dry_findings, "ok": True, "fingerprint": ""}

    tele_fields = {}
    if guards is not None:
        raw, rc_num, tele, err_tail = _run_streamed(
            argv, timeout_s, guards["max_stream_bytes"], guards["provider"]
        )
        tele_fields = {
            "model": tele["model"],
            "assistant_events": tele["assistant_events"],
            "stream_bytes": tele["stream_bytes"],
            "elapsed_s": round(tele["elapsed_s"], 1),
        }
        if err_tail:
            tele_fields["cc_stderr_tail"] = err_tail
        if tele["killed"] == "timeout":
            # Same fingerprint + semantics as the legacy TimeoutExpired path — the
            # wall-clock cap (ADR #43) now kills MID-STREAM with telemetry attached.
            return {
                **base,
                "ok": False,
                "fingerprint": "hetero-subprocess-timeout",
                **tele_fields,
            }
        if tele["killed"] == "bytes-cap":
            # Wrapper-side runaway breaker (ADR #52). NOT degradable: CC produced no
            # envelope (killed mid-stream) — malform loudly (rule 3); a silent retry
            # would just re-buy the same runaway stream.
            return {
                **base,
                "ok": False,
                "fingerprint": "hetero-stream-bytes-cap",
                **tele_fields,
            }
    else:
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout_s
            )
        except subprocess.TimeoutExpired:
            return {**base, "ok": False, "fingerprint": "hetero-subprocess-timeout"}
        raw, rc_num = proc.stdout, proc.returncode
        if proc.stderr.strip():
            # CC's own stderr (previously DISCARDED — an observability gap surfaced by
            # the 2026-08-21 diagnosis): substrate diagnostics such as the
            # `[claude-code:unrecognized_model]` telemetry line survive to the result.
            tele_fields["cc_stderr_tail"] = proc.stderr.strip()[-1000:]

    if rc_num != 0 and not _stdout_indicates_success(raw):
        # CC substrate errors (budget/turns/overwhelmed) land in STDOUT as a clean envelope;
        # stderr is empty. Parse BEFORE malforming — a recoverable cap DEGRADES, not rewrites.
        # (A non-zero exit WITH a success envelope — subtype 'success' — is a CC backend quirk
        # surfaced by the CSR-I6 dogfood: subtype is authoritative, the result is usable, so
        # _stdout_indicates_success short-circuits to the normal parse below. ADR #41 unchanged.)
        subtype, errors = _parse_cc_substrate_error(raw)
        if subtype in DEGRADABLE_CC_SUBTYPES:
            return {
                **base,
                "ok": False,
                "fingerprint": "",
                "error_subtype": subtype,
                "errors": errors,
                **tele_fields,
            }
        if subtype:
            # A NON-degradable CC error (invalid-args / auth) — surface the subtype in the
            # fingerprint (richer than hetero-subprocess-rc{N}) and malform; do NOT mask it.
            fp = f"hetero-cc-error:{subtype}"
        else:
            fp = f"hetero-subprocess-rc{rc_num}"
        return {**base, "ok": False, "fingerprint": fp, "errors": errors, **tele_fields}

    if argv[argv.index("--output-format") + 1] == "stream-json":
        findings, hook_count, ok, fp = _parse_stream_json(raw)
    else:
        findings, hook_count, ok, fp = _parse_json_return(raw)
    return {
        **base,
        "findings": findings,
        "hook_count": hook_count,
        "ok": ok,
        "fingerprint": fp,
        **tele_fields,
    }


def _argv_without_json_schema(argv):
    """Return a copy of argv with `--json-schema` and its value removed (defensive-parse
    mode). Used by run_claude's structured-output-retry fallback. `--json-schema <value>`
    is a two-token arg; drop both. Leaves `--output-format json` intact so the CC wrapper
    envelope is still parsed."""
    out = []
    skip_next = False
    for a in argv:
        if skip_next:
            skip_next = False
            continue
        if a == "--json-schema":
            skip_next = True
            continue
        out.append(a)
    return out


def run_claude(
    argv,
    timeout_s,
    dry_run,
    dry_findings,
    dry_malform=False,
    dry_budget=False,
    guards=None,
):
    """Spawn the subprocess (or dry-run), with a ONE-SHOT auto-fallback on the Morph-caveat
    structured-output-retry failure. Signature + DEGRADE logic preserved (ADR #41);
    the trailing `guards` kwarg (ADDITIVE, ADR #52) passes through to BOTH spawns —
    the structured-output fallback retry keeps the stream mode + guards.

    A heterogeneous backend that exhausts CC's `--json-schema` structured-output retries
    (STRUCTURED_OUTPUT_RETRY_FP) cannot satisfy CC's strict shape enforcement, but it CAN
    still return usable findings as fenced / preamble-prose JSON that the wrapper's
    defensive parse (_extract_json_object + _validate_findings_shape) handles (the
    live-substrate path, lines ~640-645). So: spawn once WITH `--json-schema`; on that
    specific malformation, retry once WITHOUT it and stamp `fell_back_to_unstructured=True`
    on the result (honest disclosure — rule 3; surfaced in the coverage trail by main()).

    Backward-compatible: compliant backends never hit the retry, so they see no change. The
    fallback is gated on `--json-schema in argv` (a non-schema caller is unaffected) and on
    the EXACT fingerprint (a different malformation never retries — never mask a regression).
    """
    rc = _run_claude_once(
        argv, timeout_s, dry_run, dry_findings, dry_malform, dry_budget, guards=guards
    )
    if (
        argv is not None
        and "--json-schema" in argv
        and not rc["ok"]
        and rc["fingerprint"] == STRUCTURED_OUTPUT_RETRY_FP
    ):
        rc = _run_claude_once(
            _argv_without_json_schema(argv),
            timeout_s,
            dry_run,
            dry_findings,
            dry_malform,
            dry_budget,
            guards=guards,
        )
        rc["fell_back_to_unstructured"] = True
    return rc


def _parse_json_return(raw):
    """Parse --output-format json return.

    CC v2.1.201 wraps the structured output as
    `{"type":"result", ..., "result": "<json-string>", "structured_output": <obj>, ...}`
    (verified live). Extract the doc-findings-shaped object from `structured_output`
    (preferred — already parsed) or `result` (a JSON string). Fall back to the raw
    object if the subprocess returned the shape without a wrapper.
    """
    try:
        wrapper = json.loads(raw)
    except json.JSONDecodeError:
        return None, 0, False, "hetero-malformed-json"
    obj = None
    if isinstance(wrapper, dict):
        so = wrapper.get("structured_output")
        if isinstance(so, dict):
            obj = so
        elif isinstance(wrapper.get("result"), str):
            # structured_output was null — extract from `result` (the backend may have
            # wrapped the JSON in a markdown fence with preamble prose).
            obj = _extract_json_object(wrapper["result"])
    if obj is None and isinstance(wrapper, dict):
        obj = wrapper  # bare shape, no CC wrapper
    if obj is None:
        return None, 0, False, "hetero-no-structured-output"
    fp = _validate_findings_shape(obj)
    if fp:
        return None, 0, False, fp
    return obj, 0, True, ""


def _parse_stream_json(raw):
    """Parse --output-format stream-json return: walk lines for the final structured
    result + count hook events. Best-effort (the live dogfood exercises this).
    Token-delta partial events (--include-partial-messages, ADR #52) are skipped by
    line prefix BEFORE the JSON parse — they carry no findings signal and are the
    hot path (one event per delta)."""
    hook_count = 0
    last_result_obj = None
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(_PARTIAL_EVENT_PREFIX):
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "hook":
            hook_count += 1
        # Prefer the parsed structured_output on the final result event (CC v2.1.201).
        if evt.get("type") == "result" and isinstance(
            evt.get("structured_output"), dict
        ):
            last_result_obj = evt["structured_output"]
        elif evt.get("type") in ("assistant", "result") and isinstance(
            evt.get("message"), dict
        ):
            # The final assistant message may carry the structured result as text.
            content = evt["message"].get("content")
            txt = _extract_text(content)
            if txt:
                cand = _try_json(txt)
                if cand is not None:
                    last_result_obj = cand
        if (
            last_result_obj is None
            and evt.get("type") == "result"
            and isinstance(evt.get("result"), dict)
        ):
            last_result_obj = evt["result"]
    if last_result_obj is not None:
        fp = _validate_findings_shape(last_result_obj)
        if fp:
            return None, hook_count, False, fp
        return last_result_obj, hook_count, True, ""
    return None, hook_count, False, "hetero-stream-no-result"


def _extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                return part.get("text", "")
    return None


def _try_json(txt):
    try:
        return json.loads(txt)
    except (json.JSONDecodeError, TypeError):
        return None


# Live-substrate caveat (verified in pd's Phase-1 dogfood; carries over): under a
# complex review prompt, the non-Claude backend often returns the JSON inside a
# markdown code fence with preamble prose, and CC's `structured_output` comes back
# null. The wrapper must extract the JSON defensively from `result` (fence-aware,
# then brace-balanced).
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)


def _extract_json_object(text):
    """Extract the first JSON object from text. Prefer a ```json fence; else the
    first brace-balanced `{...}` substring. Returns the parsed dict or None.
    Preserved verbatim from pd's hetero_review.py."""
    if not text:
        return None
    m = _JSON_FENCE_RE.search(text)
    candidate = m.group(1) if m else text
    obj = _try_json(candidate)
    if isinstance(obj, dict):
        return obj
    start = candidate.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(candidate)):
            ch = candidate[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    obj = _try_json(candidate[start : i + 1])
                    if isinstance(obj, dict):
                        return obj
                    break
        start = candidate.find("{", start + 1)
    return None


def _validate_findings_shape(obj):
    """Return a malformation fingerprint if the shape violates doc-findings; else ''.

    Signature `(obj) -> str` preserved per the Phase-A compat constraint (proposal
    §5 / F3). The VALIDATION LOGIC diverges from pd's hetero_review.py: this accepts
    the doc-findings shape (top-level `outcome_axis_respected` bool + `findings` list;
    per-finding `severity` ∈ {blocker,warning,coverage} — coverage preserved per Q2;
    `kind` ∈ the 6 Q2 doc kinds). The full JSON-schema validation lives in the
    findings shape-contract gate (CSR-I5); this is a fast pre-check so run_claude can
    distinguish a usable return from model junk.
    """
    if not isinstance(obj, dict):
        return "hetero-not-object"
    if "findings" not in obj or not isinstance(obj["findings"], list):
        return "hetero-missing-findings"
    if not isinstance(obj.get("outcome_axis_respected"), bool):
        return "hetero-missing-outcome-axis"
    for f in obj["findings"]:
        if not isinstance(f, dict) or "severity" not in f:
            return "hetero-finding-malformed"
        if f["severity"] not in ("blocker", "warning", "coverage"):
            return "hetero-bad-severity"
        if f.get("kind") not in (
            "contradiction",
            "authority-chain-break",
            "scope-creep",
            "structural-gap",
            "citation-error",
            "coverage-gap",
        ):
            return "hetero-bad-kind"
    return ""


def _extract_coverage(findings_obj):
    """Doc-domain: the reviewer's 'could not verify X' disclosures arrive as
    coverage-severity findings (the doc-findings schema has no top-level coverage
    array — unlike pd's violation-log). Collect their evidence/location strings for
    the coverage trail. Returns a de-duplicated list."""
    if not isinstance(findings_obj, dict):
        return []
    findings = findings_obj.get("findings", [])
    if not isinstance(findings, list):
        return []
    cov = []
    for f in findings:
        if isinstance(f, dict) and f.get("severity") == "coverage":
            note = f.get("evidence") or f.get("location") or "undisclosed"
            if note not in cov:
                cov.append(note)
    return cov


def main():
    # Load <project>/.env.solidforge + .env BEFORE argparse captures the os.environ.get
    # defaults below (--profile/$HETERO_DOC_PROFILE, --timeout/$HETERO_DOC_TIMEOUT).
    # Previously this ran AFTER parse_args, so an env var set ONLY in .env (not the
    # shell) was invisible to args -> --profile silently fell back to the hardcoded
    # "deepseek", dropping every other configured provider (e.g. HETERO_DOC_PROFILE
    # =deepseek,minimax ran only deepseek). Shell still wins (setdefault).
    _load_dotenv()
    ap = argparse.ArgumentParser(
        description="different-family doc-domain adversarial review wrapper (CSR-I3)."
    )
    ap.add_argument(
        "--artifact",
        required=True,
        help="Path/ref to the DOC under review (a doc has no diff/blueprint).",
    )
    ap.add_argument(
        "--authority",
        default="",
        help="Optional authoritative reference (doc + section) to verify claims "
        "against. Empty (default) = the doc is self-contained; verify against its "
        "own internal consistency.",
    )
    ap.add_argument(
        "--profile",
        default=os.environ.get("HETERO_DOC_PROFILE", "deepseek"),
        help="Provider NAME (or comma-list for dual-/multi-different-family), resolved against "
        "profiles/<name>.json templates. Default: $HETERO_DOC_PROFILE or 'deepseek'. "
        "The token is read at runtime from the convention var "
        "<UPPERCASE-FILENAME>_ANTHROPIC_AUTH_TOKEN (e.g. "
        "DEEPSEEK_ANTHROPIC_AUTH_TOKEN) — the SOLE source (the suffix namespaces "
        "it to this substrate, NOT the provider's native <FILENAME>_API_KEY). "
        "Override via the template's _token_env. The committed profile carries no secret.",
    )
    ap.add_argument(
        "--model", default="opus", help="Tier/model alias resolved via the profile."
    )
    ap.add_argument(
        "--budget-usd",
        type=float,
        default=12.0,
        help="Coarse runaway breaker per subprocess — NOT real spend. CC prices "
        "UNRECOGNIZED models (any non-Anthropic backend) at premium fallback rates "
        "(measured $0.24 for ONE tiny turn at CC v2.1.238 — ADR #42 amendment), so "
        "the cap fires on CC's mismeasure; real accounting is the provider's own "
        "dashboard. Default 12.0 leaves a mid-size multi-turn review headroom under "
        "that mismeasure. If a review still trips the cap it DEGRADES (ADR #41), "
        "not rewrites.",
    )
    ap.add_argument(
        "--allowed-tools",
        default="Read Grep Glob Bash",
        help="Tools the different-family subprocess may wield (read-only review surface).",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("HETERO_DOC_TIMEOUT", "600")),
        help="Subprocess wall-clock cap (seconds). Default 600, or $HETERO_DOC_TIMEOUT — "
        "raise it (or drop a tier via --model) for a cold large-doc review on the "
        "pro tier; do NOT remap the profile alias to dodge a timeout (ADR #43).",
    )
    ap.add_argument(
        "--max-turns",
        type=int,
        default=int(os.environ.get("HETERO_DOC_MAX_TURNS", "60")),
        help="Hard cap on CC agentic turns per subprocess. Print mode has NO default "
        "turn limit — an unbounded tool loop runs until the wall-clock cap (ADR #52). "
        "Tripping it DEGRADES (error_max_turns is degradable, ADR #41). Default 60, "
        "or $HETERO_DOC_MAX_TURNS. Dense docs can legitimately spend dozens of turns; a fast-cycling runaway loop still dies early.",
    )
    ap.add_argument(
        "--max-stream-bytes",
        type=int,
        default=int(
            os.environ.get("HETERO_DOC_MAX_STREAM_BYTES", str(64 * 1024 * 1024))
        ),
        help="Runaway breaker on accumulated stream-json stdout (bytes, INCLUDING "
        "token-delta partial events — an endless response stream is visible BEFORE "
        "any message completes; ADR #52). Tripping it MALFORMS loudly (the "
        "2026-08-21 incident class). Default 64MiB, or $HETERO_DOC_MAX_STREAM_BYTES.",
    )
    ap.add_argument(
        "--no-stream",
        action="store_true",
        help="Legacy `--output-format json` spawn: single end-of-run envelope, NO "
        "incremental telemetry / heartbeat / byte cap (subprocess.run full-buffer). "
        "The documented FALLBACK if a CC upgrade breaks the stream-json surface "
        "(FLAG-SURFACE MANIFEST). Incompatible with --observe-hooks.",
    )
    ap.add_argument(
        "--observe-hooks",
        action="store_true",
        help="Add --include-hook-events to the DEFAULT stream-json spawn for gate "
        "observability.",
    )
    ap.add_argument(
        "--progress-file",
        default="",
        help="Run-progress sidecar (ADR #61): append this leg's boundary events "
        "(hetero-leg-start/-end) + streamed heartbeats as JSONL to this path, in "
        "addition to the stderr heartbeat. Best-effort — an unwritable path warns "
        "once and never fails the review.",
    )
    ap.add_argument(
        "--round-index",
        type=int,
        default=1,
        help="This leg's round number (label only; the convergence loop is "
        "CSR-I4-driver-driven per proposal §3 — the driver alternates same-family ↔ this "
        "wrapper, and the cap = the count of wrapper invocations).",
    )
    ap.add_argument(
        "--prior-findings",
        default="",
        help="Accumulated debate context (the same-family primary's latest findings) as "
        "JSON, or `@file` to read from a path. Fed to the adversarial prompt so the "
        "different-family leg hunts what the primary MISSED, not what it already found.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Offline mode: emit a canned doc-findings return, no claude call "
        "(for the CSR-I5 wiring gate).",
    )
    ap.add_argument(
        "--dry-run-malform",
        action="store_true",
        help="Offline malformation: forces the malformation path (no claude call). "
        "For the CSR-I5 offline convergence-policy gate.",
    )
    ap.add_argument(
        "--dry-run-budget",
        action="store_true",
        help="Offline budget-exhaustion: forces the DEGRADE path (no claude call). "
        "Returns a canned error_max_budget_usd envelope so the wiring gate exercises "
        "degrade end-to-end (ADR #41).",
    )
    ap.add_argument(
        "--findings-schema",
        default=FINDINGS_SCHEMA,
        help="Schema JSON passed via --json-schema (default: doc-findings.schema.json).",
    )
    args = ap.parse_args()
    # Run-progress sidecar (ADR #61): module-global, NOT a run_claude kwarg, so the
    # preserved function-signature contract (divergence.md) stays untouched.
    global _PROGRESS_PATH
    _PROGRESS_PATH = args.progress_file or None
    # The offline knobs (--dry-run-malform / --dry-run-budget) imply --dry-run — without
    # this, --dry-run-budget alone would skip run_claude's canned branch and fall through to
    # subprocess.run(None). Same footgun pre-existed in pd for --dry-run-malform; carried over.
    if args.dry_run_malform or args.dry_run_budget:
        args.dry_run = True
    if args.no_stream and args.observe_hooks:
        # Hook events exist only in stream-json output; the json fallback cannot
        # serve them. Fail fast (argument error, exit 2) instead of silently
        # dropping the requested observability (rule 3).
        print(
            "error: --no-stream (json fallback) cannot serve --observe-hooks "
            "(hook events require stream-json output)",
            file=sys.stderr,
        )
        return 2

    try:
        schema_json = _strip_schema_marker_for_cc(_read_schema(args.findings_schema))
    except FileNotFoundError:
        print(
            f"error: findings schema not found: {args.findings_schema}", file=sys.stderr
        )
        return 2

    provider_names = [p.strip() for p in args.profile.split(",") if p.strip()]
    if not provider_names:
        print("error: --profile requires at least one provider name", file=sys.stderr)
        return 2
    # Validate every provider NAME up front (fail-fast on a typo / unknown template,
    # regardless of dry-run — _resolve_profile_path sys.exits with a clear error).
    for name in provider_names:
        _resolve_profile_path(name)

    # Canned doc-findings-shaped return for dry-run (offline test path).
    dry_findings = {
        "outcome_axis_respected": True,
        "findings": [],
    }

    # ONE different-family review per provider per invocation (faithful to proposal §3: the same-family
    # primary ↔ different-family alternation is CSR-I4-DRIVEN — this wrapper is the different-family leg only;
    # the driver alternates + caps). Multi-provider (dual-/multi-different-family) runs each backend
    # independently + merges; a finding is tagged with its `provider` when >1 backend
    # runs, so reconciliation (proposal §3 table) can attribute it.
    prior = _load_prior(args.prior_findings)
    prompt = adversarial_prompt(args.artifact, args.authority, prior, args.round_index)
    per_provider = []  # per-provider result dicts
    for name in provider_names:
        tmp_path = None
        argv = None
        if not args.dry_run and not args.dry_run_malform and not args.dry_run_budget:
            tmp_path = _materialize_profile(name)  # fail-fast on missing token env var
            argv = _claude_argv(
                tmp_path,
                args.model,
                schema_json,
                prompt,
                args.budget_usd,
                args.allowed_tools,
                args.observe_hooks,
                max_turns=args.max_turns,
                stream=not args.no_stream,
            )
        # Stream guards ride every spawn incl. the structured-output fallback retry;
        # None (legacy --no-stream json spawn) keeps the pre-ADR-#52 spawn behavior.
        guards = (
            None
            if args.no_stream
            else {"provider": name, "max_stream_bytes": args.max_stream_bytes}
        )
        _progress_append("hetero-leg-start", round=args.round_index, provider=name)
        try:
            rc = run_claude(
                None if argv is None else argv,
                args.timeout,
                args.dry_run,
                dry_findings,
                args.dry_run_malform,
                dry_budget=args.dry_run_budget,
                guards=guards,
            )
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
        _progress_append(
            "hetero-leg-end",
            round=args.round_index,
            provider=name,
            outcome=(
                "ok"
                if rc["ok"]
                else ("degraded" if rc["error_subtype"] else "malformed")
            ),
            findings=len((rc["findings"] or {}).get("findings", [])) if rc["ok"] else 0,
            model=rc.get("model"),
            elapsed_s=rc.get("elapsed_s"),
            degraded=bool(rc["error_subtype"]),
        )
        findings_obj = rc["findings"]
        pf = (findings_obj or {}).get("findings", []) if rc["ok"] else []
        if len(provider_names) > 1:
            for f in pf:
                f.setdefault("provider", name)
        per_provider.append(
            {
                "name": name,
                "findings": pf,
                "model_coverage": _extract_coverage(findings_obj) if rc["ok"] else [],
                "ok": rc["ok"],
                "fingerprint": rc["fingerprint"],
                "hook_count": rc["hook_count"],
                "error_subtype": rc["error_subtype"],
                "errors": rc["errors"],
                "fell_back_to_unstructured": rc.get("fell_back_to_unstructured", False),
                "model": rc.get("model"),
                "assistant_events": rc.get("assistant_events", 0),
                "stream_bytes": rc.get("stream_bytes", 0),
                "elapsed_s": rc.get("elapsed_s"),
                "cc_stderr_tail": rc.get("cc_stderr_tail", ""),
            }
        )

    # Aggregate across providers (single = classic different-family; multi = dual-/multi-different-family).
    all_findings = [f for p in per_provider for f in p["findings"]]
    # Genuine malformation = ok=False AND no degradable subtype (unparseable, or a
    # non-degradable CC error like invalid-args/auth). These surface a fingerprint + rewrite.
    malform_fps = [
        p["fingerprint"] for p in per_provider if not p["ok"] and not p["error_subtype"]
    ]
    # Degrade = a DEGRADABLE substrate error (ok=False, error_subtype set, fingerprint "").
    # The different-family leg contributed nothing; the same-family primary stands (proposal §3 reconcile table).
    degraded_providers = [
        {"provider": p["name"], "subtype": p["error_subtype"], "errors": p["errors"]}
        for p in per_provider
        if p["error_subtype"]
    ]
    any_malform = bool(malform_fps)
    degraded = bool(degraded_providers)
    blockers = [f for f in all_findings if f.get("severity") == "blocker"]
    malformation = ",".join(malform_fps)

    if any_malform:
        # Genuine malformation / non-degradable CC error. Never silent (rule 3).
        verdict = "rewrite"
    else:
        # passed iff NO non-degraded provider surfaced a blocker (rule 4: warnings/coverage
        # are advisory). Degraded providers contribute 0 findings and never force a rewrite.
        gate_passed = len(blockers) == 0
        verdict = "pass" if gate_passed else "rewrite"

    # coverage: the degrade-honestly trail (degrade + malform notes) + the reviewer's own
    # coverage-severity disclosures (doc-domain: those arrive as findings, extracted per
    # provider — the schema has no top-level coverage array).
    coverage = []
    for d in degraded_providers:
        detail = "; ".join(d["errors"]) if d["errors"] else "no detail"
        coverage.append(f"provider {d['provider']} degraded: {d['subtype']} ({detail})")
    for p in per_provider:
        if not p["ok"] and not p["error_subtype"] and p["fingerprint"]:
            coverage.append(f"provider {p['name']} malformation: {p['fingerprint']}")
    for p in per_provider:
        if p.get("fell_back_to_unstructured"):
            # Morph-caveat disclosure (rule 3 — never silent): this provider could NOT
            # satisfy CC's --json-schema structured-output retries, so run_claude retried
            # WITHOUT --json-schema and parsed the return defensively. Findings are still
            # shape-validated (_validate_findings_shape); the fallback is disclosed, not
            # masked.
            coverage.append(
                f"provider {p['name']} fell_back_to_unstructured "
                "(--json-schema structured-output retries exhausted; defensive parse used)"
            )
    for p in per_provider:
        for c in p["model_coverage"]:
            if c not in coverage:
                coverage.append(c)

    # Per-run substrate telemetry (ADR #52): the resolved model name, agentic turns,
    # stream bytes, elapsed — the 2026-08-21 incident's post-hoc questions ("which
    # model actually ran? was the stream alive?") answered IN the record.
    # cc_stderr_tail (CC substrate diagnostics, e.g. unrecognized_model telemetry)
    # is included when present.
    provider_runs = []
    for p in per_provider:
        run_entry = {
            "name": p["name"],
            "model": p["model"],
            "assistant_events": p["assistant_events"],
            "stream_bytes": p["stream_bytes"],
            "elapsed_s": p["elapsed_s"],
        }
        if p["cc_stderr_tail"]:
            run_entry["cc_stderr_tail"] = p["cc_stderr_tail"][-500:]
        provider_runs.append(run_entry)

    result = {
        "verdict": verdict,
        "degraded": degraded,
        "degraded_providers": degraded_providers,
        "findings_count": len(all_findings),
        "findings": all_findings,
        "coverage": coverage,
        "malformation": malformation,
        "providers": [p["name"] for p in per_provider],
        "provider_runs": provider_runs,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Exit code: 0 = the wrapper produced a usable result (pass OR rewrite-due-to-blocker
    # OR degrade — read the structured fields for which). 1 = malformation (the wrapper
    # could NOT parse a usable return). 2 = argument/IO error. pd always exits 0 because
    # its loop_state/driver interprets the verdict; the doc-wrapper is standalone (no
    # loop_state — proposal Q3), so it surfaces malformation via exit 1 for the CSR-I4
    # subprocess contract.
    return 1 if any_malform else 0


if __name__ == "__main__":
    sys.exit(main())
