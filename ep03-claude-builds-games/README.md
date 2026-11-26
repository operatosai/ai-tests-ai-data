# Episode 3: Claude Models Build Video Games

Video: __LIEN_VIDEO__

Claude Opus, Sonnet and Haiku (5.5 family) got the same brief (`brief.txt`): one self-contained HTML arcade game about collecting glowing orbs.
- **Round 1:** 3 attempts per model (9 games).
- **Round 2:** each model improved its own best game for 10 generations (gen 0 to gen 10, 33 games).

Everything was run with the Claude Code CLI (`claude -p`, subscription access, no API key, no other vendor), November 22-25, 2026.

## The files

| Path | What it is |
|---|---|
| `PREREGISTRATION.md` | The protocol, written before the first run. Deviations are dated at the end. |
| `RESULTATS.md` | All results and caveats, generated from the logged data. |
| `brief.txt` | The game request given to every model. |
| `games/<round>_<model>_<n>/index.html` | Every game, exactly as the model wrote it. Open it in a browser to play. |
| `games/.../meta.json`, `notes.txt` | Generation time, token usage, which version it was based on, the model's change notes. |
| `jury/` | Blind jury scores (3 fresh Claude jurors per game, random IDs, never the model name). |
| `logs/` | Every prompt and every raw answer, verbatim. |
| `gen.py`, `jury.py`, `playtest.js`, `features.py` | The scripts used (playtest needs `playwright-core`). |

## Read this before drawing conclusions
- One lineage per model in Round 2; n=3 in Round 1. Descriptive numbers only, no statistical test.
- Jury noise is about ±1.3 points. Only Opus's gain (5.1 → 7.8) clearly exceeds it.
- The jurors are Claude too (same-family bias), and they see only frames, not how a game feels.
- The playtest robot presses random keys and passed every version, so it cannot tell good from better.
