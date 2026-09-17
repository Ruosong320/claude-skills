#!/usr/bin/env python3
"""Phase 1 triage for every skill in this ratchet repo.

Prints one row per skill: runtime red lights (wording + tool-name class),
frontmatter health, and cheap structural proxies for dim3/4/5/6/9.

The tool-name class is a local addition: darwin's own red-light grep only
matches wording ("in Claude Code", "Cursor only", ...) and let
process-thinker's hard requirement "at least one WebSearch per node" pass
the gate — unfulfillable on any runtime without that tool.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REDLIGHT_WORD = re.compile(
    r"在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中"
    r"|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b", re.M)
REDLIGHT_TOOL = re.compile(
    r"\b(WebFetch|WebSearch|web_search|TodoWrite|MultiEdit|NotebookEdit|Task tool)\b")
HEDGE = re.compile(r"建议|可以考虑|根据情况|灵活把握|视情况而定|尽量|should probably")
MARKER = re.compile(r"🔴|🛑|CHECKPOINT")
FALLBACK = re.compile(r"触发条件|Trigger\b.*First-line|一线修复")
BLACKLIST = re.compile(r"反模式|Anti-?pattern|What To Avoid|Common Failure Modes|禁止|Blacklist|不要做")
REF_LINK = re.compile(r"\]\((references/[^)]+|assets/[^)]+|scripts/[^)]+)\)")


def frontmatter(text):
    parts = text.split("---")
    if len(parts) < 3:
        return None, "no-frontmatter"
    try:
        import yaml
        fm = yaml.safe_load(parts[1])
    except Exception as exc:
        return None, f"YAML-FAIL: {exc.__class__.__name__}"
    return fm, ""


def main():
    rows = []
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name, "SKILL.md")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        fm, err = frontmatter(text)
        desc = (fm or {}).get("description", "") if fm else ""
        missing = [r for r in set(REF_LINK.findall(text))
                   if not os.path.exists(os.path.join(ROOT, name, r))]
        rows.append({
            "skill": name,
            "lines": text.count("\n") + 1,
            "desc": len(desc) if desc else -1,
            "fm": "OVER" if len(desc) > 1024 else (err or "ok"),
            "word": len(REDLIGHT_WORD.findall(text)),
            "tool": len(REDLIGHT_TOOL.findall(text)),
            "marker": len(MARKER.findall(text)),
            "fallback": "Y" if FALLBACK.search(text) else "-",
            "black": "Y" if BLACKLIST.search(text) else "-",
            "hedge": len(HEDGE.findall(text)),
            "refs": len(REF_LINK.findall(text)),
            "refmiss": len(missing),
        })

    hdr = ("skill", "lines", "desc", "fm", "word", "tool", "marker", "fallback", "black", "hedge", "refs", "refmiss")
    w = [max(len(str(r[h])), len(h)) for h in hdr for r in [rows[0]]]
    print("  ".join(h.ljust(x) for h, x in zip(hdr, w)))
    for r in rows:
        print("  ".join(str(r[h]).ljust(x) for h, x in zip(hdr, w)))
    print()
    print("marker=dim4 显性检查点;  fallback=dim3 三段式表;  black=dim9 反例清单;")
    print("hedge=dim5 软化措辞(>=3 触发扣分);  refmiss=dim6 引用路径不可达数")
    bad = [r["skill"] for r in rows if r["word"] or r["tool"] or r["refmiss"]]
    print(f"\n红灯/断链命中: {bad or '无'}")


if __name__ == "__main__":
    sys.exit(main())
