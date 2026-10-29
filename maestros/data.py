"""Download StatsBomb open data once and read it back from the local cache.

Cache layout (gitignored):
    data/cache/matches.json          the team's matches for the season
    data/cache/events/<match_id>.json  every event of one match
"""

import argparse
import json
from pathlib import Path

from maestros.settings import ROOT, Settings, load_settings

CACHE_DIR = ROOT / "data" / "cache"


def _team_matches(settings: Settings, client) -> list[dict]:
    matches = client.matches(
        competition_id=settings.competition_id, season_id=settings.season_id, fmt="dict"
    )
    return sorted(
        (
            m
            for m in matches.values()
            if settings.team
            in (m["home_team"]["home_team_name"], m["away_team"]["away_team_name"])
        ),
        key=lambda m: m["match_id"],
    )


def _statsbomb():
    from statsbombpy import sb  # imported late so offline checks never touch it

    return sb


def download(settings: Settings, cache_dir: Path = CACHE_DIR, client=None) -> list[int]:
    """Save every team match and its events. Skip what is already cached.

    Returns the match ids downloaded on this run.
    """
    cache_dir = Path(cache_dir)
    matches_file = cache_dir / "matches.json"
    events_dir = cache_dir / "events"

    if matches_file.exists():
        matches = json.loads(matches_file.read_text())
    else:
        client = client or _statsbomb()
        matches = _team_matches(settings, client)
        cache_dir.mkdir(parents=True, exist_ok=True)
        matches_file.write_text(json.dumps(matches))

    events_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for match in matches:
        match_id = match["match_id"]
        target = events_dir / f"{match_id}.json"
        if target.exists():
            continue
        client = client or _statsbomb()
        events = client.events(match_id=match_id, fmt="dict")
        tmp = target.with_suffix(".part")
        tmp.write_text(json.dumps(list(events.values())))
        tmp.rename(target)
        downloaded.append(match_id)
    return downloaded


def load_events(match_id: int, cache_dir: Path = CACHE_DIR) -> list[dict]:
    return json.loads((Path(cache_dir) / "events" / f"{match_id}.json").read_text())


def player_events(events: list[dict], player_id: int) -> list[dict]:
    return [e for e in events if e.get("player", {}).get("id") == player_id]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m maestros.data")
    parser.add_argument("--download", action="store_true", help="fetch matches into data/cache/")
    args = parser.parse_args(argv)
    if not args.download:
        parser.print_help()
        return
    settings = load_settings()
    new = download(settings)
    total = len(json.loads((CACHE_DIR / "matches.json").read_text()))
    print(f"{total} {settings.team} matches cached in {CACHE_DIR}; downloaded {len(new)} this run")


if __name__ == "__main__":
    main()
