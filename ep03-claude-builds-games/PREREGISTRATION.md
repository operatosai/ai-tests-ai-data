# Pre-registration, episode 3 "Claude models build video games" (written 2026-11-22, BEFORE any run)

Question: when Opus, Sonnet and Haiku (Claude 5.5 family, subscription CLI `claude -p`, 0 USD, no API key, no other vendor) get the same game brief, how do their games differ, and what happens when each model improves its own game for 10 generations?

## Setup
- Models: `--model opus` (claude-opus-5-5), `sonnet` (claude-sonnet-5-5), `haiku` (claude-haiku-5-5). Default effort. No tools for Round 1 (the model answers with the file as text). Round 2 gives only the Read tool (to look at screenshots).
- Every prompt and every raw response is stored verbatim (logs/*.json). Nothing is edited by hand.
- Brief (identical for all, Round 1): `brief.txt`. One theme: collect glowing orbs, avoid hazards, harder over time. One self-contained HTML file, no external assets/network. Required test hook `window.gameState = {score:number, state:"menu"|"playing"|"over"|"won"}` kept up to date (same for all models; a test hook, not a game feature).

## Round 1 "Big vs small"
3 independent attempts per model (9 games), fresh process each, no shared memory.

## Round 2 "Evolution"
Selection rule (fixed now): per model, the Round 1 game with the highest automated playtest points (see below); ties broken by lower console-error count, then lower attempt number. Then 10 generations (gen 1..10). At each generation a FRESH instance of the same model receives: the full current code, the automated playtest report of that code (metrics + console errors + paths to 4 screenshots it may Read), and the instruction to (1) write short playtest notes, (2) return an improved full file. The model chooses what "better" means. No size limit given. All generations kept (gen0 = Round 1 winner). If a generation fails to load (crash), it is KEPT and counted as a regression; the next generation still receives it with the error report (no rollback), unless 2 crashes in a row, then the last working version is passed on and the crash is logged.

## Automated playtest (Playwright, Chromium headless 1280x720), per game
P1 loads without exception within 5 s (1 pt). P2 zero console errors/page errors during 60 s (1 pt). P3 renders non-blank canvas/DOM (1 pt). P4 input response: a scripted bot (seeded random arrows/WASD/space/mouse for 40 s, pressing Enter/Space/click to start) changes the screen (pixel difference between frames) (1 pt). P5 score changes (gameState.score changes) under bot play (1 pt). P6 can lose: gameState.state reaches "over" in 60 s of bot play OR 45 s idle (1 pt). P7 restart works: after "over", Enter/Space/click returns to "playing" with score reset (1 pt). P8 hook present and valid (1 pt). Max 8 points. Also logged: code size (bytes, lines), time of the model call, response tokens, console error list, whether "won" is ever reached, frame-rate proxy (rAF count in 5 s).
Features per generation: counted by a fresh Haiku call reading the diff only (list of added/removed features, plain text) = exploratory, marked as such. Regression = a playtest point lost vs the previous generation, or a feature the notes say worked that is gone.

## Blind jury (fun/quality)
Jurors are fresh Sonnet instances; they see only a contact sheet of 8 frames of bot gameplay plus a one-line static description-free label (game id like "G17", random), never the model name, generation order or code. Rubric, 1 to 10 each: clarity (is it clear what to do), visual polish, game feel/juice, depth/variety, replay appeal. Each game is scored by 3 jurors in 3 different random batch orders; jury score = mean of the 5 criteria averaged over jurors. Limitation stated in advance: the jurors are Claude too (same-family bias), and frames can't show feel in motion. our creator is final judge by playing (page `jouer/`).

## Main metrics reported
crash/load rate per model; mean playtest points per model (Round 1); jury score per model (Round 1); Round 2: playtest points and jury score by generation, code size by generation, regressions, time per generation, features added. Headline number and title chosen AFTER the data. No statistical test beyond descriptive numbers and the min/max across attempts (n=3 is small: said openly).

## Deviations
Any change to this protocol after runs begin will be appended below with a date and reason, never edited above.
- 2026-11-22: network (DNS) outage at Round 2 start; driver retry loop lengthened (60 tries x 2 min). No protocol change.
- 2026-11-25: the Round 2 attempt of 2026-11-22/23 failed at generation 01 for all three models (logs/r2_*_g01.error*.json, terminal_reason api_error, 0 tokens, plus r2.out) because of the network outage. These are infrastructure failures, NOT model crashes in the sense of the protocol: they are not counted as crashes or regressions, and the generation-01 prompts are simply re-sent unchanged. Round 2 resumes from gen00 (no generation had been produced). The failed-attempt logs are kept. Retry policy during the resume: if the network fails again, the driver waits and retries (wrapper run_r2_loop.sh re-launches gen.py r2, which skips every generation whose response is already logged); API-error retries are never counted as failures. No change to prompts, selection rule, playtest or jury.
- 2026-11-25 (second note): the Round 1 jury had no recorded responses (only the prompts in logs/jury_r1_*.prompt.txt), so it was run with jury.py with the same blind ids, contact sheets and rubric. The Round 2 jury (33 games, gen 0 included as a separate blind game) shows n=2 jurors on some games because a juror omitted them in its answer; they are kept as is. Features per generation were counted with features.py (fresh Haiku reading the diff only, exploratory as announced).
