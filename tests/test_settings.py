from pathlib import Path

from maestros.settings import DEFAULT_PATH, load_settings


def test_repo_settings_file_holds_xavi_and_2008_09():
    s = load_settings(DEFAULT_PATH)
    assert s.player_id == 20131
    assert s.team == "Barcelona"
    assert s.competition_id == 11
    assert s.season_id == 41
    assert s.match_id == 69222
    assert s.charts == ["pass_map"]


def test_values_come_from_the_file(tmp_path: Path):
    path = tmp_path / "settings.yaml"
    path.write_text(
        "player_id: 5503\nteam: Real Madrid\ncompetition_id: 2\nseason_id: 27\nmatch_id: 7\ncharts: [pass_map]\n"
    )
    s = load_settings(path)
    assert (s.player_id, s.team, s.competition_id, s.season_id, s.match_id, s.charts) == (
        5503,
        "Real Madrid",
        2,
        27,
        7,
        ["pass_map"],
    )
