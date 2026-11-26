# Episode 3 results: Claude models build video games

Generated 2026-11-25 from the logged data (protocol: PREREGISTRATION.md; deviations listed at its end and recalled here). Subscription `claude -p` only, 0 USD. n=3 per model in Round 1, one lineage per model in Round 2: descriptive numbers only, no statistical test.

## Round 1: big vs small (3 attempts per model)

| model | load failures | mean playtest pts (/8) | min-max pts | mean jury (/10) | min-max jury | mean bytes | mean lines | mean call time s | mean output tokens |
|---|---|---|---|---|---|---|---|---|---|
| opus | 1/3 | 5.67 | 2-8 | 3.91 | 1.07-6.40 | 16897 | 406 | 83 | 9005 |
| sonnet | 0/3 | 8.00 | 8-8 | 4.82 | 4.73-4.93 | 9306 | 253 | 39 | 4979 |
| haiku | 0/3 | 7.67 | 7-8 | 5.67 | 5.27-6.20 | 17307 | 572 | 105 | 24463 |

Per game:

| game | pts | console errors | bytes | jury | note |
|---|---|---|---|---|---|
| r1_opus_1 | 2 | 1 | 20722 | 1.07 | failed: P1_loads, P2_no_console_errors, P4_input_changes_screen, P5_score_changes, P7_restart_works, P6_can_lose |
| r1_opus_2 | 8 | 0 | 15160 | 6.40 |  |
| r1_opus_3 | 7 | 0 | 14808 | 4.27 | failed: P5_score_changes |
| r1_sonnet_1 | 8 | 0 | 9874 | 4.80 |  |
| r1_sonnet_2 | 8 | 0 | 8272 | 4.93 |  |
| r1_sonnet_3 | 8 | 0 | 9772 | 4.73 |  |
| r1_haiku_1 | 8 | 0 | 18850 | 5.53 |  |
| r1_haiku_2 | 7 | 2 | 14686 | 5.27 | failed: P2_no_console_errors |
| r1_haiku_3 | 8 | 0 | 18385 | 6.20 |  |

Selection (pre-registered rule): opus attempt 2, sonnet attempt 1, haiku attempt 1. Note: sonnet attempts 1-3 and haiku 1 and 3 all tie at 8 pts with 0 errors, so lowest attempt number decided. No game reached the "won" state under the bot in Round 1.

Finding: the biggest model produced both the best-judged Round 1 game (opus_2, 6.40) and the only game that did not load at all (opus_1, jury 1.07, a pageerror on `.length` of undefined). Sonnet was the most consistent but also the shortest and plainest.

## Round 2: 10 generations of self-improvement (gen0 = Round 1 winner)

Playtest points: **8/8 for every one of the 33 versions, 0 console errors, 0 load failures, 0 NO_HTML_RETURNED**. The automated playtest saturates at the ceiling from gen0, so it cannot show improvement or regression; the jury, size and features carry the signal.

### Jury score by generation (blind, mean of 3 sonnet jurors x 5 criteria; some games scored by 2 jurors because a juror skipped them, n shown in jury_r2.json)

| gen | opus | sonnet | haiku |
|---|---|---|---|
| 0 | 5.13 | 4.13 | 4.80 |
| 1 | 5.80 | 4.67 | 5.67 |
| 2 | 7.27 | 4.60 | 6.33 |
| 3 | 6.93 | 4.67 | 5.87 |
| 4 | 7.40 | 5.00 | 5.30 |
| 5 | 7.20 | 4.90 | 5.70 |
| 6 | 7.07 | 5.40 | 5.60 |
| 7 | 7.67 | 5.07 | 5.90 |
| 8 | 6.80 | 5.20 | 5.67 |
| 9 | 7.47 | 5.90 | 4.93 |
| 10 | 7.80 | 5.30 | 5.87 |

### Code size by generation (bytes / lines)

