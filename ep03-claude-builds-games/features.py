#!/usr/bin/env python3
"""Exploratory feature count per generation: fresh Haiku reads the diff only. Logged in logs/feat_*."""
import json, os, sys, difflib, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
P = """Below is a unified diff between two consecutive versions of a small HTML arcade game. Read ONLY the diff. List the player-visible features/mechanics ADDED and REMOVED (plain text, one short line each; ignore refactors). Then answer with a final line exactly: COUNTS added=<int> removed=<int>

{diff}"""
out = {}
def run(m, g):
    a = open(f"{gen.JEUX}/r2_{m}_g{g-1:02d}/index.html").read().splitlines(); b = open(f"{gen.JEUX}/r2_{m}_g{g:02d}/index.html").read().splitlines()
    diff = "\n".join(difflib.unified_diff(a, b, lineterm="", n=1))[:120000]
    if not diff: out[f"{m}_{g}"] = {"added": 0, "removed": 0, "text": "identical file"}; return
    t, _ = gen.claude("haiku", P.format(diff=diff), f"feat_{m}_g{g:02d}", tools="")
    import re; mm = re.search(r"COUNTS added=(\d+) removed=(\d+)", t)
    out[f"{m}_{g}"] = {"added": int(mm.group(1)) if mm else None, "removed": int(mm.group(2)) if mm else None, "text": t}
ts = []
for m in gen.MODELS:
    def seq(m=m):
        for g in range(1, 11): run(m, g)
    ts.append(threading.Thread(target=seq))
[t.start() for t in ts]; [t.join() for t in ts]
json.dump(out, open(f"{gen.HERE}/features_r2.json", "w"), indent=1)
for k, v in out.items(): print(k, v["added"], v["removed"])
