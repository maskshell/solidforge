#!/usr/bin/env python3
"""Plugin-layout self-check for the Solid Forge plugin.

Loading-chain check for the PLUGIN BOUNDARY (the analog of disconnect_check.py for the new layout). Asserts the plugin's structural pieces exist and are well-formed so a model following progressive disclosure from plugin-enable never hits a dead end:

  - .claude-plugin/plugin.json parses and has name=solidforge, version, description
  - hooks/hooks.json parses, has PreToolUse + PostToolUse, and the hook commands reference ${CLAUDE_PLUGIN_ROOT} and the three hook scripts (blueprint_guard / counters / fast_gate)
  - commands/arm-tools.md exists (the /solidforge:arm-tools Layer 2 command)
  - agents/ contains the 17 plugin-bundled agents (by frontmatter name)
  - every agent that references a references/agent-patterns/<role>.md companion has that companion bundled under skills/parallel-development/references/agent-patterns/ (catches the loading-chain break where an agent points at a companion that was not copied)

The hook command PATHS use ${CLAUDE_PLUGIN_ROOT}/skills/parallel-development/... (resolved at runtime on plugin-enable). This check validates STRUCTURE (files present + well-formed), not runtime resolution.

Run:
    python3 infra/test/plugin_layout.py
"""

import glob
import json
import os
import re
import sys


# plugin_layout.py lives at <plugin-root>/skills/parallel-development/infra/test/.
# Locate the plugin root by walking up to .claude-plugin/plugin.json — depth-independent, so it survives the skill nesting introduced at the Phase 4 cutover (skill moved off the repo root).
def _find_plugin_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, ".claude-plugin", "plugin.json")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:  # filesystem root reached
            return None
        cur = parent


_HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = _find_plugin_root(_HERE)
if PLUGIN_ROOT is None:
    print(f"FAIL: no .claude-plugin/plugin.json found walking up from {_HERE}")
    sys.exit(1)

PLUGIN_JSON = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
HOOKS_JSON = os.path.join(PLUGIN_ROOT, "hooks", "hooks.json")
ARM_TOOLS_MD = os.path.join(PLUGIN_ROOT, "commands", "arm-tools.md")
AGENTS_DIR = os.path.join(PLUGIN_ROOT, "agents")

# The 17 plugin-bundled agents (Solid Forge registers these as solidforge:<name>).
EXPECTED_AGENTS = [
    "architect",
    "backend-developer",
    "code-reviewer",
    "devops-engineer",
    "documentation-writer",
    "frontend-developer",
    "graphiti-config-generator",
    "ios-developer",
    "ios-tester",
    "plan-reviewer",
    "playwright-test-generator",
    "playwright-test-healer",
    "playwright-test-planner",
    "requirements-manager",
    "researcher",
    "security-specialist",
    "tester",
]

# The three hook scripts the hooks.json must wire (by basename substring in the command).
EXPECTED_HOOK_SCRIPTS = ["blueprint_guard", "counters", "fast_gate"]

# The two skills bundled under skills/ (Phase 4 cutover moved them off the repo root).
EXPECTED_SKILLS = ["parallel-development", "blueprint-crafting"]
SKILLS_DIR = os.path.join(PLUGIN_ROOT, "skills")

RESULTS = []


def check(name, cond, how):
    RESULTS.append((name, bool(cond), how))
    print(f"  {'ok' if cond else 'FAIL'}: {name}")
    return bool(cond)


