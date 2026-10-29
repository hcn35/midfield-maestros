import json
from pathlib import Path

from maestros.data import download, load_events, player_events
from maestros.settings import Settings

FIXTURE = Path(__file__).parent / "fixtures" / "xavi_events.jsonl"

SETTINGS = Settings(player_id=20131, team="Barcelona", competition_id=11, season_id=41, charts=[])


def _match(match_id, home, away):
    return {
        "match_id": match_id,
        "home_team": {"home_team_name": home},
        "away_team": {"away_team_name": away},
    }


class FakeClient:
    """Stands in for statsbombpy: no network in tests."""

    def __init__(self):
        self.match_calls = []
        self.event_calls = []

    def matches(self, competition_id, season_id, fmt):
        self.match_calls.append((competition_id, season_id))
        return {
            1: _match(1, "Barcelona", "Sevilla"),
            2: _match(2, "Valencia", "Barcelona"),
            3: _match(3, "Getafe", "Sevilla"),
        }

    def events(self, match_id, fmt):
        self.event_calls.append(match_id)
        return {f"e{match_id}": {"id": f"e{match_id}", "player": {"id": 20131}}}


def test_download_saves_only_team_matches(tmp_path):
    client = FakeClient()
    saved = download(SETTINGS, tmp_path, client)
    assert sorted(saved) == [1, 2]
    assert client.event_calls == [1, 2]
    assert sorted(p.name for p in (tmp_path / "events").iterdir()) == ["1.json", "2.json"]
    assert sorted(m["match_id"] for m in json.loads((tmp_path / "matches.json").read_text())) == [1, 2]
    assert load_events(1, tmp_path) == [{"id": "e1", "player": {"id": 20131}}]


def test_second_run_downloads_nothing(tmp_path):
    download(SETTINGS, tmp_path, FakeClient())
    client = FakeClient()
    assert download(SETTINGS, tmp_path, client) == []
    assert client.match_calls == []
    assert client.event_calls == []


def test_fixture_is_one_player_one_match_under_200_lines():
    lines = FIXTURE.read_text().splitlines()
    assert 0 < len(lines) < 200
    events = [json.loads(line) for line in lines]
    assert {e["player"]["id"] for e in events} == {20131}
    assert len({e["match_id"] for e in events}) == 1


def test_player_events_filters_by_settings_player():
    events = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
    other = {"id": "x", "player": {"id": 1}}
    no_player = {"id": "y"}
    assert player_events(events + [other, no_player], SETTINGS.player_id) == events


def test_interrupted_download_resumes_missing_matches_only(tmp_path):
    download(SETTINGS, tmp_path, FakeClient())
    (tmp_path / "events" / "2.json").unlink()
    client = FakeClient()
    assert download(SETTINGS, tmp_path, client) == [2]
    assert client.match_calls == []
    assert client.event_calls == [2]
