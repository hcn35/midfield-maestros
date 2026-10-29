# QA v3 · issue #1 · head `f1bd6f2`

Verdict: ✅ pass. All 5 ACs pass after the R1 fix (match list keyed by competition, season and team). Fresh clone of the branch, real StatsBomb download.

| AC | Result | Proof |
|---|---|---|
| 1 settings.yaml, nothing hard-coded | ✅ | `tests/test_settings.py` · `checks.log`: no ids or names in `maestros/*.py` · cache key read from settings (`maestros/data.py` `matches_path`) |
| 2 download 31 matches, gitignored, 2nd run downloads 0 | ✅ | `download.log`: run 1 downloaded 31, run 2 downloaded 0, list at `matches/11-41-barcelona.json`, 31 event files, clone clean |
| 3 Xavi fixture < 200 lines, pytest offline | ✅ | 102 lines · `pytest-offline.log`: 10 passed with sockets blocked |
| 4 README under 15 lines | ✅ | `checks.log`: 14 lines · `tests/test_readme.py` guards it |
| 5 fresh clone venv + install + pytest | ✅ | `pytest-fresh-clone.log`: python3.11 venv, `pip install -e '.[dev]'`, 10 passed at `f1bd6f2` |

## R1 re-check

- `test_changed_season_fetches_its_own_match_list` and `test_changed_team_fetches_its_own_match_list` pass; real download writes `data/cache/matches/11-41-barcelona.json`.

## Test gaps (not written)

- Low · stale `events/<id>.part` from a killed run is left behind; the next run overwrites it.
- Low · a team name with no matches caches an empty list for that key; fixing the name changes the key, so no stale reuse.
- Low · `.gitignore` coverage of `data/cache/` has no automated check (verified by hand in `download.log`).