| gen | opus | sonnet | haiku |
|---|---|---|---|
| 0 | 15160 / 382 | 9874 / 250 | 18850 / 617 |
| 1 | 23653 / 559 | 13756 / 325 | 23953 / 744 |
| 2 | 30295 / 710 | 15144 / 350 | 25578 / 782 |
| 3 | 31753 / 737 | 16545 / 372 | 30155 / 901 |
| 4 | 33504 / 768 | 17005 / 383 | 31050 / 914 |
| 5 | 38199 / 866 | 17653 / 397 | 32120 / 945 |
| 6 | 39537 / 892 | 17653 / 397 | 32786 / 958 |
| 7 | 42430 / 951 | 17678 / 397 | 33947 / 988 |
| 8 | 44932 / 1006 | 18044 / 403 | 34856 / 1005 |
| 9 | 45515 / 1015 | 18013 / 404 | 35708 / 1016 |
| 10 | 46710 / 1039 | 18300 / 410 | 36285 / 1029 |

### Time per generation (s) and output tokens

| gen | opus | sonnet | haiku |
|---|---|---|---|
| 1 | 121 s / 15409 | 47 s / 8440 | 94 s / 24811 |
| 2 | 174 s / 22204 | 45 s / 8919 | 70 s / 19906 |
| 3 | 145 s / 20086 | 55 s / 10333 | 101 s / 27557 |
| 4 | 160 s / 21442 | 49 s / 9968 | 83 s / 23375 |
| 5 | 209 s / 26857 | 53 s / 10632 | 84 s / 23599 |
| 6 | 186 s / 25145 | 56 s / 10445 | 85 s / 23748 |
| 7 | 215 s / 28134 | 54 s / 10360 | 89 s / 24755 |
| 8 | 204 s / 28025 | 58 s / 10860 | 100 s / 27157 |
| 9 | 209 s / 28828 | 52 s / 10248 | 108 s / 29148 |
| 10 | 216 s / 29589 | 56 s / 10817 | 90 s / 25436 |

### Features added / removed per generation (EXPLORATORY: a fresh Haiku reads the diff only; counts are approximate)

| gen | opus | sonnet | haiku |
|---|---|---|---|
| 1 | +23 / -2 | +14 / -2 | +13 / -1 |
| 2 | +13 / -0 | +6 / -2 | +7 / -1 |
| 3 | +7 / -0 | +9 / -2 | +8 / -0 |
| 4 | +6 / -0 | +3 / -1 | +2 / -1 |
| 5 | +10 / -1 | +5 / -0 | +4 / -1 |
| 6 | +7 / -0 | +0 / -0 | +1 / -0 |
| 7 | +8 / -0 | +1 / -1 | +3 / -2 |
| 8 | +12 / -0 | +6 / -1 | +3 / -0 |
| 9 | +3 / -1 | +4 / -4 | +4 / -0 |
| 10 | +7 / -1 | +2 / -0 | +3 / -0 |

Totals over 10 generations: opus +96 / -5; sonnet +50 / -13; haiku +48 / -6.

### Regressions

By the protocol definition (a playtest point lost vs the previous generation): **none** in any of the 30 transitions. No crash, so the crash/rollback rule never triggered.

Jury drops of 0.5 or more between consecutive generations (not a protocol regression, reported for honesty; the jury sees frames only and has noise of about +-0.5):

- opus gen 7 to 8: 7.67 to 6.80
- sonnet gen 9 to 10: 5.90 to 5.30
- haiku gen 3 to 4: 5.87 to 5.30
- haiku gen 8 to 9: 5.67 to 4.93

Feature removals (2 or more removed in one generation, per the exploratory counter): opus gen 1 (-2), sonnet gen 1 (-2), sonnet gen 2 (-2), sonnet gen 3 (-2), sonnet gen 9 (-4), haiku gen 7 (-2).

### Headline numbers

