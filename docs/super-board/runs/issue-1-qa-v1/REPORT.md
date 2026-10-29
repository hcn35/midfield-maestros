# QA v1 · issue #1 · head `1e481f5`

Verdict: ❌ fail (AC4 only). AC1, AC2, AC3, AC5 pass.

| AC | Result | Proof |
|---|---|---|
| 1 settings.yaml, nothing hard-coded | ✅ | `tests/test_settings.py:6`, `:15` · `grep -nE "20131\|Barcelona\|Xavi\|\b11\b\|\b41\b" maestros/*.py` finds nothing |
| 2 download 31 matches, gitignored, 2nd run downloads 0 | ✅ | `download.log`: run 1 downloaded 31, run 2 downloaded 0, 31 event files, `data/cache/` ignored by `.gitignore:15`, worktree clean · `tests/test_data.py:40`, `:50` |
| 3 Xavi fixture < 200 lines, pytest offline | ✅ | 102 lines, all 102 event ids match `player_events(load_events(69222), 20131)` from the real download · `pytest-offline.log`: 6 passed with sockets blocked |
| 4 README under 15 lines | ❌ | `readme.log`: `wc -l README.md` = 15 (want < 15; builder reported 13). Fixed looks like: 14 lines or fewer, e.g. drop one blank line |
| 5 fresh clone venv + install + pytest | ✅ | fresh `git clone` of the branch at `1e481f5`, `python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]' && .venv/bin/pytest`: 6 passed |

## Test gaps (not written)

- Medium · resume after an interrupted download: `matches.json` present, one `events/<id>.json` missing. Witness: delete `events/2.json` after a full fake run; expect `download()` returns `[2]` and calls `events` once. Target `tests/test_data.py`.
- Low · stale `events/<id>.part` from a killed run is left behind; harmless, the next run overwrites it.
- Low · `.gitignore` coverage of `data/cache/` has no automated check (verified by hand above).
