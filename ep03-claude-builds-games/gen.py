#!/usr/bin/env python3
"""Episode 3 driver. `gen.py r1` runs Round 1 (3 attempts x 3 models) + playtests. `gen.py r2` runs Round 2 (10 generations per model).
Everything via `claude -p` (subscription). Every prompt + raw JSON response is logged verbatim in logs/."""
import json, os, re, subprocess, sys, time, threading, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LOGS = f"{HERE}/logs"; JEUX = f"{ROOT}/jeux"; os.makedirs(LOGS, exist_ok=True); os.makedirs(JEUX, exist_ok=True)
MODELS = ["opus", "sonnet", "haiku"]
SYSTEM = "You are Claude, an AI assistant made by Anthropic."
BRIEF = open(f"{HERE}/brief.txt").read()
GENS = int(os.environ.get("GENS", "10"))

def claude(model, prompt, tag, tools="", cwd="/tmp"):
    """Returns (text, meta). Logs prompt and raw response. Retries on rate limit / errors."""
    pf = f"{LOGS}/{tag}.prompt.txt"; rf = f"{LOGS}/{tag}.response.json"
    if os.path.exists(rf):
        d = json.load(open(rf)); return d.get("result", ""), d
    open(pf, "w").write(prompt)
    for essai in range(60):
        t = time.time()
        cmd = ["claude", "-p", "--model", model, "--system-prompt", SYSTEM, "--tools", tools, "--strict-mcp-config",
               "--setting-sources", "", "--no-session-persistence", "--exclude-dynamic-system-prompt-sections", "--output-format", "json"]
        if tools: cmd += ["--allowedTools", tools]
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=1800, cwd=cwd)
            d = json.loads(r.stdout)
            d["_wall_seconds"] = time.time() - t
            if not d.get("is_error") and d.get("result"):
                json.dump(d, open(rf, "w"), indent=1); return d["result"], d
            open(f"{LOGS}/{tag}.error{essai}.json", "w").write(r.stdout + "\n" + r.stderr)
        except Exception as e:
            open(f"{LOGS}/{tag}.error{essai}.txt", "w").write(repr(e))
        time.sleep(120)
    raise RuntimeError("claude failed: " + tag)

def extract_html(text):
    m = re.findall(r"```html\s*\n(.*?)```", text, re.S)
    if m: return max(m, key=len)
    m = re.search(r"(<!DOCTYPE html.*</html>)", text, re.S | re.I)
    return m.group(1) if m else None

def playtest(html, out):
    if os.path.exists(f"{out}/report.json"): return json.load(open(f"{out}/report.json"))
    subprocess.run(["node", f"{HERE}/playtest.js", html, out, "--video"], capture_output=True, text=True, timeout=400)
    return json.load(open(f"{out}/report.json")) if os.path.exists(f"{out}/report.json") else {"total": 0, "error": "playtest crashed"}

def r1_one(model, k):
    d = f"{JEUX}/r1_{model}_{k}"; os.makedirs(d, exist_ok=True)
    text, meta = claude(model, BRIEF, f"r1_{model}_{k}")
    html = extract_html(text)
    if html: open(f"{d}/index.html", "w").write(html)
    json.dump({"model": model, "attempt": k, "seconds": meta.get("_wall_seconds"), "usage": meta.get("usage"), "has_html": bool(html),
               "response_chars": len(text)}, open(f"{d}/meta.json", "w"), indent=1)
    if html: playtest(f"{d}/index.html", f"{d}/test")

def r1():
    def run(model):
        for k in (1, 2, 3):
            try: r1_one(model, k)
            except Exception as e: print("R1 fail", model, k, e, flush=True)
    ts = [threading.Thread(target=run, args=(m,)) for m in MODELS]
    [t.start() for t in ts]; [t.join() for t in ts]
    # selection rule (pre-registered)
    sel = {}
    for m in MODELS:
        c = []
        for k in (1, 2, 3):
            f = f"{JEUX}/r1_{m}_{k}/test/report.json"
            if os.path.exists(f):
                r = json.load(open(f)); c.append((-r["total"], r.get("error_count", 99), k))
        if c: sel[m] = sorted(c)[0][2]
    json.dump(sel, open(f"{HERE}/selection_r1.json", "w")); print("selection", sel)

