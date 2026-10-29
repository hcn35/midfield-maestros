import json
from pathlib import Path

import matplotlib.image as mpimg
import pytest
from matplotlib.quiver import Quiver

from maestros import charts
from maestros.data import matches_path
from maestros.settings import Settings

FIXTURE = Path(__file__).parent / "fixtures" / "xavi_events.jsonl"
EVENTS = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
PLAYER = 20131
MATCH = {
    "match_id": 69222,
    "match_date": "2009-04-11",
    "home_team": {"home_team_name": "Barcelona"},
    "away_team": {"away_team_name": "Recreativo Huelva"},
}


def _fixture_split():
    passes = [e for e in EVENTS if e["type"]["name"] == "Pass" and e["player"]["id"] == PLAYER]
    done = [p for p in passes if "outcome" not in p["pass"]]
    return len(passes), len(done), len(passes) - len(done)


def _arrows(fig):
    ax = fig.axes[0]
    return {q.get_label(): q.N for q in ax.collections if isinstance(q, Quiver)}


def test_one_arrow_per_pass_split_by_outcome():
    total, done, missed = _fixture_split()
    assert (total, done, missed) == (36, 31, 5)
    fig = charts.pass_map(EVENTS, PLAYER, MATCH)
    assert _arrows(fig) == {f"Completed ({done})": done, f"Incomplete ({missed})": missed}


def test_completed_and_incomplete_use_different_colours_with_legend():
    fig = charts.pass_map(EVENTS, PLAYER, MATCH)
    quivers = [q for q in fig.axes[0].collections if isinstance(q, Quiver)]
    colours = {tuple(q.get_facecolor()[0]) for q in quivers}
    assert len(colours) == 2
    legend = fig.axes[0].get_legend()
    assert [t.get_text() for t in legend.get_texts()] == ["Completed (31)", "Incomplete (5)"]


def test_arrows_go_from_start_to_end_location():
    fig = charts.pass_map(EVENTS, PLAYER, MATCH)
    quiver = next(q for q in fig.axes[0].collections if q.get_label().startswith("Completed"))
    first = next(e for e in EVENTS if e["type"]["name"] == "Pass" and "outcome" not in e["pass"])
    (sx, sy), (ex, ey) = first["location"], first["pass"]["end_location"]
    # vertical pitch: StatsBomb x runs up the page, y across it
    assert (quiver.X[0], quiver.Y[0]) == pytest.approx((sy, sx))
    assert (quiver.U[0], quiver.V[0]) == pytest.approx((ey - sy, ex - sx))


def test_title_names_player_both_teams_and_date():
    title = charts.pass_map(EVENTS, PLAYER, MATCH)._suptitle.get_text()
    for part in ("Xavier Hernández Creus", "Barcelona", "Recreativo Huelva", "2009-04-11"):
        assert part in title


def test_other_players_passes_are_left_out():
    other = dict(EVENTS[1], player={"id": 1, "name": "Someone"})
    fig = charts.pass_map(EVENTS + [other], PLAYER, MATCH)
    assert sum(_arrows(fig).values()) == 36


def test_png_is_portrait_and_at_least_1080_wide(tmp_path):
    out = tmp_path / "pass_map.png"
    charts.save(charts.pass_map(EVENTS, PLAYER, MATCH), out)
    height, width = mpimg.imread(out).shape[:2]
    assert width >= 1080
    assert height > width


def test_main_reads_player_and_match_from_settings(tmp_path, monkeypatch):
    settings = Settings(
        player_id=PLAYER, team="Barcelona", competition_id=11, season_id=41,
        charts=["pass_map"], match_id=69222,
    )
    cache = tmp_path / "cache"
    (cache / "events").mkdir(parents=True)
    (cache / "events" / "69222.json").write_text(json.dumps(EVENTS))
    other_match = dict(MATCH, match_id=1, match_date="2008-08-31")
    matches_path(settings, cache).parent.mkdir(parents=True)
    matches_path(settings, cache).write_text(json.dumps([other_match, MATCH]))
    seen = {}
    monkeypatch.setattr(charts, "pass_map", lambda e, p, m: seen.update(n=len(e), p=p, m=m) or "fig")
    monkeypatch.setattr(charts, "save", lambda fig, path: seen.update(path=path))
    written = charts.build(settings, cache_dir=cache, out_dir=tmp_path / "out")
    assert written == [tmp_path / "out" / "pass_map.png"]
    assert seen == {"n": 102, "p": PLAYER, "m": MATCH, "path": tmp_path / "out" / "pass_map.png"}


def test_unknown_chart_name_fails_loudly(tmp_path):
    settings = Settings(
        player_id=PLAYER, team="Barcelona", competition_id=11, season_id=41,
        charts=["heat_map"], match_id=69222,
    )
    with pytest.raises(SystemExit, match="heat_map"):
        charts.build(settings, cache_dir=tmp_path, out_dir=tmp_path)


def test_out_dir_is_gitignored():
    gitignore = (Path(__file__).resolve().parent.parent / ".gitignore").read_text().splitlines()
    assert "out/" in gitignore
