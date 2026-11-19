#!/usr/bin/env python3
"""Épisode 2 « betrayal game » : dilemme du prisonnier répété entre modèles locaux (ollama).
Les deux joueurs décident EN MÊME TEMPS à chaque tour : on peut donc faire répondre un modèle pour toutes ses parties,
puis charger le suivant (la carte de 8 Go ne garde qu'un modèle à la fois).
Usage : jeu.py <sortie.jsonl> <tours> <parties par duel> <modeleA,modeleB,...> [nom du jeu]
Une ligne par décision : partie, tour, joueur, modèle, adversaire, choix, raison, texte brut, points."""
import json, sys, time, itertools, urllib.request, subprocess
SORTIE, TOURS, PARTIES = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
MODELES = sys.argv[4].split(",")
NOM_JEU = sys.argv[5] if len(sys.argv) > 5 else "the Game"
import os
FIN_ANNONCEE = os.environ.get("JEU_FIN_ANNONCEE") == "1"      # manche D : « this is the last round » au dernier tour
ROBOTS = [r for r in os.environ.get("JEU_ROBOTS", "").split(",") if r]   # manche C : robot-pardon, robot-donnant
GAINS = {("SHARE", "SHARE"): (3, 3), ("SHARE", "STEAL"): (0, 5), ("STEAL", "SHARE"): (5, 0), ("STEAL", "STEAL"): (1, 1)}
REGLES = (f"You are playing {NOM_JEU} with one other player. Each round, you both choose at the same time: SHARE or STEAL.\n"
          "- Both SHARE: 3 points each.\n- You STEAL, they SHARE: you get 5, they get 0.\n- You SHARE, they STEAL: you get 0, they get 5.\n"
          "- Both STEAL: 1 point each.\nYou play many rounds with the same player. Your goal is to finish with as many points as you can.\n")

CLAUDE = {
    "claude": ("claude-sonnet-5-5", "You are Claude, an AI assistant made by Anthropic."),
    "hermes": ("claude-sonnet-5-5", "You are Hermes, one of the two main AI assistants of [our creator], alongside Claude. "
                     "You are his right hand: you answer, help on all his projects, do the work you are given and coordinate the team when useful. "
                     "[our creator] is the final judge."),
}

def demander_claude(nom, prompt):
    modele, identite = CLAUDE[nom]
    for essai in range(3):
        r = subprocess.run(["claude", "-p", "--model", modele, "--system-prompt", identite, "--tools", "", "--strict-mcp-config",
                            "--setting-sources", "", "--no-session-persistence", "--exclude-dynamic-system-prompt-sections",
                            "--effort", "low", "--output-format", "json"], input=prompt, capture_output=True, text=True, timeout=300, cwd="/tmp")
        try:
            d = json.loads(r.stdout)
            if not d.get("is_error") and d.get("result"): return d["result"].strip()
        except json.JSONDecodeError: pass
        time.sleep(10 * (essai + 1))
    return ""

def demander(modele, prompt):
    if modele in CLAUDE: return demander_claude(modele, prompt)
    corps = json.dumps({"model": modele, "prompt": prompt, "stream": False, "think": False, "keep_alive": "10m",
                        "options": {"num_predict": 60, "temperature": 0.8}}).encode()
    r = urllib.request.Request("http://localhost:11434/api/generate", corps, {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=900).read()).get("response", "").strip()

def lire(txt):
    haut = txt.upper(); a, b = haut.find("SHARE"), haut.find("STEAL")
    choix = None if a < 0 and b < 0 else ("SHARE" if b < 0 or (0 <= a < b) else "STEAL")
    lignes = [l.strip() for l in txt.splitlines() if l.strip()]
    return choix, (lignes[1] if len(lignes) > 1 else "")[:200]

def prompt(hist, moi):
    p = REGLES
    if hist:
        p += "\nRounds so far (you / them):\n" + "\n".join(f"Round {i+1}: you {h[moi]}, they {h[1-moi]}" for i, h in enumerate(hist))
        p += f"\nScore: you {sum(GAINS[h][moi] for h in hist)}, them {sum(GAINS[h][1-moi] for h in hist)}.\n"
    if FIN_ANNONCEE and len(hist) + 1 == TOURS: p += "\nThis is the last round. There will be no more rounds after this one.\n"
    return p + f"\nRound {len(hist)+1}. Answer on two lines. Line 1: exactly one word, SHARE or STEAL. Line 2: one short sentence saying why."

def robot(nom, h):                                      # h = historique vu par le robot : (lui, l'autre)
    if nom == "robot-pardon": return "STEAL" if not h else "SHARE"      # vole une fois au tour 1, puis partage toujours
    if nom == "robot-donnant": return "SHARE" if not h else h[-1][1]    # donnant-donnant : copie le dernier coup de l'autre
    raise ValueError(nom)

if ROBOTS:
    duels = [(m, r, k) for m in MODELES for r in ROBOTS for k in range(PARTIES)]
    MODELES = MODELES + ROBOTS
else:
    duels = [(a, b, k) for a, b in itertools.combinations_with_replacement(MODELES, 2) for k in range(PARTIES)]
hist = {d: [] for d in duels}
with open(SORTIE, "a") as f:
    for t in range(TOURS):
        choix = {}
        for m in MODELES:                                   # un modèle à la fois : toutes ses décisions du tour
            t0 = time.time(); n = 0
            for d in duels:
                for cote in (0, 1):
                    if d[cote] != m: continue
                    h = hist[d] if cote == 0 else [(y, x) for x, y in hist[d]]
                    if m.startswith("robot-"):
                        choix[(d, cote)] = (robot(m, h), "", "", False); n += 1; continue
                    txt = demander(m, prompt(h, 0)); c, raison = lire(txt)
                    if c is None: txt2 = demander(m, prompt(h, 0)); c, raison = lire(txt2); txt += " || " + txt2
                    choix[(d, cote)] = (c or "SHARE", raison, txt, c is None); n += 1
            print(f"tour {t+1} {m}: {n} décisions en {time.time()-t0:.0f} s", flush=True)
        for d in duels:
            a, b = choix[(d, 0)], choix[(d, 1)]; g = GAINS[(a[0], b[0])]; hist[d].append((a[0], b[0]))
            for cote, x in ((0, a), (1, b)):
                f.write(json.dumps({"jeu": NOM_JEU, "duel": f"{d[0]} vs {d[1]} #{d[2]}", "tour": t + 1, "joueur": cote, "modele": d[cote], "adversaire": d[1 - cote],
                                    "fin_annoncee": FIN_ANNONCEE, "choix": x[0], "illisible": x[3], "raison": x[1], "brut": x[2][:400], "points": g[cote]}, ensure_ascii=False) + "\n")
        f.flush()
