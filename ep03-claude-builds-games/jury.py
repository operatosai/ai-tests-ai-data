#!/usr/bin/env python3
"""Blind jury: fresh Sonnet instances see only a contact sheet (8 frames of bot gameplay) per game, random ids, 3 jurors x random batch order.
usage: jury.py <name> <game_dir1> <game_dir2> ... ; writes jury_<name>.json (id map + all scores). Prompts/responses logged in logs/."""
import json, os, random, re, subprocess, sys, shutil, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen
name, dirs = sys.argv[1], sys.argv[2:]
rnd = random.Random(2026)
ids = {}; pool = list(range(10, 99)); rnd.shuffle(pool)
work = f"{gen.HERE}/jury_{name}_files"; os.makedirs(work, exist_ok=True)
for d in dirs:
    gid = f"G{pool.pop()}"; ids[gid] = d
    t = f"{d}/test"; frames = [f"{t}/f{i:02d}.png" for i in range(8)]
    sheet = f"{work}/{gid}.png"
    if not os.path.exists(sheet):
        have = [f for f in frames if os.path.exists(f)]
        if not have: continue
        while len(have) < 8: have.append(have[-1])
        cmd = ["ffmpeg", "-y", "-loglevel", "error"] + sum([["-i", f] for f in have], []) + ["-filter_complex",
               "".join(f"[{i}:v]scale=480:270[s{i}];" for i in range(8)) + "".join(f"[s{i}]" for i in range(8)) + "xstack=inputs=8:layout=0_0|480_0|960_0|1440_0|0_270|480_270|960_270|1440_270[o]", "-map", "[o]", sheet]
        subprocess.run(cmd, check=True)
json.dump(ids, open(f"{gen.HERE}/jury_{name}_ids.json", "w"), indent=1)
P = """You are a member of a blind jury for small arcade games made as a single HTML file (theme: collect glowing orbs, avoid hazards, harder over time). You see, for each game, ONE contact sheet: 8 screenshots in reading order (left to right, top to bottom) taken every 7.5 seconds while a dumb bot played for 60 seconds, so the first frame is the title screen. You do not know who or what made the games. Judge only what you see. Games may look broken or empty: if so, score it low.

Read each sheet with the Read tool, then score every game from 1 to 10 on:
- clarity: is it clear what the game is and what to do
- polish: visual quality and coherence
- feel: sense of game feel (feedback, effects, readable action)
- depth: variety, progression, things happening over time
- appeal: would you want to play it again

Games to judge (files in the current folder): {games}

Answer with ONLY a JSON object: {{"G12": {{"clarity": 7, "polish": 6, "feel": 5, "depth": 4, "appeal": 5}}, ...}} for every game, nothing else."""
games = list(ids)
def juror(j):
    order = games[:]; random.Random(100 + j).shuffle(order)
    out = []
    for b in range(0, len(order), 7):
        chunk = order[b:b + 7]
        text, _ = gen.claude("sonnet", P.format(games=", ".join(f"{g}.png" for g in chunk)), f"jury_{name}_j{j}_b{b//7}", tools="Read", cwd=work)
        m = re.search(r"\{.*\}", text, re.S)
        try: out.append(json.loads(m.group(0)))
        except Exception: out.append({"_unparsed": text})
    json.dump(out, open(f"{gen.HERE}/jury_{name}_j{j}.json", "w"), indent=1)
ts = [threading.Thread(target=juror, args=(j,)) for j in (1, 2, 3)]
[t.start() for t in ts]; [t.join() for t in ts]
# aggregate
sc = {g: [] for g in games}
for j in (1, 2, 3):
    for part in json.load(open(f"{gen.HERE}/jury_{name}_j{j}.json")):
        for g, v in part.items():
            if g in sc and isinstance(v, dict) and len(v) >= 5: sc[g].append(sum(v.values()) / len(v))
res = {ids[g]: {"id": g, "jury": (sum(v) / len(v) if v else None), "n": len(v)} for g, v in sc.items()}
json.dump(res, open(f"{gen.HERE}/jury_{name}.json", "w"), indent=1)
for d, r in res.items(): print(os.path.basename(d), r)