def _frontmatter_name(text):
    """Extract the `name:` field from an agent file's YAML frontmatter."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text[3:]
    m = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def t_plugin_manifest():
    print("plugin.json:")
    if not check(
        "plugin.json exists", os.path.exists(PLUGIN_JSON), f"create {PLUGIN_JSON}"
    ):
        return
    try:
        data = json.load(open(PLUGIN_JSON, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        check("plugin.json parses", False, f"fix JSON: {exc}")
        return
    check(
        "name == solidforge",
        data.get("name") == "solidforge",
        'set name to "solidforge"',
    )
    check("version present", bool(data.get("version")), "set a version")
    check("description present", bool(data.get("description")), "set a description")
    # author must be an OBJECT ({"name": ...}), not a bare string — a string author fails the Claude Code plugin loader ("invalid manifest"). Official plugins use an object.
    check(
        "author is an object",
        isinstance(data.get("author"), dict),
        'set author to {"name": ...} (object; a bare string fails the plugin loader)',
    )


def _hook_commands(hooks_obj):
    cmds = []
    for event in ("PreToolUse", "PostToolUse"):
        for grp in hooks_obj.get(event, []):
            for h in grp.get("hooks", []):
                cmds.append(h.get("command", ""))
    return cmds


def t_hooks_json():
    print("hooks.json:")
    if not check(
        "hooks.json exists", os.path.exists(HOOKS_JSON), f"create {HOOKS_JSON}"
    ):
        return
    try:
        data = json.load(open(HOOKS_JSON, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        check("hooks.json parses", False, f"fix JSON: {exc}")
        return
    hooks = data.get("hooks", {})
    check("has PreToolUse", "PreToolUse" in hooks, "add a PreToolUse entry")
    check("has PostToolUse", "PostToolUse" in hooks, "add a PostToolUse entry")
    cmds = _hook_commands(hooks)
    check(
        "commands reference ${CLAUDE_PLUGIN_ROOT}",
        any("${CLAUDE_PLUGIN_ROOT}" in c for c in cmds),
        "point hook commands at ${CLAUDE_PLUGIN_ROOT}/skills/parallel-development/infra/hooks/*.py",
    )
    for script in EXPECTED_HOOK_SCRIPTS:
        check(
            f"wires hook script {script}.py",
            any(script in c for c in cmds),
            f"add a command invoking {script}.py",
        )


def t_arm_tools_command():
    print("commands/arm-tools.md:")
    check("arm-tools.md exists", os.path.exists(ARM_TOOLS_MD), f"create {ARM_TOOLS_MD}")


def t_agents():
    print("agents/:")
    if not check(
        "agents/ dir exists", os.path.isdir(AGENTS_DIR), f"create {AGENTS_DIR}"
    ):
        return
    agent_files = [
        f
        for f in glob.glob(os.path.join(AGENTS_DIR, "*.md"))
        if not f.endswith(".patterns.md")
    ]
    names = {}
    for f in agent_files:
        text = open(f, encoding="utf-8").read()
        nm = _frontmatter_name(text)
        if nm:
            names[nm] = f
    for expected in EXPECTED_AGENTS:
        check(
            f"agent present: {expected}",
            expected in names,
            f"copy {expected}.agent.md into agents/",
        )
    # companion coverage: any agent referencing a references/agent-patterns/<role>.md
    # companion must have it bundled under skills/parallel-development/references/agent-patterns/.
    # The agent link form is ../skills/parallel-development/references/agent-patterns/<role>.md
    # (contains slashes, so the old [\w-]+\.patterns.md class no longer matches). Structural move,
    # not a decision-point addition (rule 2): the check's purpose is unchanged, only the location.
    ref_re = re.compile(r"parallel-development/references/agent-patterns/([\w-]+)\.md")
    referenced = set()
    for f in agent_files:
        referenced.update(ref_re.findall(open(f, encoding="utf-8").read()))
    companion_dir = os.path.join(
        SKILLS_DIR, "parallel-development", "references", "agent-patterns"
    )
    for comp in sorted(referenced):
        check(
            f"companion bundled: agent-patterns/{comp}.md",
            os.path.exists(os.path.join(companion_dir, comp + ".md")),
            f"copy {comp}.md into skills/parallel-development/references/agent-patterns/ (an agent references it)",
        )


def t_skills():
    print("skills/:")
    for skill in EXPECTED_SKILLS:
        skill_md = os.path.join(SKILLS_DIR, skill, "SKILL.md")
        check(
            f"skill bundled: {skill}/SKILL.md",
            os.path.exists(skill_md),
            f"move {skill}/ under {SKILLS_DIR} (Phase 4 cutover)",
        )


def main():
    for fn in (
        t_plugin_manifest,
        t_hooks_json,
        t_arm_tools_command,
        t_skills,
        t_agents,
    ):
        print(f"\n{fn.__name__}:")
        fn()
    failed = [(n, how) for n, ok, how in RESULTS if not ok]
    print(
        f"\n{'PASS' if not failed else 'FAIL'} ({len(RESULTS) - len(failed)}/{len(RESULTS)})"
    )
    if failed:
        for n, how in failed:
            print(f"  FAILED: {n} -> {how}")
        sys.exit(1)


if __name__ == "__main__":
    main()
