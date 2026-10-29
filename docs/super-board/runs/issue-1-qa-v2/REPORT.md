# QA v2 · issue #1 · head `c377655`

Verdict: ✅ pass. All 5 ACs pass. Fresh clone of the branch, real StatsBomb download.

| AC | Result | Proof |
|---|---|---|
| 1 settings.yaml, nothing hard-coded | ✅ | `tests/test_settings.py:6`, `:15` · `hardcode-grep.log`: no ids or names in `maestros/*.py` |
| 2 download 31 matches, gitignored, 2nd run downloads 0 | ✅ | `download.log`: run 1 downloaded 31, run 2 downloaded 0, 31 event files, `.gitignore:15`, clone clean |
| 3 Xavi fixture < 200 lines, pytest offline | ✅ | 102 lines, ids equal Xavi's events in real match 69222 · `pytest-offline.log`: 8 passed with sockets blocked |
| 4 README under 15 lines | ✅ | `readme.log`: 14 lines · `tests/test_readme.py:6` guards it |
| 5 fresh clone venv + install + pytest | ✅ | `pytest-fresh-clone.log`: python3.11 venv, `pip install -e '.[dev]'`, 7 passed at `c377655` |

## Test added

- `tests/test_data.py` `test_interrupted_download_resumes_missing_matches_only`: v1 Medium gap, now covered.

## Test gaps (not written)

- Low · stale `events/<id>.part` from a killed run is left behind; the next run overwrites it.
- Low · `.gitignore` coverage of `data/cache/` has no automated check (verified by hand in `download.log`).