R2 = """You are the developer of a small arcade game, a single self-contained HTML file. The original brief was:

--- BRIEF ---
{brief}
--- END BRIEF ---

Below is the CURRENT version of the game, followed by the report of an automated playtest (a scripted bot with random inputs played it for 60 seconds, then stayed idle in a second run). The bot is not smart: it only tells you whether the game loads, reacts to input, scores, can be lost and restarted. Screenshots of the playtest are in the current folder: menu.png, f01.png, f03.png, f05.png, end.png (when they exist). Look at them with the Read tool before writing your notes.

--- CURRENT CODE ---
{code}
--- END CODE ---

--- PLAYTEST REPORT (JSON) ---
{report}
--- END REPORT ---

Your job, in this order:
1. PLAYTEST NOTES: write 5 to 15 short lines: what works, what is broken, what feels bad or boring. Be honest and specific.
2. Improve the game. You decide what "better" means: make it the best game you can. You may change anything, but keep it a single self-contained HTML file with no external assets, keep the window.gameState test hook up to date, and do not break what already works.
3. Output the COMPLETE updated file in a single ```html code block, after your notes.
"""

def r2_model(model):
    sel = json.load(open(f"{HERE}/selection_r1.json"))
    cur = f"{JEUX}/r2_{model}_g00"; os.makedirs(cur, exist_ok=True)
    src = f"{JEUX}/r1_{model}_{sel[model]}"
    if not os.path.exists(f"{cur}/index.html"):
        shutil.copy(f"{src}/index.html", f"{cur}/index.html"); shutil.copytree(f"{src}/test", f"{cur}/test", dirs_exist_ok=True)
    last_ok = cur; crashes = 0
    for g in range(1, GENS + 1):
        nxt = f"{JEUX}/r2_{model}_g{g:02d}"; os.makedirs(nxt, exist_ok=True)
        base = last_ok if crashes >= 2 else f"{JEUX}/r2_{model}_g{g-1:02d}"
        rep = json.load(open(f"{base}/test/report.json"))
        work = f"{nxt}/_in"; os.makedirs(work, exist_ok=True)
        for n in ("menu", "f01", "f03", "f05", "end"):
            if os.path.exists(f"{base}/test/{n}.png"): shutil.copy(f"{base}/test/{n}.png", f"{work}/{n}.png")
        compact = {k: rep.get(k) for k in ("points", "total", "bot", "idle", "error_count", "errors", "rAF_5s", "bytes", "lines", "notes")}
        prompt = R2.format(brief=BRIEF, code=open(f"{base}/index.html").read(), report=json.dumps(compact, indent=1))
        text, meta = claude(model, prompt, f"r2_{model}_g{g:02d}", tools="Read", cwd=work)
        html = extract_html(text)
        notes = text.split("```html")[0].strip()
        open(f"{nxt}/notes.txt", "w").write(notes)
        json.dump({"model": model, "gen": g, "seconds": meta.get("_wall_seconds"), "usage": meta.get("usage"), "has_html": bool(html),
                   "based_on": os.path.basename(base)}, open(f"{nxt}/meta.json", "w"), indent=1)
        if not html:
            html = open(f"{base}/index.html").read(); open(f"{nxt}/NO_HTML_RETURNED", "w").write("kept previous")
        open(f"{nxt}/index.html", "w").write(html)
        r = playtest(f"{nxt}/index.html", f"{nxt}/test")
        crashed = r.get("points", {}).get("P1_loads", 0) == 0
        crashes = crashes + 1 if crashed else 0
        if not crashed: last_ok = nxt
        print(model, "gen", g, "points", r.get("total"), "bytes", r.get("bytes"), flush=True)

def r2():
    ts = [threading.Thread(target=r2_model, args=(m,)) for m in MODELS]
    [t.start() for t in ts]; [t.join() for t in ts]

if __name__ == "__main__":
    {"r1": r1, "r2": r2}[sys.argv[1]]()
