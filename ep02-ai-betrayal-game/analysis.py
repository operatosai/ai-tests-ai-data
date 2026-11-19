#!/usr/bin/env python3
"""Compte les manches de l'épisode 2 (règles de PLAN.md). Usage : analyse.py [dossier]"""
import json, sys, collections, statistics as st
D = sys.argv[1] if len(sys.argv) > 1 else "games"

def charger(n):
    parties = collections.defaultdict(dict)  # duel -> {(tour, joueur): rec}
    for l in open(f"{D}/{n}.jsonl"):
        r = json.loads(l); parties[r["duel"]][(r["tour"], r["joueur"])] = r
    return parties

def resume(n, detail=True):
    P = charger(n)
    vol = collections.defaultdict(lambda: [0, 0]); vol_adv = collections.defaultdict(lambda: [0, 0])
    pts = collections.defaultdict(list); pts_adv = collections.defaultdict(list)
    illi = collections.Counter(); ranc = collections.defaultdict(lambda: [0, 0]); pardon = collections.defaultdict(list)
    dernier = collections.defaultdict(lambda: [0, 0]); avant = collections.defaultdict(lambda: [0, 0]); premier = collections.defaultdict(lambda: [0, 0])
    T = max(t for p in P.values() for (t, _) in p)
    for duel, p in P.items():
        for j in (0, 1):
            m = p[(1, j)]["modele"]; a = p[(1, j)]["adversaire"]
            ch = [p[(t, j)]["choix"] for t in range(1, T + 1)]; cha = [p[(t, 1 - j)]["choix"] for t in range(1, T + 1)]
            illi[m] += sum(p[(t, j)]["illisible"] for t in range(1, T + 1))
            s = sum(c == "STEAL" for c in ch)
            vol[m][0] += s; vol[m][1] += T; vol_adv[(m, a)][0] += s; vol_adv[(m, a)][1] += T
            tot = sum(p[(t, j)]["points"] for t in range(1, T + 1)); pts[m].append(tot); pts_adv[(m, a)].append(tot)
            dernier[m][0] += ch[-1] == "STEAL"; dernier[m][1] += 1
            avant[m][0] += sum(c == "STEAL" for c in ch[-4:-1]); avant[m][1] += 3
            premier[m][0] += ch[0] == "STEAL"; premier[m][1] += 1
            # rancune / pardon : à chaque vol de l'adversaire au tour t (t <= T-10), est-ce que je ne partage plus jamais pendant 10 tours ?
            for t in range(T):
                if cha[t] == "STEAL" and (t == 0 or cha[t - 1] != "STEAL"):
                    suite = ch[t + 1:t + 11]
                    if len(suite) == 10:
                        ranc[m][1] += 1; ranc[m][0] += all(c == "STEAL" for c in suite)
                    k = next((i for i, c in enumerate(ch[t + 1:], 1) if c == "SHARE"), None)
                    pardon[m].append(k)
    pc = lambda x: f"{100 * x[0] / x[1]:.1f} %" if x[1] else "—"
    out = {"nom": n, "tours": T, "parties": len(P)}
    print(f"\n=== {n}  ({len(P)} parties × {T} tours) ===")
    for m in sorted(vol):
        pk = [k for k in pardon[m] if k is not None]
        print(f"{m:13} vol {pc(vol[m]):>7} | 1er tour {pc(premier[m]):>7} | 3 avant-derniers {pc(avant[m]):>7} | dernier {pc(dernier[m]):>7} | pts/partie {st.mean(pts[m]):5.1f} | rancunier {ranc[m][0]}/{ranc[m][1]} | revient au partage {len(pk)}/{len(pardon[m])} (délai médian {st.median(pk) if pk else '—'}) | illisibles {illi[m]}")
    if detail:
        for (m, a) in sorted(vol_adv):
            print(f"   {m:13} contre {a:13} vol {pc(vol_adv[(m, a)]):>7}  pts/partie {st.mean(pts_adv[(m, a)]):5.1f}")
    return vol, pts, vol_adv, pts_adv

for n in ["A_tournoi", "D_fin_annoncee", "B_community", "B_wallstreet", "C_pardon", "A_relance1", "A_relance2", "A_relance3"]:
    resume(n)