- Jury, gen 0 to gen 10: opus 5.13 to 7.80 (+2.67); sonnet 4.13 to 5.30 (+1.17); haiku 4.80 to 5.87 (+1.07).
- Opus gen 10 is the best-judged game of the whole experiment (7.80); opus was above 7 from gen 2 on except gen 3 (6.93) and gen 8 (6.80).
- Code size gen 0 to 10: opus 15,160 to 46,710 bytes (x3.1, 382 to 1,039 lines); sonnet 9,874 to 18,300 (x1.9, 250 to 410); haiku 18,850 to 36,285 (x1.9, 617 to 1,029). Haiku and opus end with almost the same line count; sonnet stays small.
- Haiku gets the largest code with the smallest judged gain: the small model wrote more but did not make it look better. Sonnet rose slowly and noisily (peak 5.90 at gen 9).
- Features in gen 1 alone: opus +23, sonnet +14, haiku +13, then it falls for sonnet (2-6 per generation after gen 4, gen 6 added 0) and haiku (1-4 after gen 4), while opus keeps adding 3 to 12 features per generation up to gen 10.
- Bytes per jury point is far worse for haiku than for opus.

## Three possible titles (chosen from the data)

1. "I let 3 AIs improve their own game 10 times. Only one clearly got better." (opus +2.7 jury points; sonnet +1.2; haiku +1.1; the playtest was 8/8 for all 33 versions, so the jury and the code size carry it).
2. "The biggest AI broke its game on try 1. Then it won." (opus_1 did not load, jury 1.07 out of 10; opus ends with the best game, 7.80).
3. "Its game tripled in size. Haiku's didn't get better." or shorter: "More code is not a better game." (haiku 617 to 1,029 lines for +1.1 points; opus 382 to 1,039 lines for +2.7).

Caveats to keep in the film: jury noise is large. The same game scored differently in the two jury runs (gen 0 vs its Round 1 twin: opus 5.13 vs 6.40, haiku 4.80 vs 5.53, sonnet 4.13 vs 4.80), so differences under about 1.3 points are not reliable; only the opus climb (+2.7) clearly exceeds it, sonnet and haiku gains (+1.2, +1.1) are within noise. jurors are Claude too (same-family bias) and see frames only; n=3 in Round 1, one lineage per model in Round 2; our creator playing is the final judge (page jouer/).

## Five most visual moments for the film

1. Opus_1 (Round 1): the title screen of the game that never starts, side by side with opus_2 beside it: same model, same brief, 1.07 vs 6.40. Source: jeux/r1_opus_1/test/menu.png and play.webm.
2. Opus gen 0 vs gen 10, same frame (jeux/r2_opus_g00/test/f04.png vs r2_opus_g10/test/f04.png): a plain dark field with cyan dots becomes a layered HUD with a dash bar, combo meter, level banner, floating +10 popups, glowing orbs of several colours and particle trails.
3. Opus gen 1, the big jump: +23 features in a single generation (shield power-up, hazard warnings, expiring orbs, hitstop, score popups). Compare g00 and g01 playtest videos (play.webm).
4. The three lineages at gen 10, side by side in the same 60 s bot run: opus (1,039 lines, busy), haiku (1,029 lines, busy but flatter), sonnet (410 lines, restrained). Videos in jeux/r2_*_g10/test/play.webm.
5. The code-size race: a bar chart growing generation by generation (opus x3.1, haiku x1.9, sonnet x1.9) with the jury score as a line, showing the sonnet and haiku curves staying flat while opus climbs. Data in the tables above.

## Deviations (see PREREGISTRATION.md)

- 2026-11-22: network outage, driver retry lengthened.
- 2026-11-25: Round 2 first attempt (22-23/11) failed at generation 01 for all models because of the network (api_error, 0 tokens): infrastructure, not model crashes; not counted. Round 2 resumed from gen00 with unchanged prompts. The network did not fail again during the resume (0 retries).
- Also on 2026-11-25 (not in the protocol file, noted here): the Round 1 jury files had no recorded responses (only prompts), so the Round 1 jury was (re)run with jury.py with the same ids, sheets and rubric. The Round 2 jury includes gen 0 of each model as a separate blind game (33 games). Some games were scored by 2 jurors instead of 3 because a juror skipped them in its answer. The exploratory feature counter is features.py (logs/feat_*).
- Cost note: `claude -p` JSON reports a notional total_cost_usd; no API key or other vendor was used.
