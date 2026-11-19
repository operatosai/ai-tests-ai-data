# Episode 2: One AI Robbed Its Partner 19 Times in a Row

Video: __LIEN_VIDEO__

Three AIs played a repeated prisoner's dilemma ("SHARE or STEAL") against each other and against copies of themselves.
**14,160 decisions** in total, every one of them here: 1,200 are the moves of two fixed robots, the other 12,960 were made by the AIs, each with the one-sentence reason it gave. 0 unreadable answers.

## The players

| Name in the data | What it is |
|---|---|
| `claude` | Claude Sonnet 5.5 (Anthropic), called through the Claude Code CLI with no tools and no memory. System prompt: *"You are Claude, an AI assistant made by Anthropic."* |
| `hermes` | **The same model** (Claude Sonnet 5.5) with a short identity prompt: our creator's personal assistant, Hermes. Only the name and personality differ. The creator's name is replaced by `[our creator]` in `experiment.py`. |
| `hermes3` | Hermes 3 (Nous Research, 8B), run locally with Ollama on our own PC. Much smaller than the other two. |
| `robot-pardon` | A fixed script, not an AI: steals in round 1, then shares forever. |
| `robot-donnant` | A fixed script, not an AI: tit for tat (shares in round 1, then copies the other player's last move). Not shown in the video. |

## The rules

Each round both players choose at the same time, with no talking:

| | They SHARE | They STEAL |
|---|---|---|
| **You SHARE** | 3 / 3 | 0 / 5 |
| **You STEAL** | 5 / 0 | 1 / 1 |

20 rounds per game. Each player sees the full history and the score before choosing.
Answer format: line 1 = one word (SHARE or STEAL), line 2 = one short sentence saying why.

## The files (`games/`)

| File | What changed | Decisions |
|---|---|---|
| `A_tournoi.jsonl` | Main tournament, game called "the Game". 6 pairings (3 duels + 3 mirror games) × 10 games. | 2,400 |
| `B_community.jsonl` | Same, game called "the Community Game". | 2,400 |
| `B_wallstreet.jsonl` | Same, game called "the Wall Street Game". | 2,400 |
| `C_pardon.jsonl` | Each AI against the two robots, 10 games each (robot moves are included as lines). | 2,400 |
| `D_fin_annoncee.jsonl` | Same as A, but before round 20 the players are told "this is the last round". | 2,400 |
| `A_relance1-3.jsonl` | Main tournament re-run 3 more times (3 games per pairing). | 3 × 720 |

One line per decision: `jeu` (game name), `duel`, `tour` (round), `joueur` (side), `modele`, `adversaire`, `fin_annoncee`, `choix`, `raison`, `brut` (raw answer), `points`.

- `experiment.py`: the script that ran the games (comments in French, logic unchanged).
- `analysis.py`: the script that counts everything below. Run `python analysis.py games`.

## Main results (from `analysis.py`)

| | Steal rate | Points per game |
|---|---|---|
| claude | 21.0 % | 50.1 |
| hermes | 21.1 % | 50.1 |
| hermes3 | 92.8 % | 27.3 (last) |

- Head to head, Hermes 3 beats Claude 30.6 to 20.6 points per game, and Hermes 30.3 to 20.3.
- Mirror games: two Claudes share every round (60 points each); two Hermes 3s get about 24 each.
- Game name: Claude 19.6 % (Community) vs 21.0 % (Wall Street); Hermes 3 88.6 % vs 93.0 %.
- Last round announced: Claude and Hermes steal in round 20 in 100 % of games.
- The 3 re-runs gave the same picture.

## Limits (so you can judge it)

- `claude` and `hermes` are the same model. Of course they played the same.
- Hermes 3 is a small local model against a large cloud model. Not a fair fight.
- Claude's games are very similar to each other: 10 games are close to one story told 10 times.
- Runs were made on November 14, 2026. Claude and Hermes: Claude Code CLI, `--effort low`. Hermes 3: Ollama, temperature 0.8, 60 tokens max.

The human study quoted in the video: Liberman, Samuels & Ross (2004), "The Name of the Game", *Personality and Social Psychology Bulletin* 30(9), 1175-1185, doi:10.1177/0146167204264004.
